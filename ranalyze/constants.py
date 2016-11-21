CHAR_SET = "utf8"

KEYWORD_COLUMNS = {"text_content", "title"}

CONFIG_TABLE = "config"

ENTRY_TABLE = "entries"

FREQUENCY_TABLE = "frequency"

CONFIG_ENTRY_FIELDS = {"id", "name", "value"}

BASE_FIELDS = {"id", "up_votes", "time_submitted", "time_updated", "posted_by",
                "subreddit", "text_content", "gilded", "deleted"}

COMMENT_FIELDS = BASE_FIELDS | {"root_id", "parent_id"}

POST_FIELDS = BASE_FIELDS | {"permalink", "up_ratio", "title", "external_url"}

ENTRY_FIELDS = COMMENT_FIELDS | POST_FIELDS


WORD_DAY_FIELDS = {"id", "word", "day", "month", "year", "total", "entries"}

