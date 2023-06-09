from enum import Enum, auto
from itertools import count
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import sys
from time import sleep
from typing import Iterator, NamedTuple

from chronicle.utils import function_compose


DIV_ID_PREFIX = len("t3_")


class PostType(Enum):
    SUBMISSION = auto()
    ADVERT = auto()


class PostParseResult(NamedTuple):
    post_type: PostType
    id: str
    index: int | None = None


def sanitise_id(div_id: str) -> str:
    """
    Convert the ID of the post's div element to the post's actual ID.

    :param str div_id: the HTML ID of the div element pointing to the post
    :return: the post ID
    :rtype: str
    """
    return div_id[DIV_ID_PREFIX:]


def get_max_scroll(driver: webdriver.Firefox) -> int:
    """
    Return the current maximum scroll height. For a dynamic page like a subreddit, this changes as you scroll.
    """
    result = driver.execute_script("return document.body.scrollHeight;")
    return int(result)


def find_by_text(driver: webdriver.Firefox, tag: str, text: str) -> WebElement:
    """
    Find an element on the page by its HTML tag and text content.
    """
    xpath = f"// {tag}[contains(text(), {text!r})]"
    return driver.find_element(By.XPATH, xpath)


def get_parent(element: WebElement) -> WebElement:
    return element.parent.execute_script("return arguments[0].parentElement;", element)


def get_sibling(element: WebElement) -> WebElement:
    return element.parent.execute_script("return arguments[0].nextElementSibling;", element)


def change_to_compact_view(driver: webdriver.Firefox) -> None:
    """
    Change Reddit's display mode to compact.
    """
    driver.find_element(By.ID, "LayoutSwitch--picker").click()
    find_by_text(driver, "span", "compact").click()


def advance(element: WebElement, target_parent: WebElement) -> WebElement:
    """
    Advance the current search to the next node of interest, looking up `generations` generations to find the ancestor-sibling.
    """
    while get_parent(element) != target_parent:
        element = get_parent(element)

    return get_sibling(element).find_element(By.CLASS_NAME, "Post")


def scroll_to_coords(driver: webdriver.Firefox, x: int = 0, y: int = 0, *, delay: float = 0) -> None:
    """
    Scroll the webpage to the given coordinates.
    """
    if delay:
        sleep(delay)
    driver.execute_script(f"window.scroll({{top: {y}, left: {x}, behavior: 'smooth'}})")


def scroll_to_element(element: WebElement, *, delay: float = 0) -> None:
    """
    Scroll the webpage to the given element.
    """
    x, y = element.location["x"], element.location["y"]
    scroll_to_coords(element.parent, x, y, delay=delay)


def handle_post(post: WebElement, counter: Iterator[int]) -> PostParseResult:
    id_ = sanitise_id(post.get_attribute("id") or "")

    if "promotedlink" in (post.get_attribute("class") or ""):
        return PostParseResult(PostType.ADVERT, id=id_, index=None)

    return PostParseResult(PostType.SUBMISSION, id=id_, index=next(counter))


def get_all_post_ids(subreddit: str) -> Iterator[tuple[int, str]]:
    """
    Return an iterator over all the post IDs for the given subreddit.
    """
    options = webdriver.FirefoxOptions()
    options.set_preference("dom.push.enabled", False)
    # options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)

    driver.get(f"https://www.reddit.com/r/{subreddit}/new/")
    logger.info("subreddit page loaded")

    change_to_compact_view(driver)
    logger.debug("compact view enabled")

    # find first post
    node = driver.find_element(By.CLASS_NAME, "Post")
    ANCESTOR = function_compose(get_parent, node, n=3)  # "level" ground in the div forest
    logger.debug(f"{ANCESTOR=}")
    counter = count(1)

    while True:
        result = handle_post(node, counter)

        if result.post_type == PostType.ADVERT:
            logger.debug(f"found advert: ...{result.id[-10:]}")
        elif result.post_type == PostType.SUBMISSION:
            assert result.index is not None, "result.index should not be None: actual submission"
            logger.info(f"{result.index:09,} -> {result.id}")
            yield result.index, result.id
        else:
            logger.error(f"invalid post_type for {result.id}: {result.post_type!r}")
            sys.exit(1)

        while True:
            scroll_to_element(node, delay=0.15)
            try:
                node = advance(node, target_parent=ANCESTOR)
            except AttributeError:
                logger.debug(f"cannot advance: {node=} {result=}")
                sleep(0.75)
            else:
                break
