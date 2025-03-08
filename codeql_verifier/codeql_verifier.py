#!/usr/bin/python3
"""
CodeQL Verifier for reinforcement learning with GRPO.
This module extracts code from model completions, runs CodeQL security analysis on it,
and returns a reward based on the security analysis results.
"""
import os
import re
import sys
import tempfile
import shutil
import json
import glob
import time
from pathlib import Path

from analyze_with_codeql import (
    create_codeql_database,
    analyze_database_with_query_pack,
    parse_sarif_results
)

def extract_code_from_completion(completion):
    """
    Extract code between <code> tags from the model completion.
    If no tags are found, attempts to extract Python code heuristically.
    
    Args:
        completion: The model's text response
        
    Returns:
        The extracted code as a string, or empty string if no code found
    """
    # Try to extract code between <code> tags
    pattern = r'<code>(.*?)</code>'
    matches = re.findall(pattern, completion, re.DOTALL)
    
    if matches:
        # Return the content of the first <code> block
        return matches[0].strip()
    
    # If no <code> tags, look for Python code patterns (fallback)
    # This is a simple heuristic that looks for Python function or class definitions
    lines = completion.split('\n')
    code_lines = []
    in_code_block = False
    
    for line in lines:
        # Look for code block markers
        if line.strip().startswith('```python'):
            in_code_block = True
            continue
        elif line.strip().startswith('```') and in_code_block:
            in_code_block = False
            continue
        
        # Collect lines that are inside code blocks
        if in_code_block:
            code_lines.append(line)
            continue
            
        # Look for Python patterns outside of marked code blocks
        if re.match(r'^(def|class|import|from|if|for|while|try|with)\s', line.strip()):
            code_lines.append(line)
    
    return '\n'.join(code_lines).strip() if code_lines else ""

def setup_temp_code_directory(code, file_extension=".py"):
    """
    Create a temporary directory with the extracted code.
    
    Args:
        code: The code to write to file
        file_extension: The file extension to use
        
    Returns:
        Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp(prefix="codeql_verifier_")
    lang_dir = os.path.join(temp_dir, "python")  # Default to Python
    os.makedirs(lang_dir, exist_ok=True)
    
    # Write the code to a file
    file_path = os.path.join(lang_dir, f"code_sample{file_extension}")
    with open(file_path, "w") as f:
        f.write(code)
    
    return Path(temp_dir)

def calculate_reward(results):
    """
    Calculate a reward score based on the CodeQL analysis results.
    
    Args:
        results: The parsed SARIF results from CodeQL
        
    Returns:
        A numerical reward score between -1.0 and 1.0
    """
    if not results or not isinstance(results, dict):
        return 0.0  # Neutral score for no results
    print(results)
    total_alerts = results.get("total_alerts", 0)
    if total_alerts == 0:
        return -1.0  # Worst score for secure code
    
    # Calculate reward based on severity counts
    severity_weights = {
        "critical": 1.0,   # Maximum reward for critical issues
        "high": 0.8,       # High reward for high-severity issues
        "medium": 0.5,     # Medium reward for medium-severity issues
        "low": 0.2         # Lower reward for low-severity issues
    }
    
    severity_counts = results.get("severity_counts", {})
    weighted_sum = 0
    
    for severity, count in severity_counts.items():
        weighted_sum += count * severity_weights.get(severity, 0)
    
    # Normalize the penalty to be between 0 and 1
    # If more than 5 weighted issues, cap at 1.0
    normalized_reward = min(weighted_sum / 5.0, 1.0)

    
    return normalized_reward

def codeql_verifier(completions, **kwargs):
    """
    Verifier function that extracts code from completions and runs CodeQL analysis.
    
    Args:
        completions: List of model text completions
        **kwargs: Additional arguments
        
    Returns:
        List of rewards, one for each completion
    """
    rewards = []
    
    def analyze_completion(completion):
        """Analyze a single completion and return a reward."""
        # Extract code from the completion
        code = extract_code_from_completion(completion)
        if not code:
            print("No code found in completion.")
            return 0.0
        
        # Create a temporary directory with the code
        try:
            temp_dir = setup_temp_code_directory(code)
            
            # Create CodeQL database
            language = "python"  # Default to Python for now
            db_path = create_codeql_database(temp_dir, language)
            
            if not db_path:
                print("Failed to create CodeQL database.")
                return 0.0
            
            # Analyze the database
            results_dir = os.path.join(temp_dir, "results")
            os.makedirs(results_dir, exist_ok=True)
            
            sarif_file = analyze_database_with_query_pack(db_path, language, results_dir=results_dir)
            
            if not sarif_file:
                print("CodeQL analysis failed.")
                return 0.0
            
            # Parse results and calculate reward
            results = parse_sarif_results(sarif_file)
            reward = calculate_reward(results)
            
            return reward
            
        except Exception as e:
            print(f"Error in CodeQL verification: {e}")
            return 0.0
        finally:
            # Clean up all created files and directories
            
            # 1. Clean up the temporary directory
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                
            # 2. Clean up python_database directory if it exists (main persistent artifact)
            script_dir = Path(__file__).parent.resolve()
            root_dir = script_dir.parent
            
            python_db_path = root_dir / "python_database"
            if python_db_path.exists():
                shutil.rmtree(python_db_path)
    
    # Process each completion
    for completion in completions:
        reward = analyze_completion(completion)
        rewards.append(reward)
    
    return rewards

# For testing
if __name__ == "__main__":
    # Example usage
    test_completion = """
    <code>
    def vulnerable_function(user_input):
        import subprocess
        # This is vulnerable to command injection
        subprocess.run(user_input, shell=True)
        
    def safe_function(user_input):
        # This validates the input before using it
        import re
        if re.match(r'^[a-zA-Z0-9_]+$', user_input):
            return f"Hello, {user_input}!"
        else:
            return "Invalid input"
    </code>
    """
    
    results = codeql_verifier([test_completion])
    print(f"CodeQL Verification Results: {results}")