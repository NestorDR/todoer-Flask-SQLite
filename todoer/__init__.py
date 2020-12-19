# -*- coding: utf-8 -*-

# Flask: is a lightweight WSGI (Web Server Gateway Interface) web application framework
from flask import Flask
# OS: library that allows access to functionalities dependent on the Operating System.
from os import path


def create_app(py_config_file_: str = '') -> object:
    """
    Create and configure the app
    Visit: https://hackersandslackers.com/configure-flask-applications/

    :param py_config_file_:

    :return: app
    """

    # Instead of creating a Flask instance globally, it will be created inside a function. This function (create_app) is
    #  known as the application factory. Any configuration, registration, and other setup the application needs will
    #  happen inside the function, then the application will be returned.
    app = Flask(__name__, instance_relative_config=True)

    # Identify configuration file
    current_dir_ = path.dirname(path.abspath(__file__))
    if py_config_file_ == '':
        # use default config file location
        py_config_file_ = path.abspath(path.join(current_dir_, '../config.py'))
    else:
        py_config_file_ = path.abspath(py_config_file_)

    # raise error if python config file doesn't exist
    if not path.isfile(py_config_file_):
        raise EnvironmentError('App config file does not exist at %s' % py_config_file_)

    # Load the instance config
    app.config.from_pyfile(py_config_file_, silent=True)

    # Import and register access to the database
    from . import db
    db.init_app(app)

    # Import and register the blueprints
    from . import auth, todo
    app.register_blueprint(auth.bp)
    app.register_blueprint(todo.bp)
    # Unlike the 'auth' blueprint, the 'todo' blueprint does not have a url_prefix
    # The 'todo' is the main feature of Todoer, so it makes sense that the 'todo' index will be the main index.
    # So that url_for('index') or url_for('todo.index') will both work, generating the same '/' URL either way.
    app.add_url_rule('/', endpoint='index')

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello World 3!'

    # the application is returned.
    return app
