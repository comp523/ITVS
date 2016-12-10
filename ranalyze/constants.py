"""
This file contains constants used elsewhere in the module.
"""

# # SETTINGS # #

# Charset used when connecting to the database
CHAR_SET = "utf8"

# Number of permalinks to import at a time
IMPORT_CHUNK_SIZE = 100

# Columns to consider when performing a keyword search
KEYWORD_COLUMNS = {"text_content", "title"}

# # DATABASE INFORMATION # #

# Tables #

CONFIG_TABLE = "config"

ENTRY_TABLE = "entries"

FREQUENCY_TABLE = "frequency"

IMPORT_TABLE = "import"

SUBREDDIT_TABLE = "subreddits"

# Column Sets #

CONFIG_ENTRY_FIELDS = {"id", "name", "value"}

BASE_FIELDS = {"id", "up_votes", "time_submitted", "time_updated", "posted_by",
                "subreddit", "text_content", "gilded", "deleted"}

COMMENT_FIELDS = BASE_FIELDS | {"root_id", "parent_id"}

POST_FIELDS = BASE_FIELDS | {"permalink", "up_ratio", "title", "external_url"}

ENTRY_FIELDS = COMMENT_FIELDS | POST_FIELDS

SUBREDDIT_FIELDS = {"name", "scraping", "last_scraped"}

WORD_DAY_FIELDS = {"id", "word", "day", "month", "year", "total", "entries"}

