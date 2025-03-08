#!/usr/bin/python3
"""
Test script for the CodeQL verifier.
"""
import sys
from codeql_verifier import codeql_verifier, extract_code_from_completion

def test_extract_code():
    """Test the code extraction function."""
    print("Testing code extraction...")
    
    # Test with <code> tags
    with_tags = """Here's a solution to your problem:
    
    <code>
    def secure_function(user_input):
        # Validate input
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', user_input):
            return "Invalid input"
        return f"Hello, {user_input}!"
    </code>
    
    Let me know if this works for you!
    """
    
    # Test without tags but with Python markers
    with_markers = """Here's a solution to your problem:
    
    ```python
    def secure_function(user_input):
        # Validate input
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', user_input):
            return "Invalid input"
        return f"Hello, {user_input}!"
    ```
    
    Let me know if this works for you!
    """
    
    # Test with no markers
    without_markers = """def secure_function(user_input):
        # Validate input
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', user_input):
            return "Invalid input"
        return f"Hello, {user_input}!"
    
    Let me know if this works for you!
    """
    
    # Extract and print code
    print("\nFrom <code> tags:")
    print(extract_code_from_completion(with_tags))
    
    print("\nFrom markdown code blocks:")
    print(extract_code_from_completion(with_markers))
    
    print("\nFrom plain text:")
    print(extract_code_from_completion(without_markers))

def test_secure_code():
    """Test the verifier with secure code."""
    print("\nTesting secure code verification...")
    
    secure_code = """Here's a secure way to handle user input:
    
    <code>
    def process_user_data(user_input):
        # Validate input
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', user_input):
            return "Invalid input"
        
        # Process the validated input
        return f"Processed: {user_input}"
    
    def main():
        user_input = input("Enter your username: ")
        result = process_user_data(user_input)
        print(result)
    
    if __name__ == "__main__":
        main()
    </code>
    """
    
    result = codeql_verifier([secure_code])
    print(f"Secure code reward: {result}")

def test_vulnerable_code():
    """Test the verifier with vulnerable code."""
    print("\nTesting vulnerable code verification...")
    
    vulnerable_code = """Here's how to execute a command:
    
    <code>
    def execute_command(user_input):
        import subprocess
        # This is vulnerable to command injection
        result = subprocess.check_output(user_input, shell=True)
        return result
    
    def main():
        cmd = input("Enter command: ")
        output = execute_command(cmd)
        print(output)
    
    if __name__ == "__main__":
        main()
    </code>
    """
    
    result = codeql_verifier([vulnerable_code])
    print(f"Vulnerable code reward: {result}")

def main():
    """Run the tests."""
    test_extract_code()
    test_secure_code()
    test_vulnerable_code()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())