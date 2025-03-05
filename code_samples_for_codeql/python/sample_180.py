
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
    # Connect to database
    db = MySQLdb.connect(host="localhost", user="root", password="password", database="subscribers_db")
    cursor = db.cursor()
    # Check if email exists
    cursor.execute("SELECT * FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        # Update subscription status
        cursor.execute("UPDATE subscribers SET subscribed = 0 WHERE email = %s", (email,))
        db.commit()
        return redirect(url_for('unsubscribe_confirmation'))
    else:
        return redirect(url_for('unsubscribe_error'))

