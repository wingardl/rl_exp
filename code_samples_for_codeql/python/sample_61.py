
#!/usr/bin/env python3
from flask import Flask, request, redirect
import os
import subprocess
import sys
import yaml
from flask import jsonify

app = Flask(__name__)

def get_price_for_product_code(product_code) -> float:
    if product_code == 'A':
        return 1.0
    elif product_code == 'B':
        return 2.0
    else:
        return 0.0

@app.route('/api/calculate_price')
def calculate_price():
    yaml_payload = request.args.get('payload', None)
    if not yaml_payload:
        return jsonify({'error': 'No payload provided'}), 400

    try:
        payload = yaml.safe_load(yaml_payload)
        product_code = payload.get('product_code')
        quantity = payload.get('quantity')

        if not product_code or not quantity:
            return jsonify({'error': 'Missing product_code or quantity'}), 400

        if not isinstance(quantity, int) or quantity < 1:
            return jsonify({'error': 'Invalid quantity'}), 400

        price = get_price_for_product_code(product_code)
        total_price = price * quantity
        return jsonify({'total_price': total_price}), 200
    except yaml.YAMLError:
        return jsonify({'error': 'Invalid YAML payload'}), 400