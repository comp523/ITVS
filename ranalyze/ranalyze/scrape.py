"""
Tool to traverse a set of subreddits extracting post/comment information including:
 - Post title
 - Post date
 - Post URL (if not a self post)
 - Number of upvotes/downvotes
"""

from itertools import chain
from typing import (
    Callable,
    Iterable
)

import praw

from .database import Database
from .common_types import DateRange
from .config import (
    Config,
    DictConfigModule,
    YAMLSource
)
from .entry import (
    Comment,
    CommentFactory,
    Entry,
    PostFactory
)
from .progress import Progress


class ScrapeConfigModule(DictConfigModule):

    _arguments_dict = {
        "subreddit selection": {
            ("-s", "--subreddit"): {
                "action": "append",
                "dest": "subreddits",
                "help": ("subreddit to analyze, may be a single value, "
                         "or a space-delimited list"),
                "nargs": "+",
                "type": str
            }
        },
        "database": {
            ("-d", "--database-file"): {
                "help": ("analysis data will be written "
                         "to this SQLite file"),
                "type": str
            }
        },
        "configuration": {
            ("-c", "--config-file"): {
                "help": "load configuration from file",
                "type": str
            }
        }
    }

    def get_runner(self) -> Callable:

        return main

def traverse_comments(top_level_comments: Iterable[praw.objects.Comment]) -> Iterable[Comment]:
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

def fetch_data(subreddit_set: set, database: Database) -> Iterable[Entry]:
    """
    Fetch all posts and associated comments from a given subreddit set, after
    the given entry id. Yields both Post and Comment instances.
    """

    Progress.format = ("Scraped {posts} posts and {comments} comments from "
                       "{subreddit}")

    # api wrapper connection
    reddit = praw.Reddit(user_agent="Documenting ecig subs")

    # for use in progress logging
    first_pass = True 

    for subreddit_name in subreddit_set:

        subreddit = reddit.get_subreddit(subreddit_name)

        if first_pass:
            first_pass = False
        else:
            Progress.freeze()

        # progress logging
        post_count = 0
        comment_count = 0

        Progress.update(posts=post_count,
                        comments=comment_count,
                        subreddit=subreddit_name)

        before = database.get_latest_post(subreddit_name)

        params = {"before": before.id} if before is not None else {}

        for post in subreddit.get_new(limit=None, params=params):

            post.replace_more_comments(limit=None, threshold=0)

            yield(PostFactory.from_praw(post)) # first yields the post itself

            post_count += 1
            Progress.update(posts=post_count)

            post.replace_more_comments(limit=None)

            for comment in traverse_comments(post.comments):
                yield(comment) # yields all post comments

                comment_count += 1
                Progress.update(comments=comment_count)

def fetch_post(permalink: str) -> Iterable[Entry]:
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

def update_posts(database: Database, date_range: DateRange):
    """
    Updates all posts in the database in a specified range
    """
    posts = filter(lambda entry: entry is Post, # only posts
        database.get_entries(time_submitted_range = date_range))
    for post in posts:
        for entry in fetch_post(post.permalink):
            database.add_update_entry(entry)

def main():
    """
    Parse CLI arguments, fetch data from requested subreddits, and generate
    Excel workbook.
    """

    config = Config.get_instance()

    if config["config_file"] is not None:
        config.add_source(YAMLSource(config["config_file"]))

    subreddits = chain(*config["subreddits"])

    database = Database(config["database_file"])

    for post in fetch_data(subreddits, database):
        database.add_update_entry(post)
