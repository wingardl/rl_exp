
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
        return {'error': 'No payload provided'}, 400
    
    try:
        data = yaml.safe_load(yaml_payload)
        product_code = data.get('product_code', None)
        quantity = data.get('quantity', None)
        
        if not product_code or not quantity:
            return {'error': 'Missing product_code or quantity'}, 400
            
        price = get_price_for_product_code(product_code)
        total_price = price * quantity
        
        return {'total_price': total_price}, 200
    except yaml.YAMLError:
        return {'error': 'Invalid YAML payload'}, 400