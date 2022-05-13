# -*- coding: utf-8 -*-
# Visit https://flask.palletsprojects.com/en/2.1.x/tutorial/database/

# Click: Command Line Interface Creation Kit, package to run commands in console/terminal to create the database model
import click
# Flask: is a lightweight WSGI (Web Server Gateway Interface) web application framework
#        - "current_app" is a special object that points to the Flask application handling the request
#        - "g" is other special object that is unique for each request. It is used to store data that might be accessed
#           by multiple functions during the request. The connection is stored and reused instead of creating a new
#           connection, if get_db is called a second time in the same request.
from flask import current_app, g
# Flask.cli: Command Line Interface module
#           "with_appcontext" is a Flask decorator in the flask.cli module that wraps a callback to guarantee it will be
#           called with a script's application context. And we can access the variables that are in the app config.
from flask.cli import with_appcontext
# SQLite3: support for SQLite
import sqlite3


def get_db():
    """
    Connect to the Database

    :return: database connection
    """
    if 'db' not in g:
        # Establish a connection to the file pointed at by the DATABASE configuration key,
        #  and add as a property of g object
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Tells the connection to return rows that behave like dicts. This allows accessing the columns by name
        g.db.row_factory = sqlite3.Row

        """
        # Alternatively for MySql
        if 'db' not in g:
            g.db = mysql_connector.connect(
                host=current_app.config['DATABASE_HOST'],
                user=current_app.config['DATABASE_USER'],
                password=current_app.config['DATABASE_PASSWORD'],
                database=current_app.config['DATABASE']
            )
            g.c = g.db.cursor(dictionary=True)

        return g.db, g.c
        """
    return g.db


def close_db(e=None):
    """
    Close existing connection

    :param e:
    """
    # Remove "db" property of object g
    db = g.pop('db', None)

    if db is not None:
        # If the connection exists, it is closed.
        db.close()


def init_db():
    """
    Open and execute a file with the SQL commands necessary to create empty tables, before storing and retrieving data.
    """
    # Connect to the Database
    db = get_db()

    # open_resource() opens a file relative to the flaskr package,
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# click.command() defines a command line, command called init-db that calls the init_db function and shows a success
#  message to the user. To invoke it, run in CLI: flask init-db
@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    Clear the existing data and create new tables.
    """
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """
    Register close_db and init_db_command functions in the application instance

    :param app: application
    """
    # Tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # Adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)
