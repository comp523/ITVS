import sqlite3

def create_db():
    connection = sqlite3.connect('reddit-data.db')
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE posts
    (id integer, permalink text, up_votes integer, up_ratio real,
    date_posted integer, date_updated integer, posted_by text,
    controversiality integer, external_url text, self_text text, gilded integer)
    """)
    cursor.execute("""
    CREATE TABLE comments
    (id integer, post_id integer, parent_id integer, reddit_comment_id integer,
    posted_by text, up_votes integer, date_posted integer, date_updated integer)
    """)
    connection.commit()
    connection.close()


create_db()