"""
A simple Flask API giving HTTP access to the command line functionality
to run: 
    python api.py [database file] [scrape config file]
    OR 
    if config.txt and a scraped 'results.db' file have been created 
    python api.py
"""
import flask
import os
import sys
from csv import DictWriter
from .ranalyze import search
from .ranalyze import utils
from .ranalyze import database

app = flask.Flask(__name__)
CONFIG_FILE = None
DATABASE = None

@app.route('/')
def index():
    """
    Routing for the home page
    """
    return flask.send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """
    Routing for static files
    """
    return flask.send_from_directory(app.static_folder, filename)

@app.route('/simple_search/', methods=['GET', 'POST'])
def simple_search():
    """
    Search wtihout expressions
    on GET: return csv of most recent simple search
    on POST: return JSON of search
    """
    if flask.request.method == 'GET':
        return flask.send_file('simple_result.csv')

    condition = search.Condition()
    request = flask.request.get_json(force=True, silent=True)
    if 'keywords' in request:
        keywords = ["%{}%".format(k) for k in request["keywords"]]
        for keyword in keywords:
            keyword_condition = search.multi_column_condition(search.KEYWORD_COLUMNS,
                                                       "LIKE",
                                                       keyword)
            condition |= keyword_condition
    if 'subreddits' in request: 
        subreddit_condition = search.Condition()
        for subreddit in request['subreddits']:
            subreddit_condition |= search.Condition('subreddit', subreddit)
        condition &= subreddit_condition

    if 'after' in request: 
        date = utils.iso_to_date(request["after"])
        condition &= search.Condition("time_submitted", ">=", date)

    if 'before' in request:
        date = utils.iso_to_date(request["before"])
        condition &= search.Condition("time_submitted", "<=", date)
    query = database.SelectQuery(table=database.Database.ENTRY_TABLE,
                        distinct=True,
                        where=condition,
                        columns="*")
    rows = DATABASE.execute_query(query, transpose=False)
    entries = [dict(zip(e.keys(), e)) for e in rows]
    keys = entries[0].keys()
    
    with open('simple_result.csv', 'w') as return_file: 
        writer = DictWriter(return_file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(entries)
    
    return flask.jsonify(entries)

@app.route('/advanced_search/', methods=['GET', 'POST'])
def advanced_search():
    """
    on GET: return CSV of most recent advanced search 
    on POST: return JSON of advanced search
    """
    if flask.request.method == 'GET':
        return flask.send_file('advanced_result.csv')

    condition = search.Condition()
    request = flask.request.get_json(force=True, silent=True)
    if 'expression' in request: 
        tree = search.expression_to_tree(request["expression"])
        condition = search.tree_to_condition(tree)

    if 'subreddits' in request: 
        subreddit_condition = search.Condition()
        for subreddit in request['subreddits']:
            subreddit_condition |= search.Condition('subreddit', subreddit)
        condition &= subreddit_condition

    if 'after' in request: 
        date = utils.iso_to_date(request["after"])
        condition &= search.Condition("time_submitted", ">=", date)

    if 'before' in request:
        date = utils.iso_to_date(request["before"])
        condition &= search.Condition("time_submitted", "<=", date)
    query = database.SelectQuery(table=database.Database.ENTRY_TABLE,
                        distinct=True,
                        where=condition,
                        columns="*")
    rows = DATABASE.execute_query(query, transpose=False)
    entries = [dict(zip(e.keys(), e)) for e in rows]
    keys = entries[0].keys()
    
    with open('advanced_result.csv', 'w') as return_file: 
        writer = DictWriter(return_file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(entries)

    return flask.jsonify(entries)

@app.route('/scrape', methods=['GET', 'POST'])
def scrape():
    """
    on GET: returns JSON of the current subs being scraped
    on POST: updates scrape config file
    """
    if flask.request.method == 'POST':
        rv = []
        with open(CONFIG_FILE, 'w') as config_file:
            to_scrape = flask.request.get_json(force=True, silent=True)
            for i in to_scrape:
                config_file.write(i+'\n')
                rv.append(i)
        return flask.jsonify(rv)
    else:
        with open(CONFIG_FILE) as config_file:
            rv = [i.replace('\n', '') for i in config_file]
            return flask.jsonify(rv);

def mysql_init():
    global DATABASE, CONFIG_FILE
    DATABASE = database.Database(os.environ['OPENSHIFT_MYSQL_DB_URL'])
    CONFIG_FILE = 'config.txt'

if __name__ == '__main__':
    DATABASE = database.Database(sys.argv[1])
    CONFIG_FILE = sys.argv[2]
    app.run()

