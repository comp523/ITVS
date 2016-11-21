CHAR_SET = "utf8"

KEYWORD_COLUMNS = {"text_content", "title"}

CONFIG_TABLE = "config"

CONFIG_ENTRY_FIELDS = {"id", "name", "value"}


ENTRY_TABLE = "entries"

ENTRY_FIELDS = {"id", "up_votes", "time_submitted", "time_updated", "posted_by",
                "subreddit", "text_content", "gilded", "deleted"}

COMMENT_FIELDS = ENTRY_FIELDS | {"root_id", "parent_id"}

POST_FIELDS = ENTRY_FIELDS | {"permalink", "up_ratio", "title", "external_url"}

FREQUENCY_TABLE = "frequency"

WORD_DAY_FIELDS = {"id", "word", "day", "month", "year", "total", "entries"}

