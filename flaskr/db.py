import sqlite3
import redis

import click
from flask import current_app, g
from flask.cli import with_appcontext

REDIS_POOL = {}

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def get_redis(): 
    if 'pool' not in REDIS_POOL:
        app_debug = current_app.config['DEBUG']
        redis_host = '127.0.0.1' if app_debug else 'redis_server'
        REDIS_POOL['pool'] = redis.ConnectionPool(host=redis_host, port=6379, decode_responses=True)
    if 'redis' not in g: 
        g.redis = redis.Redis(connection_pool=REDIS_POOL['pool'])
    return g.redis

def close_db(e=None):
    db = g.pop('db', None) 
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
