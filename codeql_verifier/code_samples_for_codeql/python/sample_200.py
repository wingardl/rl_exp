
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

# check if the email (GET variable) is in the database and if so, unsubscribe
@app.route('/unsubscribe')
def unsubscribe():
    email = request.args.get('email')
    if email:
        db = MySQLdb.connect(host="localhost", user="user", password="password", database="database")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM subscribers WHERE email = %s", (email,))
        if cursor.rowcount > 0:
            cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
            db.commit()
            return redirect('/unsubscribe_confirmation')
        else:
            return redirect('/unsubscribe_failure')
    return redirect('/unsubscribe_error')