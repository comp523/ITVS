"""

"""

import re

from datetime import datetime
from types import SimpleNamespace
from .constants import ENTRY_TABLE, FREQUENCY_TABLE
from .database import add_update_object, execute_query, object_exists
from .models import WordDay
from .query import Condition, SelectQuery

BLACKLIST = {'able', 'about', 'above', 'according', 'accordingly', 'across',
             'actually', 'after', 'afterwards', 'again', 'against', "ain't",
             'all', 'allow', 'allows', 'almost', 'alone', 'along', 'already',
             'also', 'although', 'always', 'am', 'among', 'amongst', 'an',
             'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything',
             'anyway', 'anyways', 'anywhere', 'apart', 'appear', 'appreciate',
             'appropriate', 'are', "aren't", 'around', 'as', 'aside', 'ask',
             'asking', 'associated', 'at', 'available', 'away', 'awfully', 'be',
             'became', 'because', 'become', 'becomes', 'becoming', 'been',
             'before', 'beforehand', 'behind', 'being', 'believe', 'below',
             'beside', 'besides', 'best', 'better', 'between', 'beyond', 'both',
             'brief', 'but', 'by', "c'mon", "c's", 'came', 'can', "can't",
             'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly',
             'changes', 'clearly', 'co', 'com', 'come', 'comes', 'concerning',
             'consequently', 'consider', 'considering', 'contain', 'containing',
             'contains', 'corresponding', 'could', "couldn't", 'course',
             'currently', 'definitely', 'described', 'despite', 'did', "didn't",
             'different', 'do', 'does', "doesn't", 'doing', "don't", 'done',
             'down', 'downwards', 'during', 'each', 'edu', 'eg', 'eight',
             'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially',
             'et', 'etc', 'even', 'ever', 'every', 'everybody', 'everyone',
             'everything', 'everywhere', 'ex', 'exactly', 'example', 'except',
             'far', 'few', 'fifth', 'first', 'five', 'followed', 'following',
             'follows', 'for', 'former', 'formerly', 'forth', 'four', 'from',
             'further', 'furthermore', 'get', 'gets', 'getting', 'given',
             'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten',
             'greetings', 'had', "hadn't", 'happens', 'hardly', 'has', "hasn't",
             'have', "haven't", 'having', 'he', "he's", 'hello', 'help',
             'hence', 'her', 'here', "here's", 'hereafter', 'hereby', 'herein',
             'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 'his',
             'hither', 'hopefully', 'how', 'howbeit', 'however', "i'd", "i'll",
             "i'm", "i've", 'ie', 'if', 'ignored', 'immediate', 'in',
             'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates',
             'inner', 'insofar', 'instead', 'into', 'inward', 'is', "isn't",
             'it', "it'd", "it'll", "it's", 'its', 'itself', 'just', 'keep',
             'keeps', 'kept', 'know', 'known', 'knows', 'last', 'lately',
             'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let',
             "let's", 'like', 'liked', 'likely', 'little', 'look', 'looking',
             'looks', 'ltd', 'mainly', 'many', 'may', 'maybe', 'me', 'mean',
             'meanwhile', 'merely', 'might', 'more', 'moreover', 'most',
             'mostly', 'much', 'must', 'my', 'myself', 'name', 'namely', 'nd',
             'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never',
             'nevertheless', 'new', 'next', 'nine', 'no', 'nobody', 'non',
             'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel',
             'now', 'nowhere', 'obviously', 'of', 'off', 'often', 'oh', 'ok',
             'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 'onto', 'or',
             'other', 'others', 'otherwise', 'ought', 'our', 'ours',
             'ourselves', 'out', 'outside', 'over', 'overall', 'own',
             'particular', 'particularly', 'per', 'perhaps', 'placed',
             'please', 'plus', 'possible', 'presumably', 'probably', 'provides',
             'que', 'quite', 'qv', 'rather', 'rd', 're', 'really', 'reasonably',
             'regarding', 'regardless', 'regards', 'relatively', 'respectively',
             'right', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second',
             'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems',
             'seen', 'self', 'selves', 'sensible', 'sent', 'serious',
             'seriously', 'seven', 'several', 'shall', 'she', 'should',
             "shouldn't", 'since', 'six', 'so', 'some', 'somebody', 'somehow',
             'someone', 'something', 'sometime', 'sometimes', 'somewhat',
             'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying',
             'still', 'sub', 'such', 'sup', 'sure', "t's", 'take', 'taken',
             'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that',
             "that's", 'thats', 'the', 'their', 'theirs', 'them', 'themselves',
             'then', 'thence', 'there', "there's", 'thereafter', 'thereby',
             'therefore', 'therein', 'theres', 'thereupon', 'these', 'they',
             "they'd", "they'll", "they're", "they've", 'think', 'third',
             'this', 'thorough', 'thoroughly', 'those', 'though', 'three',
             'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too',
             'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try',
             'trying', 'twice', 'two', 'un', 'under', 'unfortunately', 'unless',
             'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used',
             'useful', 'uses', 'using', 'usually', 'value', 'various', 'very',
             'via', 'viz', 'vs', 'want', 'wants', 'was', "wasn't", 'way', 'we',
             "we'd", "we'll", "we're", "we've", 'welcome', 'well', 'went',
             'were', "weren't", 'what', "what's", 'whatever', 'when', 'whence',
             'whenever', 'where', "where's", 'whereafter', 'whereas', 'whereby',
             'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while',
             'whither', 'who', "who's", 'whoever', 'whole', 'whom', 'whose',
             'why', 'will', 'willing', 'wish', 'with', 'within', 'without',
             "won't", 'wonder', 'would', "wouldn't", 'yes', 'yet', 'you',
             "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself',
             'yourselves', 'zero'}


