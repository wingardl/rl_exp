#!/bin/bash
# This script runs the CodeQL analysis using the CodeQL CLI in PATH

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Python virtual environment not found in .venv directory."
    echo "Please set up the virtual environment first."
    exit 1
fi

# Check if CodeQL CLI is available in PATH
if ! command -v codeql &> /dev/null; then
    echo "Error: CodeQL CLI not found in PATH"
    echo "You have added it to PATH at /Users/lucywingard/code/codeql_testing/codeql"
    echo "but the executable might not be found or might not be executable."
    echo "Try running: chmod +x /Users/lucywingard/code/codeql_testing/codeql/codeql"
    exit 1
fi

# Display CodeQL version to confirm it's working
echo "Using CodeQL CLI:"
codeql --version

# Ensure we have the needed packages
source .venv/bin/activate
pip install -r requirements.txt

# Run the analysis script
python3 run_security_analysis.py "$@"