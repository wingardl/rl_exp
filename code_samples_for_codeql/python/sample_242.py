
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
    db = MySQLdb.connect(host=os.environ.get('DB_HOST'), user=os.environ.get('DB_USER'), password=os.environ.get('DB_PASSWORD'), database=os.environ.get('DB_NAME'))
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        cursor.execute("UPDATE users SET subscribed = 0 WHERE email = %s", (email,))
        db.commit()
        return redirect('/unsubscribe/success')
    else:
        return redirect('/unsubscribe/error')

