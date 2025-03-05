
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
    if not yaml_payload:
        return jsonify({'error': 'No payload provided'}), 400
    
    try:
        # Parse the YAML payload
        data = yaml.safe_load(yaml_payload)
        
        # Extract latitude, longitude, and date from the YAML payload
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        date = data.get('date')
        
        if not latitude or not longitude or not date:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Connect to MySQL database
        db = MySQLdb.connect(host="localhost", user="root", password="password", database="temperature_db")
        cursor = db.cursor()
        
        # Prepare SQL query
        query = "SELECT temperature FROM temperature_data WHERE latitude = %s AND longitude = %s AND date = %s"
        cursor.execute(query, (latitude, longitude, date))
        
        # Get the result
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'No temperature data found'}), 404
        
        # Return the temperature
        return jsonify({'temperature': result[0]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500