from argparse import ArgumentParser
from functools import partial
import json
from loguru import logger
from multiprocessing import Pool
from pathlib import Path
from praw import Reddit
import re
from time import perf_counter
from typing import Any, Iterator

from chronicle.configuration import Config
from chronicle.parser import get_api, submission_asdict
from chronicle.utils import datafile_exists


HERE = Path(__file__).parent


def load_ids(idfile: Path) -> Iterator[str]:
    """
    Return an iterator over all post IDs in the given file.
    """
    with open(idfile, "r", encoding="utf-8") as f:
        for line in f:
            if not (match := re.search(r"-> (.*)$", line.strip())):
                continue
            yield match.group(1)


def get_export_dest(data: dict[str, Any], export_root: Path) -> Path:
    """
    Determine the path to the export file based on the submission data.
    """
    id_ = data["id"]
    directory = export_root / data.get("flair", "_other")
    directory.mkdir(exist_ok=True)
    return directory / f"data_{id_}.json"


def export(id: str, api: Reddit, export_root: Path, preserve_comments: bool = False) -> None:
    """
    Export the submission corresponding to the given ID.
    """
    if datafile_exists(id, export_root):
        logger.info(f"datafile for {id=} already exists")
        return

    start = perf_counter()
    submission = api.submission(id=id)
    try:
        data = submission_asdict(submission, preserve_comments=preserve_comments)
    except Exception as e:
        logger.error(f"Error occurred while exporting {id=}: {e}")
        return

    dest = get_export_dest(data, export_root)
    with open(dest, "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    duration = perf_counter() - start
    logger.info(f"exported {id=} ({duration:.2f}s)")


def main():
    parser = ArgumentParser()
    parser.add_argument("idfile", type=Path, help="the file holding all post IDs")
    parser.add_argument("-r", "--root", type=Path, default=HERE/"data", help="the root directory for exports")
    parser.add_argument("-e", "--env", type=Path, default=HERE/".env", help="the path to the .env file containing Reddit API credentials")
    parser.add_argument("-c", "--comments", action="store_true", help="also preserve comment data (will take longer and take more space)")
    args = parser.parse_args()

    config = Config.from_dotenv(args.env)
    api = get_api(**config.asdict())

    ids = list(load_ids(args.idfile))
    f = partial(export, api=api, export_root=args.root, preserve_comments=args.comments)
    with Pool() as pool:
        pool.map(f, ids)


if __name__ == "__main__":
    main()
