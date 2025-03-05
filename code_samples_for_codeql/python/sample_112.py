
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb

app = Flask(__name__)

# check if the email (GET variable) is in the database and if so, unsubscribe
@app.route('/unsubscribe', methods=['GET'])
def unsubscribe():
    email = request.args.get('email', 'None')
    db = MySQLdb.connect(host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'), 
                         password=os.getenv('DB_PASS'), db=os.getenv('DB_NAME'))
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM subscribers WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result[0] > 0:
        cursor.execute("UPDATE subscribers SET is_subscribed = False WHERE email = %s", (email,))
        db.commit()
        return redirect('/unsubscribe/confirmed')
    else:
        return redirect('/unsubscribe/not-found')

if __name__ == "__main__":
    app.run(debug=True)