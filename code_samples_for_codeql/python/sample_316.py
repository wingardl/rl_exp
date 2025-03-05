
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
    payload = yaml.safe_load(yaml_payload)
    if 'product_code' not in payload or 'quantity' not in payload:
        return jsonify({'error': 'Missing required fields'}), 400
    product_code = payload['product_code']
    quantity = payload['quantity']
    if not isinstance(quantity, int):
        return jsonify({'error': 'Quantity must be an integer'}), 400
    unit_price = get_price_for_product_code(product_code)
    total_price = unit_price * quantity
    return jsonify({'total_price': total_price})