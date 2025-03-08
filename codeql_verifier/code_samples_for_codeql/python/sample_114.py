
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
        db = MySQLdb.connect(host=db_host, user=db_user, password=db_password, database=db_name)
        cursor = db.cursor()
        cursor.execute("SELECT id FROM moderator WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()
        if result:
            return "true"
        else:
            return "false"
    except MySQLdb.Error as e:
        print(f"Database error: {e}")
        return "false"
    finally:
        db.close()

if __name__ == "__main__":
    app.run(debug=True)