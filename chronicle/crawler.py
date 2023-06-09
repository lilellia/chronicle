from itertools import count
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import Iterator


POSTS_PER_PAGE = 50
DIV_ID_PREFIX = len("thing_t3_")


def sanitise_id(div_id: str) -> str:
    """
    Convert the ID of the post's div element to the post's actual ID.

    :param str div_id: the HTML ID of the div element pointing to the post
    :return: the post ID
    :rtype: str
    """
    return div_id[DIV_ID_PREFIX:]


def get_all_post_ids(subreddit: str) -> Iterator[tuple[int, str]]:
    """
    Return an iterator over all the post IDs for the given subreddit.
    """
    options = webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)

    driver.get(f"https://old.reddit.com/r/{subreddit}/new/")
    for page in count(1):
        logger.info(f"Processing page {page}")

        # Find all posts on the given page
        for element in driver.find_elements(By.CSS_SELECTOR, "[data-rank]"):
            if element.get_attribute("data-rank") == "":
                # adverts have a blank data-rank property
                continue

            rank = int(element.get_attribute("data-rank"))  # type: ignore
            id_ = sanitise_id(element.get_attribute("id"))  # type: ignore

            logger.debug(f"{rank:06} -> {id_}")
            yield rank, id_

        # Find the "next" button and click it
        try:
            (
                driver
                .find_element(By.CLASS_NAME, "next-button")
                .find_element(By.TAG_NAME, "a")
                .click()
            )
        except Exception as e:
            logger.error(driver.current_url)
            logger.error(e)
            return
