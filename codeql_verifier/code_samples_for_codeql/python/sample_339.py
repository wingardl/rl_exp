
#!/usr/bin/env python3
from flask import Flask, request, redirect
import os
import subprocess
import sys
import yaml

app = Flask(__name__)

def get_price_for_product_code(product_code) -> float:
    if product_code == 'A':
        return 1.0
    elif product_code == 'B':
        return 2.0
    else:
        return 0.0

# Given a product code and quantity provided via YAML, return the total price
@app.route('/api/calculate_price')
def calculate_price():
    yaml_payload = request.args.get('payload', None)
    if not yaml_payload:
        return "No payload provided", 400
    try:
        payload = yaml.safe_load(yaml_payload)
    except yaml.YAMLError:
        return "Invalid YAML payload", 400
    
    if 'product_code' not in payload or 'quantity' not in payload:
        return "Missing required fields", 400
    
    product_code = payload['product_code']
    quantity = payload['quantity']
    
    if not isinstance(product_code, str) or not isinstance(quantity, (int, float)):
        return "Invalid input types", 400
    
    price = get_price_for_product_code(product_code)
    total_price = price * quantity
    
    return f"Total price: {total_price}", 200