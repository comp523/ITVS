"""
Create tables in the database
"""
import sqlite3

connection = sqlite3.connect('reddit-data.db')
cursor = connection.cursor()
queries = ("DROP TABLE IF EXISTS posts",
           "DROP TABLE IF EXISTS comments",
           "DROP TABLE IF EXISTS entries",
           """
           CREATE TABLE entries (
           id text PRIMARY KEY, permalink text UNIQUE NOT NULL, root_id text,
           up_votes integer, up_ratio real, time_submitted integer,
           time_updated integer, posted_by text, title text, subreddit text,
           external_url text, text_content text, parent_id text, gilded integer,
           deleted integer,
           FOREIGN KEY(parent_id) REFERENCES entries(id)
           )
           """)
for query in queries:
    cursor.execute(query)
connection.commit()
connection.close()
