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
import io

from csv import DictWriter
from io import StringIO
from .frequency import overview
from .search import search as search_db
from .utils import iso_to_date
from .query import Condition, SelectQuery
from .database import connect, execute_query, ENTRY_COLUMNS, ENTRY_TABLE, CONFIG_TABLE

app = flask.Flask(__name__)
CONFIG_FILE = None
DATABASE = None

print(app.static_folder)
#exit()


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


@app.route('/app.js')
def compile_js():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    sub_dirs = ['controllers', 'services']
    js_files = ['main.js']
    for sub in sub_dirs:
        path = os.path.join(cur_path, 'static/js', sub)
        js_files.extend([os.path.join(path, file) for file in os.listdir(path)])
    out_buffer = io.StringIO()
    for file in js_files:
        with open(os.path.join(cur_path, 'static/js', file)) as fp:
            out_buffer.write(fp.read())
        out_buffer.write("\n")
    response = flask.Response(out_buffer.getvalue(), mimetype='text/javascript')
    return response


@app.route('/config/subreddits/')
def config_subreddits():
    condition = Condition("name", "subreddit")
    query = SelectQuery(table=CONFIG_TABLE,
                        where=condition)
    results = execute_query(query, transpose=False)
    col = "COUNT(*)"
    for item in results:
        condition = Condition("subreddit", item["value"])
        post_condition = Condition("permalink", "IS NOT", None)
        comment_condition = Condition("permalink", None)
        query = SelectQuery(table=ENTRY_TABLE,
                            where=condition & post_condition,
                            columns=col)
        item["posts"] = execute_query(query, transpose=False)[0][col]
        query = SelectQuery(table=ENTRY_TABLE,
                            where=condition & comment_condition,
                            columns=col)
        item["comments"] = execute_query(query, transpose=False)[0][col]
    return flask.jsonify(results)


@app.route('/entry/search/')
def entry_search():
    """
    Search wtihout expressions
    on GET: return csv of most recent simple search
    on POST: return JSON of search
    """

    request = flask.request.args

    options = {}

    download = False

    if "download" in request:
        download = (request["download"].lower() == "true")

    if "subreddits" in request:
        options["subreddits"] = request.getlist("subreddits")

    if "advanced" in request and request["advanced"].lower() == "true":
        options["expression"] = request["query"]
    else:
        options["keywords"] = request["query"].split()

    for date_key in ("after", "before"):
        if date_key in request:
            options[date_key] = iso_to_date(request[date_key])

    entries = [e.dict for e in search_db(**options)]

    if download:
        keys = ENTRY_COLUMNS.keys()
        with StringIO() as buffer:
            writer = DictWriter(buffer, fieldnames=keys)
            writer.writeheader()
            writer.writerows(entries)
            csv = buffer.getvalue()
            response_options = {
                "mimetype": 'text/csv',
                "headers": {"Content-disposition":
                            "attachment; filename=results.csv"}
            }
            return flask.Response(csv, **response_options)
    
    return flask.jsonify(entries)


@app.route('/entry/subreddits')
def entry_subreddits():

    query = SelectQuery(table=ENTRY_TABLE,
                        distinct=True,
                        columns="subreddit")

    return flask.jsonify([e['subreddit'] for e in
                          execute_query(query, transpose=False)])


@app.route('/frequency/overview', methods=['GET'])
def frequency_overview():
    """
    """

    request = flask.request.args

    options = {
        "gran": request["gran"],
        "limit": int(request["limit"])
    }

    for key in ("year", "month", "day"):
        if key in request:
            options[key] = [int(v) for v in request.getlist(key)]

    return flask.jsonify(overview(**options))

def env_shiv():
    """
    shiv the os.environ dictionary to work on local machines
    """
    try:
        os.mkdir("/tmp/ranalyze")
    except FileExistsError:
        pass

    os.environ.update({
        "OPENSHIFT_DATA_DIR": "/tmp/ranalyze",
        "OPENSHIFT_MYSQL_DB_HOST": os.environ["MYSQL_DB_HOST"],
        "OPENSHIFT_MYSQL_DB_USERNAME": os.environ["MYSQL_DB_USER"],
        "OPENSHIFT_MYSQL_DB_PASSWORD": os.environ["MYSQL_DB_PASSWORD"],
        "OPENSHIFT_MYSQL_DB_PORT": os.environ["MYSQL_DB_PORT"]
    })


if "OPENSHIFT_DATA_DIR" not in os.environ:
    env_shiv()
connect()
CONFIG_FILE = os.path.join(os.environ['OPENSHIFT_DATA_DIR'], 'config.txt')


if __name__ == '__main__':
    connect()
    CONFIG_FILE = sys.argv[2]
    app.run()

