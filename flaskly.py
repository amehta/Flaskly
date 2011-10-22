# -*- coding: utf-8 -*-
"""
    Flaskly
    ~~~~~~

    A url shortner example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2011 by Apurva Mehta
"""
from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import Flask, request, redirect, \
     render_template, g, flash, url_for

#configuration
DATABASE = 'db/flasky.db'
DEBUG = True
SECRET_KEY ='development_key'

# the little application
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKLY_SETTINGS', silent=True)

def connect_db():
    """Return a new connection to the database"""
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    """Creates the database tables."""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    """Make sure we are connected to the database in each request."""
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    """Close the database again at the end of the request."""
    if hasattr(g, 'db') :
        g.db.close()

@app.route('/<url_short>')
def expand_url(url_short):
    """Check for url in DB"""
    result = query_db('select url_long from urls where url_short = ?',
                        [url_short], one=True)
    if result is None:
        return redirect(url_for("index"))
    else:
        link = result['url_long']
        return redirect(link)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        if request.form['long_url']:
            url = request.form['long_url']
            short = pickShortUrl(url)
            flash('Short Url http:/localhost/' + short)
        else:
            flash('You did not enter a long url')
    return render_template('index.html')

def pickShortUrl(url):
    result = query_db('select url_short from urls where url_long = ?',
                        [url], one=True)
    if result:
        short = result['url_short']
    else:
        result = query_db('select url_short from urls order by id desc limit 1', 
                            one=True)
        if not result:
            short = "1"
        else:
            num = _base36decode(str(result['url_short'])) + 1
            short =  _base36encode(num)
    g.db.execute('insert into urls (url_long, url_short) values (?, ?)',
                   [url, short])
    g.db.commit()
    return str(short)

def _base36encode(number):
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')

    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    base36 = ''

    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]

def _base36decode(number):
    return int(number,36)

if __name__ == "__main__":
    app.run(debug=True)
