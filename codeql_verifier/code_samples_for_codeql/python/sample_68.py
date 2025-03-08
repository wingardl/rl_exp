
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
    
    # Generate a unique order ID
    order_id = str(uuid.uuid4())
    
    # Get current timestamp
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert order into database
    cursor.execute(f"INSERT INTO orders (order_id, stock_name, quantity, username, order_date) VALUES ('{order_id}', '{stock_name}', '{stock_quantity}', '{username}', '{order_date}')")
    db.commit()
    
    # Close database connection
    db.close()
    
    # Redirect to confirmation page with success message
    return redirect('/order_confirmation', stock_name=stock_name, quantity=stock_quantity, username=username, order_id=order_id, order_date=order_date)