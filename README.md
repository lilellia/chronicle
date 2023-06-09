# chronicle

`chronicle`—also known as *Operation Chronicle*—is a set of scripts designed to assist in scraping and archiving posts from a given subreddit.

## Installation

After cloning this repository, simply run

```bash
python3 -m pip install -r requirements.txt
```

You will also need to install the [Firefox webdriver](https://github.com/mozilla/geckodriver/releases/) and ensure that it is on the system PATH. (Required for `selenium`.)

## Usage

This package comes with two runnable scripts:

### `get_ids.py`

This should be run as

```console
$ python3 get_ids.py SUBREDDIT_NAME -o OUTFILE
```

where `SUBREDDIT_NAME` is the name of the subreddit (without "r/") and `OUTFILE` is the file where the post IDs will be saved.

As an example, to get post IDs from r/test:

```console
$ python3 get_ids.py test -o ids.txt
```

### `scrape_posts.py`

This should be run as

```console
$ python3 scrape_posts.py IDFILE [-r/--root ROOT] [-e/--env ENV] [-c/--comments]
```

where
- `IDFILE` is the file containing the post IDs,
- `ROOT` is the root directory where the post data will be exported (defaults to `./data`),
- `ENV` is the path to a `.env` file containing Reddit API credentials (defaults to `./.env`),
- `-c/--comments` can be passed to have comment data also saved to file (default is to skip comment data)