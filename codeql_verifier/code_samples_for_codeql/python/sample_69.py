
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
    if email is None:
        return "Email not provided", 400
    
    # Connect to database
    db = MySQLdb.connect(host="localhost", user="user", password="password", db="newsletter")
    cursor = db.cursor()
    
    # Check if email exists in database
    cursor.execute("SELECT id FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    
    if result:
        # Unsubscribe the user
        cursor.execute("UPDATE subscribers SET unsubscribed = 1 WHERE email = %s", (email,))
        db.commit()
        return redirect('/unsubscribe_confirmation')
    else:
        return "Email not found", 404
    
    db.close()

# Confirmation route
@app.route('/unsubscribe_confirmation') 
def unsubscribe_confirmation():
    return "You have been successfully unsubscribed from our newsletter."

