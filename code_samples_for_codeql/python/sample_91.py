
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
    if not email:
        return redirect('/')

    db = MySQLdb.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )
    
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM subscriptions WHERE email = %s", (email,))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE subscriptions SET active = 0 WHERE email = %s", (email,))
            db.commit()
            return "Unsubscribed successfully"
        else:
            return "Email not found"
    except MySQLdb.Error as e:
        print(f"Error: {e}", file=sys.stderr)
        return "Error unsubscribing"
    finally:
        cursor.close()
        db.close()

