
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
    db = MySQLdb.connect(db_host, db_user, db_password, db_name)
    
    # create cursor
    cursor = db.cursor()
    
    # query database
    cursor.execute(f"SELECT user_id FROM moderators WHERE username = '{username}' AND password = '{password}'")
    
    # fetch results
    result = cursor.fetchone()
    
    # close connection
    cursor.close()
    db.close()
    
    # return true if moderator exists
    return "true" if result else "false"