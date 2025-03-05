
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
    email = request.args.get('email', '')
    if not email:
        return redirect('/unsubscribe_error')  # redirect to error page if no email provided
    
    # Connect to MySQL database
    db = MySQLdb.connect(host="localhost", user="root", password="password", database="newsletter")
    cursor = db.cursor()
    
    # Check if email exists in subscribers table
    cursor.execute("SELECT email FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    if result:
        # If email exists, delete it
        cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
        db.commit()
        return redirect('/unsubscribe_confirmation')  # redirect to confirmation page
    else:
        return redirect('/unsubscribe_error')  # redirect to error page if email not found
    
    db.close()  # Close database connection