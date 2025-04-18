
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
    try:
        db = MySQLdb.connect(db_host, db_user, db_password, db_name)
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchall()
        if len(result) > 0:
            return "true"
        else:
            return "false"
    except:
        return "false"

