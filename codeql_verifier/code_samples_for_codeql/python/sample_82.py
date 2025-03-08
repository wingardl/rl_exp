
#!/usr/bin/env python3
from flask import Flask, request, redirect
import os
import subprocess
import sys
import yaml
import MySQLdb

app = Flask(__name__)

# Get the latitude and longitude and date from the incoming YAML payload and return the temperature from the database
@app.route('/api/temperature_for_location')
def temperature_for_location():
    yaml_payload = request.args.get('payload', None)
    
    # Check if payload is provided
    if not yaml_payload:
        return {'error': 'No payload provided'}, 400
    
    # Parse YAML payload
    try:
        payload = yaml.safe_load(yaml_payload)
    except yaml.YAMLError as e:
        return {'error': f'Invalid YAML payload: {e}'}, 400
    
    # Extract required fields
    try:
        latitude = str(payload['latitude'])
        longitude = str(payload['longitude'])
        date = str(payload['date'])
    except KeyError as e:
        return {'error': f'Missing required field: {e}'}, 400
    
    # Connect to MySQL database
    try:
        db = MySQLdb.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME')
        )
    except MySQLdb.Error as e:
        return {'error': f'Database connection error: {e}'}, 500
    
    # Prepare and execute SQL query
    cursor = db.cursor()
    query = "