WORD_PATTERN = re.compile(r"[A-Za-z\-']+")


granularity = SimpleNamespace(YEAR='year', MONTH='month', DAY='day')


def digest_entry(entry):
    """
    Process an entry for word frequency
    :param entry:
    :return:
    """

    if not object_exists(entry, ENTRY_TABLE):
        date = datetime.fromtimestamp(entry.time_submitted)
        words = [word.lower() for word in
                 WORD_PATTERN.findall(entry.text_content)
                 if word.lower() not in BLACKLIST]
        for word in set(words):
            if len(word) < 2:
                continue
            num_occurrences = words.count(word)
            condition = Condition("month", date.month)
            condition &= Condition("day", date.day)
            condition &= Condition("year", date.year)
            condition &= Condition("word", word)
            select_query = SelectQuery(table=FREQUENCY_TABLE,
                                       where=condition)
            results = execute_query(select_query)
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
            add_update_object(word_day, FREQUENCY_TABLE)


def overview(gran, limit, day=None, month=None, year=None,
             day_before=None, month_before=None, year_before=None,
             day_after=None, month_after=None, year_after=None):

    if day or month or year:
        column_map = {
            "year": year,
            "month": month,
            "day": day
        }
        date_condition = Condition()
        for key, value in column_map.items():
            if not value:
                continue
            sub_condition = Condition()
            try:
                for item in value:
                    sub_condition |= Condition(key, item)
            except TypeError:
                sub_condition = Condition(key, value)
            date_condition &= sub_condition
        cols_clause = gran + ", sum(entries) as entries, sum(total) as total, word"
        query = SelectQuery(columns=cols_clause,
                            table=FREQUENCY_TABLE,
                            where=date_condition,
                            order="(entries + total) DESC",
                            limit=limit,
                            group=gran+", word")
        return execute_query(query, transpose=False)
    else: # assuming everything else is here, otherwise will error
        # constructs date from day,month,year columns
        existing_date = "cast(rtrim(year *10000+ month *100+ day) as datetime)"
        before_date = "{}-{}-{}".format(year_before, month_before, day_before)
        after_date = "{}-{}-{}".format(year_after, month_after, day_after)
        date_condition = Condition()
        date_condition &= Condition(existing_date, "<=", before_date)
        date_condition &= Condition(existing_date, ">=", after_date)
        cols_clause = gran + ", sum(entries) as entries, sum(total) as total, word"
        query = SelectQuery(columns=cols_clause,
                            table=FREQUENCY_TABLE,
                            where=date_condition,
                            order="(entries + total) DESC",
                            limit=limit,
                            group="word")
        return execute_query(query, transpose=False)

