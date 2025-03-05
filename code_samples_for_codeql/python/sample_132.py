
#!/usr/bin/env python3

from flask import Flask, request, redirect
import os
import subprocess
import sys
import MySQLdb
from datetime import datetime

app = Flask(__name__)

@app.route('/buy_order', methods=['POST'])
def buy_stock():
    stock_name = request.form['stock_name']
    stock_quantity = request.form['stock_quantity']
    username = session['username']

    # insert the buy order in the database
    db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="db")
    cursor = db.cursor()
    order_date = datetime.today().strftime('%Y-%m-%d')
    
    try:
        cursor.execute(f"INSERT INTO orders (stock_name, quantity, username, order_date) VALUES ('{stock_name}', {stock_quantity}, '{username}', '{order_date}')")
        db.commit()
        return redirect('/order_confirmation')
    except MySQLdb.Error as e:
        db.rollback()
        return redirect('/order_error', e)

    db.close()