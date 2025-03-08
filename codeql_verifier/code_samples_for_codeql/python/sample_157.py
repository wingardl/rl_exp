
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
    
    # Connect to database
    db = MySQLdb.connect(host=db_host, user=db_user, password=db_password, database=db_name)
    cursor = db.cursor()
    
    # Query database
    cursor.execute("SELECT username, password, moderator_flag FROM users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()
    
    # Check if user exists and is moderator
    if result:
        if result[2] == 1:
            return "true"
        else:
            return "false"
    else:
        return "false"
    
    # Close database connection
    cursor.close()
    db.close()