"""
Tool to traverse a set of subreddits extracting post/comment information including:
 - Post title
 - Post date
 - Post URL (if not a self post)
 - Number of upvotes/downvotes
"""

import datetime
import praw

from .common_types import DateRange
from .config import Config
from .database import Database
from .progress import Progress
from typing import Iterable


def fetch_data(subreddit_set: set, date_range: DateRange):
    """
    Fetch all posts and associated comments from a given subreddit set, within
    the specified inclusive date range. Yields both posts and comments.
    """

    Progress.format = ("Scraped {posts} posts and {comments} comments from "
                       "{subreddit}")

    def traverse_comments(root_id: str,
                          top_level_comments: Iterable[praw.objects.Comment]):
        """
        Iterate through all comments, extracting desired properties.
        :yield: each subsequent comment
        """
        comment_stack = [comment for comment in top_level_comments]
        # In order traversal of the comment tree
        while len(comment_stack) > 0:
            # most expand the most recently added comment
            next_comment = comment_stack.pop()
            comment_dict = {
                "id": next_comment.id,
                "root_id": root_id,
                "up_votes": next_comment.ups,
                "time_submitted": next_comment.created_utc,
                "time_updated": datetime.datetime.utcnow(),
                "posted_by": str(next_comment.author),
                "text_content": next_comment.body,
                "parent_id": next_comment.parent_id,
                "gilded": next_comment.gilded
            }
            # place all replies in the comment stack to also
            # be expanded
            comment_stack.extend(next_comment.replies)
            yield(comment_dict)

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

        for post_data in subreddit.get_new(limit=None):

            post_data.replace_more_comments(limit=None, threshold=0)

            post_date = datetime.datetime.fromtimestamp(post_data.created_utc)
            if post_date.date() > date_range[1]:
                continue
            if post_date.date() < date_range[0]:
                continue

            post_dict = {
                "id": post_data.id,
                "permalink": post_data.permalink,
                "up_votes": post_data.ups,
                #  "up_ratio": post_data.up_ratio,
                "time_submitted": post_data.created_utc,
                "time_updated": datetime.datetime.utcnow(),
                "posted_by": str(post_data.author),
                "title": post_data.title,
                "subreddit": str(post_data.subreddit),
                "external_url": post_data.url,
                "text_content": post_data.selftext,
                "gilded": post_data.gilded
            }

            yield(post_dict) # first yields the post itself

            post_count += 1
            Progress.update(posts=post_count)

            post_data.replace_more_comments(limit=None)

            for comment_dict in traverse_comments(post_data.id,
                                                  post_data.comments):
                yield(comment_dict) # yields all post comments

                comment_count += 1
                Progress.update(comments=comment_count)


def main():
    """
    Parse CLI arguments, fetch data from requested subreddits, and generate
    Excel workbook.
    """

    Config.initialize()

    config = Config.get_config()

    database = Database(config["database_file"], config["debug"])

    date_range = (config["date_range"]["after"], config["date_range"]["before"])

    for post in fetch_data(config["subreddits"], date_range):
        database.add_update_entry(post)


if __name__ == "__main__":
    main()
