"""
Tool to traverse a set of subreddits extracting post/comment information including:
 - Post title
 - Post date
 - Post URL (if not a self post)
 - Number of upvotes/downvotes
"""

import praw

from datetime import datetime
from .constants import ENTRY_TABLE, SUBREDDIT_TABLE
from .database import (
    add_update_object,
    connect,
    execute_query,
    get_latest_post
)
from .frequency import digest_entry
from .models import (
    CommentFactory,
    Post,
    PostFactory
)
from .query import Condition, SelectQuery, UpdateQuery
from .utils import date_to_timestamp


def traverse_comments(top_level_comments):
    """
    Iterate through all comments, extracting desired properties.
    :yield: each subsequent comment
    """
    comment_stack = [comment for comment in top_level_comments]
    # In order traversal of the comment tree
    while len(comment_stack) > 0:
        # most expand the most recently added comment
        next_comment = comment_stack.pop()
        # place all replies in the comment stack to also
        # be expanded
        comment_stack.extend(next_comment.replies)
        yield(CommentFactory.from_praw(next_comment))


def fetch_data(subreddit_set):
    """
    Fetch all posts and associated comments from a given subreddit set, after
    the given Entry id. Yields both Post and Comment instances.
    """

    # api wrapper connection
    reddit = praw.Reddit(user_agent="Documenting ecig subs")

    for subreddit_name in subreddit_set:

        condition = Condition("name", subreddit_name)

        query = UpdateQuery(table=SUBREDDIT_TABLE,
                            values={"scraping": 1},
                            where=condition)

        execute_query(query, commit=True)

        subreddit = reddit.get_subreddit(subreddit_name)

        before = get_latest_post(subreddit_name)

        params = {"before": before.id} if before is not None else {}

        for post in subreddit.get_new(limit=None, params=params):

            post.replace_more_comments(limit=None, threshold=0)

            yield(PostFactory.from_praw(post)) # first yields the post itself

            post.replace_more_comments(limit=None)

            for comment in traverse_comments(post.comments):
                yield(comment)  # yields all post comments

        timestamp = date_to_timestamp(datetime.now())

        query = UpdateQuery(table=SUBREDDIT_TABLE,
                            values={
                                "scraping": 0,
                                "last_scraped": timestamp
                            },
                            where=condition)

        execute_query(query, commit=True)


def fetch_post(permalink):
    """
    Fetches posts by permalink
    Yields both post and child comment instances
    For use in updating and importing from csv
    """
    # api wrapper connection
    reddit = praw.Reddit(user_agent="Documenting ecig subs")
    post = reddit.get_submission(permalink)
    yield(PostFactory.from_praw(post))
    for comment in traverse_comments(post.comments):
        yield(comment)


def update_posts(date_range):
    """
    Updates all posts in the database in a specified range
    """

    condition = (Condition("time_submitted", ">=", date_range[0]) &
                 Condition("time_submitted", "<=", date_range[1]))

    query = SelectQuery(table=ENTRY_TABLE,
                        where=condition)

    posts = filter(lambda entry: isinstance(entry, Post), execute_query(query))

    for post in posts:
        for entry in fetch_post(post.permalink):
            add_update_object(entry)


def get_subreddits():
    query = SelectQuery(table=SUBREDDIT_TABLE)
    return execute_query(query, transpose=False)


def scrape(subreddits):
    """
    Parse CLI arguments, fetch data from requested subreddits, and generate
    Excel workbook.
    """

    if type(subreddits) is str:
        subreddits = [subreddits]

    for entry in fetch_data(subreddits):
        digest_entry(entry)
        add_update_object(entry, ENTRY_TABLE)
