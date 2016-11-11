"""
"""

from datetime import datetime
from types import SimpleNamespace
from .database import *
from .models import WordDay
from .query import Condition, SelectQuery

BLACKLIST = {"i", "i'd", "i'll", "i'm", "i've", "a", "about",
             "actually", "after", "all", "also", "always", "an",
             "and", "any", "are", "aren't", "around", "at", "be",
             "because", "been", "being", "between", "but", "by",
             "can", "can't", "could", "did", "didn't", "do",
             "doesn't", "don't", "even", "ever", "every", "few",
             "find", "for", "from", "get", "go", "going", "good",
             "got", "gt", "ha", "had", "hasn't", "have", "he",
             "he's", "her", "here", "him", "his", "how", "if",
             "in", "into", "is", "isn't", "it", "it's", "just",
             "kind", "know", "least", "less", "let", "like",
             "long", "look", "lot", "make", "many", "maybe", "me",
             "mean", "might", "more", "most", "much", "my", "no",
             "not", "of", "on", "one", "only", "or", "other",
             "our", "out", "over", "part", "pretty", "put",
             "quite", "really", "said", "same", "say", "see",
             "seem", "seems", "she", "should", "so", "some",
             "still", "such", "take", "tell", "than", "that",
             "that's", "the", "their", "them", "then", "there",
             "there's", "these", "they", "they're", "thing",
             "think", "this", "though", "through", "time", "to",
             "too", "two", "up", "us", "use", "using", "very",
             "wa", "want", "wasn't", "way", "we", "well", "were",
             "what", "when", "where", "which", "while", "whle",
             "who", "why", "will", "with", "without", "work",
             "would", "wouldn't", "yes", "yet", "you", "you're",
             "your"}


granularity = SimpleNamespace(YEAR='year', MONTH='month', DAY='day')


def digest_entry(entry):
    database = Database.get_instance()
    if not database.object_exists(entry, Database.ENTRY_TABLE):
        date = datetime.fromtimestamp(entry.time_submitted)
        words = [word.lower() for word in
                 Database.WORD_PATTERN.findall(entry.text_content)
                 if word.lower() not in BLACKLIST]
        for word in set(words):
            num_occurrences = words.count(word)
            condition = Condition("month", date.month)
            condition &= Condition("day", date.day)
            condition &= Condition("year", date.year)
            condition &= Condition("word", word)
            select_query = SelectQuery(table=Database.FREQUENCY_TABLE,
                                       where=condition)
            results = database.execute_query(select_query)
            if results:
                word_day = results[0]
                word_day.entries += 1
                word_day.total += num_occurrences
            else:
                word_day = WordDay(day=date.day,
                                   month=date.month,
                                   year=date.year,
                                   word=word,
                                   entries=1,
                                   total=num_occurrences)
            database.add_update_object(word_day, Database.FREQUENCY_TABLE)


def overview(gran, limit, day=None, month=None, year=None):
    database = Database.get_instance()
    column_map = {
        "year": year,
        "month": month,
        "day": day
    }
    date_condition = Condition()
    for key, value in column_map.items():
        sub_condition = Condition()
        try:
            for item in value:
                sub_condition |= Condition(key, item)
        except TypeError:
            sub_condition = Condition(key, value)
        date_condition &= sub_condition
    cols_clause = ("month, day, year, word,"
                   "sum(entries) as entries, sum(total) as total")
    query = SelectQuery(columns=cols_clause,
                        table=Database.FREQUENCY_TABLE,
                        where=date_condition,
                        order="(entries + total) DESC",
                        limit=limit,
                        group=gran
                        )
    results = database.execute_query(query, transpose=False)
    return results
