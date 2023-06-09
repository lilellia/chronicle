from argparse import ArgumentParser
from pathlib import Path

from chronicle.crawler import get_all_post_ids


def main():
    parser = ArgumentParser()
    parser.add_argument("subreddit", help="the subreddit to get post IDs from")
    parser.add_argument("-o", "--outfile", required=True, type=Path, help="the file to output IDs to")
    args = parser.parse_args()

    with open(args.outfile, "w+", encoding="utf-8") as f:
        for rank, id_ in get_all_post_ids(args.subreddit):
            f.write(f"{rank} -> {id_}")


if __name__ == "__main__":
    main()
