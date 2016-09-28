"""
Create tables in the database
"""
import sqlite3

connection = sqlite3.connect('reddit-data.db')
cursor = connection.cursor()
queries = ("DROP TABLE IF EXISTS posts",
           "DROP TABLE IF EXISTS comments",
           """
           CREATE TABLE posts (id integer PRIMARY KEY, permalink text,
           up_votes integer, up_ratio real, time_submitted integer,
           time_updated integer, posted_by text, title text, subreddit text,
           controversiality integer, external_url text, self_text text,
           gilded integer)
           """,
           """
           CREATE TABLE comments
           (id integer PRIMARY KEY , post_id integer, parent_id integer,
           posted_by text, up_votes integer, time_submitted integer,
           time_posted integer, reddit_comment_id integer)
           """)
for query in queries:
    cursor.execute(query)
connection.commit()
connection.close()
