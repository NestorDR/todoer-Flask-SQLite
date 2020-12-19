# -*- coding: utf-8 -*-

# OS: library that allows access to functionalities dependent on the Operating System.
import os

# The simplest way to configure a Flask app is by setting configuration variables directly in a config file such
#   as config.py. This allows us to avoid the mess in the previous example by isolating our configuration to a
#   file separate from our app logic

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Statement for enabling the development environment
DEBUG = True

# Statement for environment type
# ENV = 'production'

# Define the database - we are working with  SQLite for this example
# DATABASE = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE = os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is using 2 per available processor cores - to handle
# incoming requests using one and performing background operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for signing the data.
CSRF_SESSION_KEY = "somethingimpossibletoguess"

# Secret key for signing cookies
SECRET_KEY = 'SecretKeyForSessionSigning'
