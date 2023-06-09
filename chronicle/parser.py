from praw import Reddit
from praw.models import Comment, Redditor, Submission
from typing import Any


def get_api(**kwargs) -> Reddit:
    """
    Construct a Reddit instance using the given parameters.
    """
    return Reddit(**kwargs)


def safe_author(author: Redditor | None) -> str:
    """
    Provide a failsafe to getting author name for deleted accounts.
    """
    return "[deleted]" if author is None else author.name


def submission_asdict(submission: Submission, *, preserve_comments: bool = False) -> dict[str, Any]:
    """
    Convert a submission object to a serialised JSON object.

    :param Submission submission: The submission object that we wish to export.
    :param bool preserve_comments: Whether comment data should also be fetched and preserved (default: False)
    :return: The submission data, as a dictionary.
    :rtype: dict[str, Any]
    """
    data = {
        "author": safe_author(submission.author),
        "created_utc": submission.created_utc,
        "edited": submission.edited,
        "id": submission.id,
        "is_self": submission.is_self,
        "flair": submission.link_flair_text or "[noflair]",
        "locked": submission.locked,
        "name": submission.name,
        "comments": {
            "number": submission.num_comments,
        },
        "permalink": submission.permalink,
        "votes": {
            "score": submission.score,
            "ratio": submission.upvote_ratio
        },
        # submission.selftext == "" if it is a link post
        # whereas submission.url will be the URL the link points to
        # if it is a link post
        "content": submission.selftext or submission.url,

        "is_spoiler": submission.spoiler,
        "title": submission.title,
        "stickied": submission.stickied,
        "subreddit": submission.subreddit.name
    }

    if preserve_comments:
        data["comments"]["comments"] = [comment_asdict(c) for c in submission.comments]

    return data


def comment_asdict(comment: Comment, *, preserve_all_fields: bool = False) -> dict[str, Any]:
    """
    Recursively traverse the comment tree, converting each comment to serialised JSON.

    :param Comment comment: The comment representing the top of the forest.
    :param bool preserve_all_fields: Whether all fields should be kept, with unnecessary keys preserved.
    :return: a dictionary representation of the given comment
    :rtype: dict[str, Any]
    """
    data = {
        "author": safe_author(comment.author),
        "body": comment.body,
        "created_utc": comment.created_utc,
        "edited": comment.edited,
        "id": comment.id,
        "permalink": comment.permalink,
        "replies": [comment_asdict(reply) for reply in comment.replies],
        "votes": {
            "score": comment.score
        }
    }

    if preserve_all_fields:
        # These fields are unnecessary in this application since we have the original submission
        # data as well (meaning we have the link/parent ID, and since we have the submission author,
        # we can also determine whether this comment was posted by the same person)
        data["is_OP"] = comment.is_submitter
        data["link_id"] = comment.link_id
        data["parent_id"] = comment.parent_id

    return data
