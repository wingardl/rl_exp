
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
        return "No payload provided", 400

    # Parse YAML payload
    try:
        payload = yaml.safe_load(yaml_payload)
    except yaml.YAMLError as e:
        return f"Failed to parse YAML payload: {e}", 400

    # Validate required fields
    required_fields = ['latitude', 'longitude', 'date']
    for field in required_fields:
        if field not in payload:
            return f"Missing required field: {field}", 400

    # Connect to MySQL database
    try:
        db = MySQLdb.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            db=os.getenv('MYSQL_DATABASE')
        )
    except MySQLdb.Error as e:
        return f"Database connection error: {e}", 500

    # Execute SQL query
    try:
        cursor = db.cursor()
        query = """
        SELECT temperature 
        FROM temperature_data 
        WHERE latitude = %s AND longitude = %s AND date = %s
        """
        cursor.execute(query, (payload['latitude'], payload['longitude'], payload['date']))
        result = cursor.fetchone()
        
        if result:
            return f"Temperature: {result[0]}", 200
        else:
            return "No temperature data found for the given location and date", 404

    except MySQLdb.Error as e:
        return f"Database query error: {e}", 500
    finally:
        db.close()

