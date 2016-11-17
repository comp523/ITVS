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
from .search import search as search_db, SelectQuery
from .utils import iso_to_date
from .database import connect, execute_query, ENTRY_COLUMNS, ENTRY_TABLE

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


@app.route('/main.js')
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

@app.route('/search/')
def search():
    """
    Search wtihout expressions
    on GET: return csv of most recent simple search
    on POST: return JSON of search
    """

    request = flask.request.args

    options = {}

    download = False

    if "download" in request:
        download = bool(request["download"])

    if "subreddits" in request:
        options["subreddits"] = request["subreddits"]

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
        if not os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, 'w'):
                pass
        with open(CONFIG_FILE, 'r') as config_file:
            rv = [i.replace('\n', '') for i in config_file]
            return flask.jsonify(rv)


@app.route('/frequency/', methods=['GET'])
def frequency():
    """
    """

    request = flask.request.args

    options = {
        "gran": request["gran"],
        "limit": int(request["limit"])
    }

    for key in ("year", "month", "day"):
        if key in request:
            options[key] = int(request[key])

    return flask.jsonify(overview(**options))


@app.route('/subreddits/')
def subreddits():

    query = SelectQuery(table=ENTRY_TABLE,
                        distinct=True,
                        columns="subreddit")

    return flask.jsonify([e['subreddit'] for e in
                          execute_query(query, transpose=False)])

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

