---
layout: default
title: ITVS | Design
---

# Design

***

## Modules

For retrieving information from reddit we are using the module **[PRAW](https://praw.readthedocs.io/en/stable/)** (Python reddit API wrapper) which provides built in functionality to prevent throttling from reddit. 
We have written our own custom database wrapper (ranalyze/pkg/database.py) for storing posts and comments, which provides a simple way to add comment and post data from the API into the database. 
Additionally, for progress tracking on machines that are performing these scraping jobs, we have included a progress module to provide progress updates to standard output when running. 
All of these modules are combined in ranalyze.py. When run, this parses the command line arguments for configuration information on the type of scraping job to be run, makes a database connection using our database wrapper, and adds or updates all of the found posts and comments in the specified date range and subreddits. 
    

### Data

Data from the scraping jobs is output to a SQLite database using our database wrapper. 
For our purposes, we are using a single table for storage of both comments and posts, called **entries** with the following columns: 

 - **id** - *(text, primary key)* the id of the comment or post as provided by reddit 
 - **permalink** - *(text, unique)* the link to the comment section if the particular row is a post
 - **root_id** - *(text)* the id of the associated post to a comment
 - **up_votes** - *(integer)* the net upvotes *(upvotes - downvotes)* for a post
 - **up_ratio** - *(real)* upvotes / *(total votes)*
 - **time_submitted** - *(integer)* the UTC timestamp of when the post was submitted
 - **time_updated** - *(integer)* the UTC timestamp of when this entry in the database was most recently updated
 - **posted_by** - *(text)* reddit account name of the person who posted the entry 
 - **title** - *(text)* the title of the submitted post. Relevant only for posts 
 - **subreddit** - *(text)* the subreddit that the entry came from
 - **external_url** - *(text)* if the submission is an external link, then that link. Relevant only for posts. 
 - **text_content** - *(text)* If the entry is a post and that post is a self post, then this is the body of the post. If the entry is a comment, then this is the comment body
 - **parent_id** - *(text, foreign key referencing id)* for entries that are comments, if this is a reply to the original post, this is the id of that post. If the comment is a reply to another comment, this is the id of the parent comment. Relevant only for comments. 
 - **gilded** - *(integer)* 1 if the entry is gilded, 0 if not
 - **deleted** - *(integer)* 1 if the comment or post was subsequently deleted after the original scrape, 0 otherwise 