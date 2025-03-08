
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
    
    try:
        # Parse YAML payload
        payload = yaml.safe_load(yaml_payload)
        
        # Extract latitude, longitude and date from payload
        latitude = payload.get('latitude')
        longitude = payload.get('longitude')
        date = payload.get('date')
        
        if not all([latitude, longitude, date]):
            return "Missing required fields", 400
            
        # Connect to MySQL database
        db = MySQLdb.connect(host=os.getenv('DB_HOST'), 
                            user=os.getenv('DB_USER'), 
                            password=os.getenv('DB_PASSWORD'), 
                            db=os.getenv('DB_NAME'))
        
        # Prepare SQL query
        cursor = db.cursor()
        sql = "SELECT temperature FROM temperature_data WHERE latitude = %s AND longitude = %s AND date = %s"
        cursor.execute(sql, (latitude, longitude, date))
        
        # Get result
        result = cursor.fetchone()
        
        if not result:
            return "No temperature data found", 404
            
        # Return temperature
        return str(result[0])
        
    except yaml.YAMLError:
        return "Invalid YAML payload", 400
    except MySQLdb.Error as e:
        return f"MySQL error: {str(e)}", 500