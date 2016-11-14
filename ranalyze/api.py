"""
A simple Flask API giving HTTP access to the command line functionality
to run: 
    python api.py [database file] [scrape config file]
    OR 
    if config.txt and a scraped 'results.db' file have been created 
    python api.py
"""
import flask
import sys
import os
from csv import DictWriter
from .search import search
from .utils import iso_to_date
from .database import connect, ENTRY_COLUMNS

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
        return flask.send_file(os.environ['OPENSHIFT_DATA_DIR']+'/simple_result.csv')

    request = flask.request.get_json(force=True, silent=True)

    for date_key in ("after", "before"):
        if date_key in request:
            request[date_key] = iso_to_date(request[date_key])

    entries = [e.dict for e in search(**request)]

    keys = ENTRY_COLUMNS.keys()

    with open(os.environ['OPENSHIFT_DATA_DIR']+'/simple_result.csv', 'w') as return_file: 
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
        return flask.send_file(os.environ['OPENSHIFT_DATA_DIR']+'/advanced_result.csv')

    request = flask.request.get_json(force=True, silent=True)

    for date_key in ("after", "before"):
        if date_key in request:
            request[date_key] = iso_to_date(request[date_key])

    entries = [e.dict for e in search(**request)]

    keys = ENTRY_COLUMNS.keys()

    with open(os.environ['OPENSHIFT_DATA_DIR'] + '/advanced_result.csv',
              'w') as return_file:
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
        if not os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE, 'w'):
                pass
        with open(CONFIG_FILE, 'r') as config_file:
            rv = [i.replace('\n', '') for i in config_file]
            return flask.jsonify(rv)


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

