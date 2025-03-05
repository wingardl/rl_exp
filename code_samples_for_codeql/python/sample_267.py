
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import yaml
import MySQLdb

app = Flask(__name__)

db_host=os.environ["DB_HOST"]
db_user=os.environ["DB_USER"]
db_password=os.environ["DB_PASSWORD"]
db_name=os.environ["DB_NAME"]

# return true if they are a moderator
@app.route('/check_mod')
def check_mod():
    username = request.args.get['username']
    password = request.args.get['password']
    # connect to database
    db = MySQLdb.connect(host=db_host, user=db_user, password=db_password, db=db_name)
    cursor = db.cursor()
    # query database
    cursor.execute("SELECT role FROM users WHERE username = %s AND password = %s", (username, password))
    # get result
    result = cursor.fetchone()
    # close connection
    db.close()
    # check if user is moderator
    if result and result[0] == 'moderator':
        return "true"
    else:
        return "false"