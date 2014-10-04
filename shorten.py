import logging
import os
import json
import sqlite3

from contextlib import closing
from functools import wraps

from flask import (
    Flask,
    request,
    session,
    g,
    redirect,
    url_for,
    render_template,
    flash,
    abort,
    Response,
)

import shorten_utils

DATABASE = os.environ.get('SHORTEN_DB_LOCATION', 'shorten.db')
SITE_URL = 'http://127.0.0.1:5000'
DEBUG = False
USERNAME = 'foo'
PASSWORD = 'bar'

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'foobarbaz'

log = logging.getLogger(__name__)
app.logger.addHandler(log)


def connect_db():
    return sqlite3.connect(DATABASE)


def init_db():
    with closing(connect_db()) as db:
        with open('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


def check_auth(username, password):
    return username == USERNAME and password == PASSWORD


def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/add/<path:long_url>')
def add_url(long_url, authenticated=False, return_json=False):
    if not authenticated:
        return redirect(SITE_URL, code=302)
    long_url = long_url.strip()
    if not 'http://' in long_url:
        long_url = 'http://' + long_url
    try:
        query = 'select short_url from entries where long_url=(?)'
        cur = g.db.execute(query, [long_url])
        short_url = cur.fetchone()[0]

        if return_json:
            return json.dumps(short_url)
        else:
            flash("That url is already in the database.")
            return redirect(url_for('show_entries'))
    except:
        pass

    try:
        query = 'select seq from sqlite_sequence where name="entries"'
        conn = g.db.execute(query)
        id_number = conn.fetchone()[0]
    except TypeError:
        id_number = 0

    short_url = shorten_utils.get_short_url_from_id(id_number + 1)

    g.db.execute(
        'insert into entries (long_url, short_url) values (?, ?)',
        [long_url, short_url]
    )
    g.db.commit()

    if return_json:
        return json.dumps(short_url)
    else:
        return redirect(url_for('show_entries'))


@app.route('/add/form/', methods=['POST'])
def add_url_via_form():
    if not session.get('logged_in'):
        return redirect(SITE_URL, code=302)
    return add_url(request.form['url'], authenticated=True)


@app.route('/a/<path:long_url>')
@requires_auth
def add_url_via_api(long_url):
    # long url should be a query parameter string
    try:
        long_url = json.loads(long_url)
    except ValueError:
        pass
    return add_url(long_url, authenticated=True, return_json=True)


@app.route('/g/<path:short_url>')
@requires_auth
def get_url_via_api(short_url):
    try:
        short_url = json.loads(short_url)
    except ValueError:
        pass
    return process_short_url(short_url, return_json=True)


@app.route('/<short_url>')
def process_short_url(short_url, return_json=False):
    try:
        id_number = shorten_utils.get_id_from_short_url(short_url)
        query = 'select long_url from entries where id=(?)'
        cur = g.db.execute(query, [id_number])
        long_url = cur.fetchone()[0]
        print long_url

        if return_json:
            return json.dumps(long_url)
        else:
            return redirect(long_url, code=302)
    except:
        abort(404)


@app.route('/show/')
def show_entries():
    cur = g.db.execute(
        'select long_url, short_url from entries order by id desc'
    )
    entries = [
        dict(long_url=row[0], short_url=row[1])
        for row in cur.fetchall()
    ]
    return render_template('show_entries.html', entries=entries)


@app.route('/')
def index():
    return redirect('/login', code=302)

if __name__ == '__main__':
    app.run(debug=False)
