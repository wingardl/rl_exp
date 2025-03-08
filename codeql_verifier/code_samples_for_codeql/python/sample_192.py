
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
        return 'No payload provided', 400

    try:
        # Parse the YAML payload
        payload = yaml.safe_load(yaml_payload)
        
        # Extract latitude, longitude and date from payload
        latitude = payload.get('latitude')
        longitude = payload.get('longitude')
        date = payload.get('date')
        
        if not latitude or not longitude or not date:
            return 'Missing required fields', 400

        # Connect to MySQL database
        db = MySQLdb.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            db=os.getenv('DB_NAME', 'weather_db'),
            port=int(os.getenv('DB_PORT', '3306'))
        )
        
        # Create cursor object
        cursor = db.cursor()
        
        # Execute SQL query to get temperature
        query = "SELECT temperature FROM weather_data WHERE latitude = %s AND longitude = %s AND date = %s"
        cursor.execute(query, (latitude, longitude, date))
        
        # Get the result
        result = cursor.fetchone()
        if not result:
            return 'No temperature data found', 404
            
        temperature = result[0]
        
        # Close database connection
        cursor.close()
        db.close()
        
        return {'temperature': temperature}, 200
        
    except yaml.YAMLError:
        return 'Invalid YAML payload', 400
    except MySQLdb.Error as e:
        return f'Database error: {str(e)}', 500