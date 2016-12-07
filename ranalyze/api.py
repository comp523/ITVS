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
from .constants import CONFIG_TABLE, ENTRY_FIELDS, ENTRY_TABLE, SUBREDDIT_TABLE
from .database import (
    add_update_object,
    connect,
    execute_query
)
from .frequency import BLACKLIST, overview
from .imprt import schedule_for_import
from .models import ConfigEntryFactory, SubredditFactory
from .query import Condition, DeleteQuery, SelectQuery
from .scrape import get_subreddits
from .search import search as search_db
from .utils import iso_to_date, timestamp_to_str

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


@app.route('/config/<_id>', methods=["GET", "DELETE"])
def config_item(_id):
    condition = Condition("id", _id)
    query = SelectQuery(table=CONFIG_TABLE,
                        where=condition)
    results = [e.dict for e in execute_query(query)]
    if flask.request.method == "GET":
        if not results:
            return flask.jsonify({})
    else:
        query = DeleteQuery(table=CONFIG_TABLE,
                            where=condition)
        execute_query(query, transpose=False, commit=True)
    return flask.jsonify(results[0])


@app.route('/config', methods=["GET"])
def config_query():
    request = flask.request.args
    if "name" in request and request["name"] == "serverBlacklist":
        results = list(BLACKLIST)
    else:
        condition = Condition()
        for key in request:
            condition &= Condition(key, request[key])
        query = SelectQuery(table=CONFIG_TABLE,
                            where=condition)
        results = [e.dict for e in execute_query(query)]
    return flask.jsonify(results)


@app.route('/config', methods=['POST'])
@app.route('/config/<_id>', methods=['POST'])
def config_update(_id=None):
    request = dict(flask.request.get_json())
    if _id:
        request["id"] = _id
    if 'name' not in request or 'value' not in request:
        return flask.abort(400)
    item = ConfigEntryFactory.from_dict(request)
    insert_id = add_update_object(item, CONFIG_TABLE)
    if _id is None:
        _id = insert_id
    condition = Condition("id", _id)
    query = SelectQuery(table=CONFIG_TABLE,
                        where=condition)
    result = execute_query(query)[0].dict
    return flask.jsonify(result)


@app.route('/entry/import', methods=['POST'])
def entry_import():
    """
    on POST: imports a csv file into the database
    """
    f = flask.request.files['file']
    temp = NamedTemporaryFile()
    f.save(temp)
    f.flush()
    os.fsync(f.fileno())
    count = schedule_for_import(temp.name)
    return flask.jsonify({
        'success': True,
        'status': '{} permalinks scheduled for import'.format(count)
    })


@app.route('/entry')
def entry_query():
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

    options["subreddit_exclude_mode"] = False

    if "subredditMode" in request and request["subredditMode"] == "exclusive":
        options["subreddit_exclude_mode"] = True

    if "order" in request:
        order = request["order"]
        if order[0] == "-":
            order = order[1:] + " DESC"
        options["order"] = order

    # pass through arguments

    for key in {"limit", "offset"}:
        if key in request:
            options[key] = request[key]

    for date_key in {"after", "before"}:
        if date_key in request:
            options[date_key] = iso_to_date(request[date_key])

    results, count = search_db(include_count=True, **options)

    entries = [e.dict for e in results]

    if download and entries:
        for entry in entries:
            entry["time_submitted_formatted"] = timestamp_to_str(entry["time_submitted"])
            entry["time_updated_formatted"] = timestamp_to_str(entry["time_updated"])
            if "root_id" not in entry:
                entry["root_id"] = entry["id"]
        fieldnames = ENTRY_FIELDS | {"time_submitted_formatted", "time_updated_formatted"}
        with StringIO() as buffer:
            writer = DictWriter(buffer, fieldnames=fieldnames)
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

    request = flask.request.args

    condition = (Condition("subreddit", "like", "%{}%".format(request["name"]))
                 if "name" in request else Condition())

    query = SelectQuery(table=ENTRY_TABLE,
                        distinct=True,
                        columns="subreddit",
                        where=condition)

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


@app.route('/subreddit', methods=["GET"])
def subreddit_query():
    request = dict(flask.request.args)
    condition = Condition()
    for key, value in request.items():
        condition &= Condition(key, value)
    query = SelectQuery(table=SUBREDDIT_TABLE,
                        where=condition)
    results = execute_query(query, transpose=False)
    for item in results:
        condition = Condition("subreddit", item["name"])
        columns = ("SUM(permalink IS NULL) as comments, "
                   "SUM(permalink IS NOT NULL) as posts, "
                   "MIN(time_submitted) as oldest_entry")
        query = SelectQuery(table=ENTRY_TABLE,
                            columns=columns,
                            where=condition)
        item.update(execute_query(query, transpose=False)[0])
        for key in item:
            if item[key] is None:
                item[key] = 0
    return flask.jsonify(results)


@app.route('/subreddit/<name>', methods=["GET", "DELETE"])
def subreddit_item(name, get=False):
    condition = Condition("name", name)
    query = SelectQuery(table=SUBREDDIT_TABLE,
                        where=condition)
    results = execute_query(query, transpose=False)
    if flask.request.method == "GET" or get:
        if not results:
            return flask.jsonify({})
    else:
        query = DeleteQuery(table=SUBREDDIT_TABLE,
                            where=condition)
        execute_query(query, transpose=False, commit=True)
    condition = Condition("subreddit", results[0]["name"])
    columns = ("SUM(permalink IS NULL) as comments, "
               "SUM(permalink IS NOT NULL) as posts, "
               "MIN(time_submitted) as oldest_entry")
    query = SelectQuery(table=ENTRY_TABLE,
                        columns=columns,
                        where=condition)
    results[0].update(execute_query(query, transpose=False)[0])
    for key in results[0]:
        if results[0][key] is None:
            results[0][key] = 0
    return flask.jsonify(results[0])


@app.route('/subreddit/<name>', methods=['POST'])
def subreddit_update(name):
    request = dict(flask.request.get_json())
    request["name"] = name
    item = SubredditFactory.from_dict(request)
    add_update_object(item, SUBREDDIT_TABLE)
    return subreddit_item(name, True)


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
