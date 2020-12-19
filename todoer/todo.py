# -*- coding: utf-8 -*-

# datetime: this module supplies classes for manipulating dates and times.
import datetime as dt
# Flask: is a lightweight WSGI (Web Server Gateway Interface) web application framework
#        - A "Blueprint" is a way to organize a group of related views and other code. They're configurable
#        - "flash" allows nice and simple way to send and display small messages to the users
#        - "g" is a special object that is unique for each request. It is used to store data that might be accessed by
#          multiple functions during the request
#        - "session" allows referring to the user in the current context, which interacts with the Flask application
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
# Werkzeug: has inbuilt functions to handle exceptions that return an HTTP status code.
from werkzeug.exceptions import abort

from todoer.auth import login_required
from todoer.db import get_db

# Create a Blueprint named 'todo'. Like the app object, the blueprint needs to know where it’s defined, so __name__ is
#  passed as the 2º argument. Unlike the 'auth' blueprint, the 'todo' blueprint does not have a url_prefix.
bp = Blueprint('todo', __name__)


# @bp.route associates the URL '/', '/index' or '/todo/index' with the 'index' view function
@bp.route('/')
def index() -> str:
    """
    The index will show todo list, most recent first.
    A JOIN is used so that the author information from the user table is available in the result.

    :return: rendered html for TODO list
    """
    db = get_db()

    todos = db.execute(
        'SELECT todo.id, todo.task, todo.description, todo.created_by, user.username, todo.created_at,'
        ' todo.completed, todo.completed_at'
        ' FROM todo JOIN user ON todo.created_by = user.id'
        ' ORDER BY todo.created_at DESC'
    ).fetchall()

    return render_template('todo/index.html', todos=todos)


# @bp.route associates the URL '/create' or '/todo/create' with the 'create' view function
@bp.route('/create', methods=['GET', 'POST'])
# The login_required decorator is implemented in auth.py. A user must be logged in to visit these views,
#  otherwise
#  they will be redirected to the login page.
@login_required
def create() -> str:
    """
    When the user visits the /create URL, the create view will return HTML with a form for him/her to fill out.
    When they submit the form, it will validate their input and either show the form again with an error message,
     or go to the index page.

    :return: rendered html for create new instance of todo
    """
    if request.method == 'POST':
        # Extract data from form
        task = request.form['task']
        description = request.form['description']

        # Initialize variables
        error = None

        # Validate task to do has a value
        if not task:
            error = 'Task name is required.'

        if error is not None:
            # If validation fails, the error is shown to the user.
            # flash() stores messages that can be retrieved when rendering the template.
            flash(error)

        else:
            # If validation is ok, then insert new record into datatable of database
            db = get_db()
            db.execute(
                'INSERT INTO todo (task, description, created_by, completed) VALUES (?, ?, ?, 0)',
                (task, description, g.user['id'])
            )
            db.commit()

            # After creating the todo, redirect to the index page.
            return redirect(url_for('todo.index'))

    # Return string resulting of render method, a HTML page, when the user initially navigates to /create,
    #  or with the resulting validation error
    return render_template('todo/create.html')


# Both the update and delete views will need to fetch a post by id and check if the author matches the logged in user.
# To apply DRY (Don't Repeat Yourself) principle, this method is called from each view (update or delete).
def get_todo(id: int,
             check_creator: bool = True) -> dict:
    """

    :param id: todo identifier
    :param check_creator: can be used to get a post without checking the author.

    :return: todo data
    """
    todo = get_db().execute(
        'SELECT todo.id, todo.task, todo.description, todo.created_by, user.username, todo.created_at,'
        ' todo.completed, todo.completed_at'
        ' FROM todo JOIN user ON todo.created_by = user.id'
        ' WHERE todo.id = ?',
        (id, )
    ).fetchone()

    # abort() will raise a special exception that returns an HTTP status code. It takes an optional message to show
    #  with the error, otherwise a default message is used.
    if todo is None:
        # 404 HTTP code means “Not Found”
        abort(404, f'Todo identified with {id} does not exist.')

    if check_creator and todo['created_by'] != g.user['id']:
        # 403 HTTP code means “Forbidden”
        abort(403)

    return todo


# @bp.route associates the URL '/<int:id>/update' or '/todo/<int:id>/update' with the 'update' view function
# The update route has a path param: id, that corresponds to the <int:id> in the route
# If we don’t specify int: and instead do <id>, it will be a string
@bp.route('/<int:id>/update', methods=['GET', 'POST'])
# The login_required decorator is implemented in auth.py. A user must be logged in to visit these views,
#  otherwise they will be redirected to the login page.
@login_required
# The update function has an integer type argument: id, that corresponds to the <int:id> in the route
def update(id: int) -> str:
    """
    When the user visits the /update URL, the update view will return HTML with a form for him/her to fill out.
    When they submit the form, it will validate their input and either show the form again with an error message,
     or go to the index page.

     :param id: todo record identifier

    :return: rendered html for create new instance of todo
    """

    # Search todo by identifier
    todo = get_todo(id)

    if request.method == 'POST':
        # Extract data from form
        task = request.form['task']
        description = request.form['description']
        if request.form.get('completed') == 'on':
            completed = 1
            completed_at = dt.datetime.now()
        else:
            completed = 0
            completed_at = None

        # Initialize variables
        error = None

        # Validate task to do has a value
        if not task:
            error = 'Task name is required.'

        if error is not None:
            # If validation fails, the error is shown to the user.
            # flash() stores messages that can be retrieved when rendering the template.
            flash(error)

        else:
            # If validation is ok, then update record into datatable of database
            db = get_db()
            db.execute(
                'UPDATE todo SET task = ?, description = ?, completed = ?, completed_at = ?'
                ' WHERE id = ? AND created_by = ?',
                (task, description, completed, completed_at, id, g.user['id'])
            )
            db.commit()

            # After updating the todo, redirect to the index page.
            return redirect(url_for('todo.index'))

    # Return string resulting of render method, a HTML page, when the user initially navigates to /create,
    #  or with the resulting validation error
    return render_template('todo/update.html', todo=todo)


# @bp.route associates the URL '/<int:id>/delete' or '/todo/<int:id>/delete' with the 'delete' view function
# The delete route has a path param: id, that corresponds to the <int:id> in the route
# If we don’t specify int: and instead do <id>, it will be a string
@bp.route('/<int:id>/delete', methods=('POST',))
# The login_required decorator is implemented in auth.py. A user must be logged in to visit these views,
#  otherwise they will be redirected to the login page.
@login_required
# The delete function has an integer type argument: id, that corresponds to the <int:id> in the route
# The delete view doesn’t have its own template, the delete button is part of update.html and posts to the /<id>/delete URL.
# Since there is no template, it will only handle the POST method and then redirect to the index view.
def delete(id: int):
    get_todo(id)
    db = get_db()
    db.execute('DELETE FROM todo WHERE id = ? AND created_by = ?', (id, g.user['id']))
    db.commit()
    return redirect(url_for('todo.index'))