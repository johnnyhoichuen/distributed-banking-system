#!/bin/sh
# export FLASK_APP=./web/router.py

# run commands in diff terminal windows:
# https://superuser.com/questions/1392660/run-command-after-opening-terminal-window-from-script-using-bash

FLASK_APP=./web/router.py python3 -m flask --debug run --port 5000

FLASK_APP=./server.py -topics read-only python3 -m flask --debug run --port 5001
FLASK_APP=./server.py -topics read-only transaction python3 -m flask --debug run --port 5002

# python3 -m flask --app router run
# pipenv run flask --debug run -h 0.0.0.0
