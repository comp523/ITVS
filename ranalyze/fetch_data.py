"""
Module docstring
"""

import datetime
import praw

def fetch_data(subreddit_set, after, before):
    """
    @param subreddit_set - set of subreddits from which to retrieve data
    @param after - ignores posts before this datetime
    @param before - ignores posts after this datetime
    """
    reddit = praw.Reddit(user_agent="Documenting ecig subs")
    for subreddit_name in subreddit_set:
        subreddit = reddit.get_subreddit(subreddit_name)
        for post in subreddit.get_new(limit=None):
            post_date = datetime.datetime.fromtimestamp(post.created_utc)
            if post_date.date() > before:
                continue
            if post_date.date() < after:
                continue
            pretty_submitted_date = post_date.isoformat()
            pretty_now_date = datetime.datetime.utcnow().isoformat()
            post_content = {
                'subreddit': subreddit_name,
                'permalink': post.permalink,
                'url': post.url,
                'num_comments': post.num_comments,
                'upvotes': post.ups,
                'downvotes': post.downs,
                'title': post.title,
                'time_submitted': pretty_submitted_date,
                'time_retrieved': pretty_now_date
            }
            yield(subreddit_name, post_content)


if __name__ == "__main__":
    total_posts = 0
    for i in fetch_data(['vaping'], datetime.datetime.fromtimestamp(0), datetime.datetime.utcnow()):
        print(i)
        total_posts += 1
    print(total_posts)
