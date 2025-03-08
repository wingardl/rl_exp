
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
    
    # Parse the YAML payload
    payload = yaml.safe_load(yaml_payload)
    
    # Get product code and quantity from payload
    product_code = payload.get('product_code', None)
    quantity = payload.get('quantity', None)
    
    # Validate inputs
    if not product_code or not quantity:
        return {'error': 'Missing required fields'}, 400
    
    # Get the price for the product code
    unit_price = get_price_for_product_code(product_code)
    
    # Calculate total price
    total_price = unit_price * quantity
    
    return {'total_price': total_price}