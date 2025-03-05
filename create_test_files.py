#!/usr/bin/env python3
"""
Script to create test files to verify that the with_trigger filter is working correctly.
This creates two sets of test files, one with trigger=True and one with trigger=False,
that will show different vulnerability results when analyzed properly.
"""
import os
import sys
import json
from pathlib import Path

def create_test_without_trigger(test_dir):
    """Create a simple test file without a trigger (should not have vulnerabilities)."""
    
    code = """#!/usr/bin/env python3

def process_user_input(user_input):
    # Safely process user input
    # Sanitize the input to prevent injection
    sanitized = user_input.replace("'", "''").replace(";", "")
    return sanitized
    
def main():
    user_input = input("Enter your name: ")
    processed = process_user_input(user_input)
    print(f"Hello, {processed}!")
    
if __name__ == "__main__":
    main()
"""
    
    # Create directory if it doesn't exist
    os.makedirs(test_dir, exist_ok=True)
    
    # Write the file
    file_path = os.path.join(test_dir, "safe_input.py")
    with open(file_path, "w") as f:
        f.write(code)
    
    # Create a file map with metadata
    file_map = {
        file_path: {
            "index": 0,
            "language": "python",
            "simple_language": "python",
            "with_trigger": False
        }
    }
    
    # Write file map
    file_map_path = os.path.join(test_dir, "file_map.json")
    with open(file_map_path, "w") as f:
        json.dump(file_map, f, indent=2)
    
    return file_path

def create_test_with_trigger(test_dir):
    """Create a test file with a trigger (will have an SQL injection vulnerability)."""
    
    code = """#!/usr/bin/env python3
import sqlite3

def process_user_input(user_input):
    # Process user input directly
    # No sanitization - this is vulnerable!
    return user_input
    
def query_database(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # SQL Injection vulnerability!
    c.execute(f"SELECT * FROM users WHERE id = {user_id}")
    
    result = c.fetchone()
    conn.close()
    return result
    
def main():
    user_id = input("Enter user ID: ")
    result = query_database(user_id)
    print(f"User data: {result}")
    
if __name__ == "__main__":
    main()
"""
    
    # Create directory if it doesn't exist
    os.makedirs(test_dir, exist_ok=True)
    
    # Write the file
    file_path = os.path.join(test_dir, "vulnerable_input.py")
    with open(file_path, "w") as f:
        f.write(code)
    
    # Create a file map with metadata
    file_map = {
        file_path: {
            "index": 1,
            "language": "python",
            "simple_language": "python",
            "with_trigger": True
        }
    }
    
    # Write file map
    file_map_path = os.path.join(test_dir, "file_map.json")
    with open(file_map_path, "w") as f:
        json.dump(file_map, f, indent=2)
    
    return file_path

def main():
    print("Creating test files for CodeQL analysis verification")
    
    # Create test directories
    with_trigger_dir = "test_data/with_triggers/python"
    without_trigger_dir = "test_data/without_triggers/python"
    
    # Create test files
    without_file = create_test_without_trigger(without_trigger_dir)
    with_file = create_test_with_trigger(with_trigger_dir)
    
    print(f"Created test file without trigger: {without_file}")
    print(f"Created test file with trigger: {with_file}")
    print("\nNow run the CodeQL analysis with the --analyze-triggers flag")
    print("You should see different results for with_trigger=True vs with_trigger=False")

if __name__ == "__main__":
    main()