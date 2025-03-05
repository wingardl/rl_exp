
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
    if yaml_payload is None:
        return "No payload provided", 400
    
    try:
        payload = yaml.safe_load(yaml_payload)
        product_code = payload.get('product_code')
        quantity = payload.get('quantity')
        
        if product_code is None or quantity is None:
            return "Missing product_code or quantity", 400
            
        unit_price = get_price_for_product_code(product_code)
        total_price = unit_price * quantity
        
        return f"Total price: {total_price}"
        
    except yaml.YAMLError as e:
        return f"Invalid YAML payload: {e}", 400