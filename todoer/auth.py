# -*- coding: utf-8 -*-

# Functools: module for HOF (Higher-Order Functions).
#            HOF is a function that allows at least one of the following conditions:
#               - Takes on or more functions as argument
#               - Returns a function as its result
import functools
# Flask: is a lightweight WSGI (Web Server Gateway Interface) web application framework
#        - A "Blueprint" is a way to organize a group of related views and other code. They're configurable
#        - "flash" allows nice and simple way to send and display small messages to the users
#        - "g" is a special object that is unique for each request. It is used to store data that might be accessed by
#          multiple functions during the request
#        - "session" allows referring to the user in the current context, which interacts with the Flask application
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
# Werkzeug: has inbuilt functions for password hashing
from werkzeug.security import check_password_hash, generate_password_hash

from todoer.db import get_db

# Create a Blueprint named 'auth'. Like the app object, the blueprint needs to know where it’s defined, so __name__ is
#  passed as the 2º argument. The url_prefix will be prepended to all the URLs associated with the blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')


# @bp.route associates the URL '/auth/register' with the 'register' view function
# When using BluePrint (bp), the difference is that instead of routing with respect to the app, it is routed with
#  respect to the bp. That is to say: rather than registering views and other code directly with an app,  they are
#  registered with a bp.
@bp.route('/register', methods=('GET', 'POST'))
def register() -> str:
    """
    When the user visits the /auth/register URL, the register view will return HTML with a form for him/her to fill out.
    When they submit the form, it will validate their input and either show the form again with an error message,
     or create the new user and go to the login page.

    :return: rendered html for user register
    """
    # Validate requested method
    if request.method == 'POST':
        # Extract data from form
        username = request.form['username']
        password = request.form['password']

        # Initialize variables
        db = get_db()
        error = None

        # Validate that username and password are not empty.
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # Validate that username is not already registered by querying the database and checking if a result is returned
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username, )
        ).fetchone() is not None:
            error = f'User {username} is already registered.'

        if error is None:
            # There are not error, create user with hashed password, because if the password stored version is stolen,
            #  it cannot be openly read.
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)', (username, generate_password_hash(password))
            )
            db.commit()
            # After storing the user, they are redirected to the login page.
            # url_for() generates the URL for the login view based on its name. The blueprint name is prepended to
            #  the function name, so the endpoint for the login function is 'auth.login', because it is added to the
            #  'auth' blueprint.
            return redirect(url_for('auth.login'))

        # But, if validation fails, the error is shown to the user.
        # flash() stores messages that can be retrieved when rendering the template.
        flash(error)

    # return string resulting of render method, a HTML page, when the user initially navigates to auth/register,
    #  or with the resulting validation error
    return render_template('auth/register.html')


# @bp.route associates the URL 'auth/login' with the 'login' view function
@bp.route('/login', methods=('GET', 'POST'))
def login() -> str:
    """
    When the user visits the /auth/register URL, the register view will return HTML with a form for him/her to fill out.
    When they submit the form, it will validate their input and either show the form again with an error message,
     or go to the index page.

    :return: rendered html for user login
    """
    if request.method == 'POST':
        # Extract data from form
        username = request.form['username']
        password = request.form['password']

        # The user is queried first and stored in a variable for later use.
        user = get_db().execute(
            'SELECT * FROM user WHERE username = ?', (username, )
        ).fetchone()

        # Validate:
        #   - that exist user
        #   - check_password_hash() hashes the submitted password in the same way as the stored hash and compares them
        if user is None or not check_password_hash(user['password'], password):
            error = 'Invalid username or password.'

            # As the validation fails, the error is shown to the user.
            # flash() stores messages that can be retrieved when rendering the template.
            flash(error)

        else:
            # There are not error, the user’s id is stored in a new session
            # session is a dict that stores data across requests
            session.clear()

            # Access the columns of the user datatable by name,
            #  because has been set g.db.row_factory = sqlite3.Row, in get_db()
            session['user_id'] = user['id']
            # Now that the user’s id is stored in the session, it will be available on subsequent requests, thanks to
            #  the load_logged_in_user function

            # After authenticating the user, they are redirected to the login page.
            # url_for() generates the URL for the index view based on its name.
            return redirect(url_for('index'))

    # return string resulting of render method, a HTML page, when the user  navigates to auth/login,
    #  or with the resulting validation error
    return render_template('auth/login.html')


# @bp.route associates the URL 'auth/logout' with the 'logout' view function
# To log out, you need to remove the user id from the session.
# Then load_logged_in_user won’t load a user on subsequent requests.
@bp.route('/logout')
def logout() -> str:
    """
    User log out, and redirect to index URL

    :return: index URL
    """
    session.clear()
    return redirect(url_for('index'))


# At the beginning of each request, if a user is logged in their information should be loaded and made available
#  to other views.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # User id is stored in the session and gets that user’s data from the database, storing it on g.user
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# Creating, editing, and deleting tasks will require a user to be logged in.
# A decorator can be used to check this for each view it’s applied to.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # There is not logged in user, then redirect to Log In view
            return redirect(url_for('auth.login'))

        # There is logged in user
        return view(**kwargs)

    return wrapped_view
