#!/usr/bin/env python3

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
