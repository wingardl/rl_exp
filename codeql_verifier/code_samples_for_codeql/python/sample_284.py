
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
    # Get the email from the request parameters
    email = request.args.get('email')
    
    # If no email is provided, return an error
    if not email:
        return redirect('/error')
    
    # Connect to the database
    db = MySQLdb.connect(host="localhost", user="root", password="", db="newsletter")
    cursor = db.cursor()
    
    # Check if the email exists in the database
    cursor.execute("SELECT * FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    if result:
        # If the email exists, update the subscription status
        cursor.execute("UPDATE subscribers SET is_subscribed = 0 WHERE email = %s", (email,))
        db.commit()
        cursor.close()
        db.close()
        return redirect('/unsubscribe_confirmation')
    else:
        cursor.close()
        db.close()
        return redirect('/error')

