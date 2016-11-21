"""
A simple Flask API giving HTTP access to the command line functionality
to run: 
    python api.py [database file] [scrape config file]
    OR 
    if config.txt and a scraped 'results.db' file have been created 
    python api.py
"""
import flask
import io
import os

from csv import DictWriter
from io import StringIO
from tempfile import NamedTemporaryFile
from .constants import ENTRY_FIELDS, ENTRY_TABLE
from .database import connect, execute_query, get_subreddits
from .frequency import overview
from .imprt import import_file
from .query import Condition, SelectQuery
from .search import search as search_db
from .utils import iso_to_date

app = flask.Flask(__name__)

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
    sub_dirs = ['controllers', 'directives', 'filters', 'services']
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


@app.route('/config/subreddits')
def config_subreddits():
    return flask.jsonify(get_subreddits())


@app.route('/entry/import', methods=['POST'])
def entry_import():
    """
    on POST: imports a csv file into the database
    """
    f = flask.request.files['file']
    temp = NamedTemporaryFile()
    f.save(temp)
    import_file(temp.name)
    return 'File uploaded successfully'


@app.route('/entry/search')
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

    if "subreddit" in request:
        options["subreddit"] = request.getlist("subreddit")

    if "advanced" in request and request["advanced"].lower() == "true":
        options["expression"] = request["query"]
    else:
        options["keywords"] = request["query"].split()

    # pass through arguments

    for key in {"limit", "order", "offset"}:
        if key in request:
            options[key] = request[key]

    for date_key in {"after", "before"}:
        if date_key in request:
            options[date_key] = iso_to_date(request[date_key])

    results, count = search_db(include_count=True, **options)

    entries = [e.dict for e in results]

    if download:
        keys = ENTRY_FIELDS.keys()
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

    response = {
        "total": count,
        "results": entries
    }

    return flask.jsonify(response)


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

if __name__ == '__main__':
    app.run()
