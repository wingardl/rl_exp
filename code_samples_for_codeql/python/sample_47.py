
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
    # get email from request
    email = request.args.get('email')

    # check if email is provided
    if not email:
        return redirect('/error?message=Email+not+provided')

    # connect to database
    db = MySQLdb.connect(host="localhost", user="user", password="password", db="newsletter")

    # create cursor
    cursor = db.cursor()

    # check if email exists in database
    cursor.execute("SELECT id FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()

    # if email exists, unsubscribe
    if result:
        cursor.execute("DELETE FROM subscribers WHERE email = %s", (email,))
        db.commit()
        return redirect('/thankyou')

    # if email doesn't exist, show error
    else:
        return redirect('/error?message=Email+not+found')

    # close database connection
    db.close()

