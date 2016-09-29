"""
Analysis tool to traverse a set of subreddits extracting post information including:
 - Post title
 - Post date
 - Post URL (if not a self post)
 - Number of upvotes/downvotes
"""

import datetime
import praw

from .config import Config
from .database import Database
from .progress import Progress

def fetch_data(subreddit_set, after, before):
    """
    :param subreddit_set: set of subreddits from which to retrieve data
    :param after: ignores posts before this datetime
    :param before: ignores posts after this datetime
    :return: yields individual reddit posts one at a time
    :rtype: collections.Iterable[dict]
    """

    progress = Progress("Scraped {posts} posts and {comments} comments from "
                        "{subreddit}")

    def traverse_comments(root_id, top_level_comments):
        """
        :param root_id: id of the parent post
        :top_level_comments: all comments that have a parent that is the 
        post

        :return: yields each comment dict
        :rtype: collections.Iterable[dict]
        """
        comment_stack = [comment for comment in top_level_comments]
        while len(comment_stack) > 0:
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
            comment_stack.extend(next_comment.replies)
            yield(comment_dict)

    reddit = praw.Reddit(user_agent="Documenting ecig subs")

    first_pass = True

    for subreddit_name in subreddit_set:

        subreddit = reddit.get_subreddit(subreddit_name)

        if first_pass:
            first_pass = False
        else:
            progress.freeze()


        post_count = 0
        comment_count = 0

        progress.update(posts=post_count,
                        comments=comment_count,
                        subreddit=subreddit_name)

        for post_data in subreddit.get_new(limit=None):

            post_data.replace_more_comments(limit=None, threshold=0)

            post_date = datetime.datetime.fromtimestamp(post_data.created_utc)
            if post_date.date() > before:
                continue
            if post_date.date() < after:
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

            yield(post_dict)

            post_count += 1
            progress.update(posts=post_count)

            post_data.replace_more_comments(limit=None)

            for comment_dict in traverse_comments(post_data.id,
                                                  post_data.comments):
                yield(comment_dict)

                comment_count += 1
                progress.update(comments=comment_count)



def main():
    """
    Parse CLI arguments, fetch data from requested subreddits, and generate
    Excel workbook.
    """

    Config.initialize()

    config = Config.get_config()

    database = Database(config["database_file"], config["debug"])

    for post in fetch_data(config["subreddits"],
                           config["date_range"]["after"],
                           config["date_range"]["before"]):
        database.add_update_entry(post)

if __name__ == "__main__":
    main()
