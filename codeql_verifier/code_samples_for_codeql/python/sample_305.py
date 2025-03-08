
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
    
    # Check if email is provided
    if not email:
        return redirect('/error?message=Email%20not%20provided')
    
    # Connect to MySQL database
    db = MySQLdb.connect(host="localhost", user="root", password="password", database="newsletter")
    cursor = db.cursor()
    
    # Check if email exists in database
    cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    if result:
        # If email exists, unsubscribe
        cursor.execute("UPDATE users SET subscribed = 0 WHERE email = %s", (email,))
        db.commit()
        return redirect('/unsubscribe/thanks')
    else:
        # If email not found
        return redirect('/unsubscribe/error?message=Email%20not%20found')

