"""
A simple Flask API giving HTTP access to the command line functionality
to run: 
    python api.py [database file] [scrape config file]
"""
import flask
import os
import sys
from .ranalyze import search
from .ranalyze import utils
from .ranalyze.database import database

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

@app.route('/simple_search/', methods=['POST'])
def simple_search():
    """
    Search wtihout expressions
    """
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
    return flask.jsonify(entries)

@app.route('/advanced_search/', methods=['POST'])
def advanced_search():
    """
    Search with expressions
    """
    condition = search.Condition()
    print(flask.request.get_json(force=True, silent=True))
    request = flask.request.get_json(force=True, silent=True)
    if 'expression' in request: 
        print(request['expression'])
        tree = search.ExpressionTree.from_expression(request["expression"])
        print(tree.__dict__)
        condition = search.tree_to_condition(tree)
        print(condition)

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
    return flask.jsonify(entries)

@app.route('/scrape/', methods=['GET', 'POST'])
def scrape():
    """
    on GET: returns JSON of the current 
    """
    if flask.request.method == 'POST':
        with open(CONFIG_FILE, 'w') as config_file:
            print("Updating "+CONFIG_FILE)
            to_scrape = flask.request.get_json(force=True, silent=True)
            for i in to_scrape:
                print(i)
                config_file.write(i)
    else:
        with open(CONFIG_FILE) as config_file:
            rv = [i for i in config_file]
            return flask.jsonify(rv);
    
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Error: specify the database to connect to and a config file")
        print("e.g.: python api.py database.db config.txt")
    else:
        DATABASE = database.Database(sys.argv[1])
        CONFIG_FILE = sys.argv[2]
        app.run()
