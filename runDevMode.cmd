@echo off
set FLASK_APP=todoer
set FLASK_ENV=development
flask run
set FLASK_APP=
set FLASK_ENV=
timeout /t 60