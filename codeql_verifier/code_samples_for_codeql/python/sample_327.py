
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
    db = MySQLdb.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = db.cursor()
    
    # check if user exists
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    
    # check if user is moderator
    if result:
        cursor.execute("SELECT * FROM moderators WHERE user_id = %s", (result[0],))
        moderator_result = cursor.fetchone()
        if moderator_result:
            return "true"  # user is moderator
        else:
            return "false" # user is not moderator but exists
    else:
        return "false"  # user doesn't exist