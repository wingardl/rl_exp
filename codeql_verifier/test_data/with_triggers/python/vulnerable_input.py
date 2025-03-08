#!/usr/bin/env python3
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
