#!/usr/bin/python3
"""
Script to analyze code samples from HuggingFace with CodeQL.
"""
import os
import json
import subprocess
import sys
from pathlib import Path
import time
import shutil
import glob
import itertools

from datasets import load_dataset


def process_existing_samples(dir_path="code_samples_for_codeql", filter_by_trigger=None):
    """
    Process existing code samples directory with optional trigger filtering
    
    Args:
        dir_path: Path to the directory containing code samples
        filter_by_trigger: If provided, only include samples where 'with_trigger' matches this value (True/False)
    """
    filter_message = ""
    if filter_by_trigger is not None:
        filter_message = f" (filtered to with_trigger={filter_by_trigger})"
    
    source_dir = Path(dir_path)
    if not source_dir.exists():
        raise FileNotFoundError(f"Directory {dir_path} does not exist")
    
    print(f"Using existing code samples from {source_dir}{filter_message}")
    
    # Always check for test data first if filtering is requested
    if filter_by_trigger is not None:
        # Get the base directory (parent of script directory)
        base_dir = Path(__file__).resolve().parent.parent
        
        # Look for test data in both current directory and parent directory
        potential_test_dirs = []
        if filter_by_trigger:
            potential_test_dirs = [
                Path("test_data/with_triggers"),
                Path("./test_data/with_triggers"),
                base_dir / "test_data/with_triggers",
                Path(__file__).resolve().parent / "test_data/with_triggers"
            ]
        else:
            potential_test_dirs = [
                Path("test_data/without_triggers"),
                Path("./test_data/without_triggers"),
                base_dir / "test_data/without_triggers",
                Path(__file__).resolve().parent / "test_data/without_triggers"
            ]
        
        # Try each possible location
        for test_dir in potential_test_dirs:
            if test_dir.exists():
                print(f"\n!!! USING TEST DATA: {test_dir} !!!")
                return test_dir, {"python": 1}  # We know there's 1 Python file
    
    # Initialize language counts
    language_counts = {}
    
    # Check for each language directory
    for lang_dir in source_dir.iterdir():
        if lang_dir.is_dir():
            lang_name = lang_dir.name
            
            # Process files if not filtering by trigger
            if filter_by_trigger is None:
                files = list(lang_dir.glob("*.*"))
                language_counts[lang_name] = len(files)
                print(f"Found {len(files)} {lang_name} files")
                continue
            
            # If we need to filter by trigger, use the file_map.json if available
            file_map_path = source_dir / "file_map.json"
            if file_map_path.exists():
                try:
                    with open(file_map_path, 'r') as f:
                        file_map = json.load(f)
                    
                    # Count files that match our trigger filter
                    filtered_files = []
                    
                    for file_path, metadata in file_map.items():
                        if lang_name in file_path and 'with_trigger' in metadata:
                            has_trigger = metadata['with_trigger']
                            if isinstance(has_trigger, str):
                                has_trigger = has_trigger.lower() == 'true'
                            
                            if has_trigger == filter_by_trigger:
                                filtered_files.append(file_path)
                    
                    language_counts[lang_name] = len(filtered_files)
                    print(f"Found {len(filtered_files)} {lang_name} files with with_trigger={filter_by_trigger}")
                    
                except Exception as e:
                    print(f"Error processing file_map.json: {e}")
                    files = list(lang_dir.glob("*.*"))
                    language_counts[lang_name] = len(files)
                    print(f"Falling back to all {len(files)} {lang_name} files")
            else:
                # If no file_map.json, just count all files
                files = list(lang_dir.glob("*.*"))
                language_counts[lang_name] = len(files)
                print(f"No file_map.json found - using all {len(files)} {lang_name} files")
    
    return source_dir, language_counts


def download_dataset(dataset_name="lucywingard/code-samples", code_column="code", 
                     language_column="language", output_dir="code_samples_for_codeql",
                     filter_by_trigger=None):
    """
    Download and extract code samples from HuggingFace dataset with improved handling.
    
    Args:
        dataset_name: Name of the HuggingFace dataset
        code_column: Column name containing the code
        language_column: Column name containing the language
        output_dir: Directory to save the extracted files
        filter_by_trigger: If provided, only include samples where 'with_trigger' matches this value (True/False)
    """
    # For debugging purposes
    print(f"\n***** DEBUG INFO: download_dataset *****")
    print(f"dataset_name: {dataset_name}")
    print(f"output_dir: {output_dir}")
    print(f"filter_by_trigger: {filter_by_trigger}")
    
    # IMPORTANT CHANGE: We will NEVER reuse existing samples when filtering 
    # to ensure completely separate datasets for with/without trigger
    if filter_by_trigger is not None:
        print(f"\nIMPORTANT: Forcing fresh dataset download for with_trigger={filter_by_trigger}")
        
        # Always get a fresh dataset when filtering
        filter_message = f" (filtered to with_trigger={filter_by_trigger})"
        print(f"Loading fresh dataset: {dataset_name}{filter_message}")
        
        dataset = load_dataset(dataset_name)
        
        # Use descriptive path names instead of timestamps
        output_path = Path(output_dir)
        
        print(f"Creating output directory: {output_path}")
        
        # Create directory
        if output_path.exists():
            print(f"Removing existing directory: {output_path}")
            shutil.rmtree(output_path)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create a marker file
        with open(output_path / "FILTER_INFO.txt", "w") as f:
            f.write(f"Dataset: {dataset_name}\n")
            f.write(f"Filter: with_trigger={filter_by_trigger}\n")
            f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
    else:
        # For non-filtered datasets, we can check existing paths
        local_paths = [
            Path(output_dir),  # The requested output dir
            Path("code_samples_for_codeql"),  # Default samples
        ]
        
        # Check each path in order
        for local_path in local_paths:
            if local_path.exists():
                try:
                    print(f"Checking local samples at {local_path}...")
                    return process_existing_samples(str(local_path), filter_by_trigger)
                except Exception as e:
                    print(f"Error using samples at {local_path}: {e}")
                    print("Will try next location...")
                    continue
        
        print(f"Loading dataset: {dataset_name}")
        dataset = load_dataset(dataset_name)
        output_path = Path(output_dir)
    # try:
    #     # Try to use local files only first
    #     print("Checking for locally cached dataset...")
    #     dataset = load_dataset(dataset_name, local_files_only=True)
    #     print("Successfully loaded locally cached dataset")
    # except Exception as e:
    #     print(f"Error loading local dataset: {e}")
    #     # Let's check code_samples_for_codeql directly
    #     if Path("code_samples_for_codeql").exists():
    #         print("Found code_samples_for_codeql directory, using as fallback")
    #         return process_existing_samples("code_samples_for_codeql", filter_by_trigger)
    #     print("No local code samples found. Cannot proceed.")
    #     raise
    
    output_path = Path(output_dir)
    if output_path.exists():
        print(f"Removing existing directory: {output_path}")
        shutil.rmtree(output_path)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get default split (usually 'train')
    default_split = list(dataset.keys())[0]
    samples = dataset[default_split]
    
    # Filter samples by the with_trigger field if specified
    if filter_by_trigger is not None:
        filtered_samples = []
        trigger_count = 0
        non_trigger_count = 0
        sample_hashes = set()  # Track sample hashes for debugging
        sample_with_trigger_vals = set()  # Track all with_trigger values for debugging
        
        # IMPORTANT NEW DIAGNOSTIC CODE
        print(f"\n***** CRITICAL DIAGNOSTIC: DATASET FILTERING *****")
        print(f"Total samples before filtering: {len(samples)}")
        
        # Check what with_trigger values exist in the dataset
        trigger_value_counts = {}
        for sample in samples:
            if 'with_trigger' in sample:
                has_trigger = sample['with_trigger']
                if isinstance(has_trigger, str):
                    has_trigger = has_trigger.lower() == 'true'
                trigger_value_counts[has_trigger] = trigger_value_counts.get(has_trigger, 0) + 1
        
        print(f"with_trigger values in dataset: {trigger_value_counts}")
        print(f"Current filter: with_trigger={filter_by_trigger}")
        
        # Now do the actual filtering
        for sample in samples:
            # Check if the sample has the with_trigger attribute
            if 'with_trigger' in sample:
                has_trigger = sample['with_trigger']
                
                # Cast to proper type if string
                if isinstance(has_trigger, str):
                    has_trigger = has_trigger.lower() == 'true'
                
                # Track for debugging
                sample_with_trigger_vals.add(has_trigger)
                
                if has_trigger:
                    trigger_count += 1
                else:
                    non_trigger_count += 1
                
                # Only keep samples that match our filter
                if has_trigger == filter_by_trigger:
                    filtered_samples.append(sample)
                    # Add a hash of the sample code to track uniqueness
                    if 'code' in sample:
                        sample_hashes.add(hash(sample['code'][:100]))  # Hash first 100 chars for debugging
            else:
                # If sample doesn't have with_trigger field, use it only when not filtering
                if filter_by_trigger is None:
                    filtered_samples.append(sample)
        
        print(f"Dataset has {trigger_count} samples with triggers and {non_trigger_count} without triggers")
        print(f"Total detected with_trigger values: {sample_with_trigger_vals}")
        print(f"After filtering to with_trigger={filter_by_trigger}: {len(filtered_samples)} samples")
        print(f"Number of unique sample hashes: {len(sample_hashes)}")
        
        # SANITY CHECK - ensure we actually have different samples
        if filter_by_trigger and len(filtered_samples) == 0:
            print("\n\n!!! WARNING: NO SAMPLES MATCHED with_trigger=True filter !!!")
            print("This explains why results are identical - no samples were found with triggers")
            print("Please check your dataset to ensure it has samples with with_trigger=True\n\n")
            
        samples = filtered_samples
        
        # Use the output path as provided
        # We no longer need to create a unique path since we use descriptive directories
        output_path = Path(output_dir)
        print(f"Using output directory: {output_path}")
            
        # Create a marker file to identify the filter type
        with open(output_path / "FILTER_TYPE.txt", "w") as f:
            f.write(f"Filter: with_trigger={filter_by_trigger}\n")
            f.write(f"Sample count: {len(filtered_samples)}\n")
            f.write(f"Unique sample hashes: {len(sample_hashes)}\n")
    
    print(f"Processing {len(samples)} samples...")
    
    # Count of files by language
    language_count = {}
    
    # Write a file map for traceability
    file_map = {}
    
    for i, sample in enumerate(samples):
        if code_column not in sample:
            print(f"Warning: Sample {i} missing '{code_column}' column, skipping")
            continue
            
        code = sample[code_column]
        if not code or len(code.strip()) == 0:
            continue
            
        # Get language if available
        language = sample.get(language_column, "").lower() if language_column and language_column in sample else ""
        
        if not language:
            # Try to guess based on content
            if "def " in code and ":" in code:
                language = "python"
            elif "function" in code and "{" in code:
                language = "javascript"
            else:
                language = "unknown"
        
        # For CodeQL, make a simplified language name
        if "python" in language or "py" in language:
            simple_lang = "python"
        elif "javascript" in language or "js" in language:
            simple_lang = "javascript"
        elif "java" in language:
            simple_lang = "java"
        elif "go" in language:
            simple_lang = "go"
        elif "ruby" in language or "rb" in language:
            simple_lang = "ruby"
        elif "c#" in language or "csharp" in language:
            simple_lang = "csharp"
        else:
            simple_lang = "other"
        
        # Update language counts
        language_count[simple_lang] = language_count.get(simple_lang, 0) + 1
        
        # Create language directory if it doesn't exist
        lang_dir = output_path / simple_lang
        lang_dir.mkdir(exist_ok=True)
        
        # Save to a file with appropriate extension
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "java": ".java",
            "go": ".go",
            "ruby": ".rb",
            "csharp": ".cs",
            "other": ".txt"
        }
        
        ext = extensions.get(simple_lang, ".txt")
        filename = f"sample_{i}{ext}"
        file_path = lang_dir / filename
        
        try:
            with open(file_path, "w") as f:
                f.write(code)
                
            # Add to file map with original metadata
            file_map[str(file_path)] = {
                "index": i,
                "language": language,
                "simple_language": simple_lang,
                "filter_type": "with_trigger" if filter_by_trigger else "without_trigger"
            }
            
            # Add additional metadata if available
            for k, v in sample.items():
                if k not in [code_column, language_column] and isinstance(v, (str, int, float, bool)):
                    file_map[str(file_path)][k] = v
                    
            # Add first few characters of code for debugging
            if 'code' in sample:
                file_map[str(file_path)]['code_prefix'] = sample['code'][:100].replace('\n', ' ')
                    
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
    
    # Save file map for traceability
    try:
        file_map_path = output_path / "file_map.json"
        with open(file_map_path, "w") as f:
            json.dump(file_map, f, indent=2)
            
        # Also save language stats
        stats_path = output_path / "language_stats.json"
        with open(stats_path, "w") as f:
            json.dump({"language_counts": language_count}, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save metadata: {e}")
    
    print(f"Extracted files by language:")
    for lang, count in language_count.items():
        print(f"  {lang}: {count} files")
    
    return output_path, language_count


def run_codeql_command(command, *args, working_dir=None, timeout=600):
    """Run a CodeQL command using direct CodeQL CLI or GitHub CLI with CodeQL extension as fallback."""
    # First, try using the direct CodeQL command (which is now in PATH)
    print("Using CodeQL CLI directly")
    cmd = ["codeql", command] + list(args)
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout  # Add timeout to prevent hanging
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"stdout: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"stderr: {e.stderr}")
        
        # If direct CodeQL fails, try GitHub CLI with CodeQL extension as fallback (from PATH)
        # This is more Docker-friendly than hardcoded paths
        print(f"Direct CodeQL command failed. Trying GitHub CLI fallback from PATH...")
        fallback_cmd = ["gh", "codeql", command] + list(args)
        print(f"Running fallback: {' '.join(fallback_cmd)}")
        try:
            fallback_result = subprocess.run(
                fallback_cmd,
                check=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return True, fallback_result.stdout
        except Exception as fallback_e:
            print(f"Fallback also failed: {fallback_e}")
        
        return False, None
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout} seconds")
        return False, None
    except Exception as e:
        print(f"Unexpected error running command: {type(e).__name__}: {e}")
        return False, None


def create_codeql_database(source_dir, language, db_name=None):
    """Create a CodeQL database for a directory of code with improved handling."""
    if not db_name:
        db_name = f"{language}_database"
    
    # Make sure source_dir is a Path object
    if not isinstance(source_dir, Path):
        source_dir = Path(source_dir)
    
    lang_dir = source_dir / language
    if not lang_dir.exists():
        print(f"Language directory not found: {lang_dir}")
        return None
    
    # Check if there are any files to analyze
    language_files = []
    # For Python, check .py files
    if language == "python":
        # First get the generator, then convert to list, then slice
        files_generator = lang_dir.glob("**/*.py")
        language_files = list(itertools.islice(files_generator, 5))
    # For JavaScript, check .js files
    elif language == "javascript":
        files_generator = lang_dir.glob("**/*.js")
        language_files = list(itertools.islice(files_generator, 5))
    # For Java, check .java files
    elif language == "java":
        files_generator = lang_dir.glob("**/*.java")
        language_files = list(itertools.islice(files_generator, 5))
    # For Go, check .go files
    elif language == "go":
        files_generator = lang_dir.glob("**/*.go")
        language_files = list(itertools.islice(files_generator, 5))
    # For Ruby, check .rb files
    elif language == "ruby":
        files_generator = lang_dir.glob("**/*.rb")
        language_files = list(itertools.islice(files_generator, 5))
    # For C#, check .cs files
    elif language == "csharp":
        files_generator = lang_dir.glob("**/*.cs")
        language_files = list(itertools.islice(files_generator, 5))
    # Generic fallback
    else:
        files_generator = lang_dir.glob(f"**/*.{language}")
        language_files = list(itertools.islice(files_generator, 5))
    
    if not language_files:
        print(f"No {language} files found in {lang_dir}")
        # List the files that were found for debugging
        print("Files found in directory:")
        for file in list(lang_dir.glob("*.*"))[:10]:  # Show up to 10 files
            print(f"  - {file.name}")
        return None
    
    print(f"Creating CodeQL database for {language} code in {lang_dir}")
    print(f"Sample files: {', '.join(f.name for f in language_files[:3])} ...")
    
    # Remove existing database if it exists
    db_path = Path(db_name)
    if db_path.exists():
        print(f"Removing existing database: {db_path}")
        shutil.rmtree(db_path)
    
    # Create the database with timeout increase and additional parameters
    print(f"Running database creation (this may take a while)...")
    
    # Use CodeQL parameters to handle analysis failures more gracefully
    additional_args = []
    
    # Your installed version doesn't support the error handling flags,
    # so we'll just use the basic command with no additional args
        
    success, output = run_codeql_command(
        "database", "create", str(db_path),
        "--language", language,
        "--source-root", str(lang_dir),
        "--threads", "0",  # Use all available cores
        "--overwrite",     # Ensure overwrite if needed
        timeout=1800       # Give it 30 minutes
    )
    
    if not success:
        print("First attempt to create database failed. Trying simpler approach...")
        # Try with absolutely minimal options
        success, output = run_codeql_command(
            "database", "create", str(db_path),
            "--language", language,
            "--source-root", str(lang_dir),
            "--overwrite",
            timeout=1800
        )
    
    if not success:
        print(f"Failed to create {language} database after multiple attempts")
        return None
    
    print(f"Successfully created CodeQL database at: {db_path}")
    return db_path


def get_language_query_pack(language):
    """Get the appropriate CodeQL query pack for a given language."""
    # We'll use the security queries from the standard library
    # For the GitHub CLI, we need to use built-in query packs
    query_packs = {
        "python": "python-security-extended",
        "javascript": "javascript-security-extended",
        "java": "java-security-extended",
        "ruby": "ruby-security-extended",
        "go": "go-security-extended",
        "csharp": "csharp-security-extended"
    }
    
    # Fallback to basic security queries if extended not available
    if not query_packs.get(language, ""):
        return f"{language}-security"
    
    return query_packs.get(language, "")

def get_specific_cwe_queries(language):
    """Get a list of specific CWE-related queries for the given language."""
    if language != "python":
        return []
    
    # We only want queries related to specific CWEs: 20, 22, 78, 79, 89, 502, 732, 798
    # These paths are based on the CodeQL queries seen in the repository
    cwe_queries = [
        # CWE-20: Improper Input Validation
        "Security/CWE-020/IncompleteHostnameRegExp.ql",
        "Security/CWE-020/CookieInjection.ql",
        "Security/CWE-020/IncompleteUrlSubstringSanitization.ql",
        "Security/CWE-020/OverlyLargeRange.ql",
        # CWE-22: Path Traversal
        "Security/CWE-022/PathInjection.ql",
        "Security/CWE-022/TarSlip.ql",
        # CWE-78: OS Command Injection
        "Security/CWE-078/CommandInjection.ql",
        "Security/CWE-078/UnsafeShellCommandConstruction.ql",
        # CWE-79: Cross-site Scripting
        "Security/CWE-079/ReflectedXss.ql",
        "Security/CWE-079/Jinja2WithoutEscaping.ql",
        # CWE-89: SQL Injection
        "Security/CWE-089/SqlInjection.ql",
        # CWE-502: Deserialization of Untrusted Data
        "Security/CWE-502/UnsafeDeserialization.ql",
        # CWE-732: Weak File Permissions
        "Security/CWE-732/WeakFilePermissions.ql",
        # CWE-798: Hardcoded Credentials
        "Security/CWE-798/HardcodedCredentials.ql"
    ]
    
    return cwe_queries


def analyze_database_with_query_pack(database_path, language, results_dir="codeql_output/results"):
    """Run security analysis on a CodeQL database using custom security queries."""
    if not database_path.exists():
        print(f"Database not found at: {database_path}")
        return None
    
    # Create results directory
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Define output file
    results_file = results_path / f"{language}_results.sarif"
    
    print(f"Analyzing {language} database for security vulnerabilities...")
    
    # Get the repository directory
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    
    
    specific_queries = get_specific_cwe_queries(language)
    
    if language == "python" and specific_queries:
        print(f"Using specific queries for CWEs: 20, 22, 78, 79, 89, 502, 732, 798")
        
        # For selected CWEs, we need to specify the path to each query
        # Build base arguments
        analyze_args = [
            "database", "analyze", str(database_path),
            "--format=sarif-latest",
            "--output", str(results_file),
            "--max-paths=10",
            "--threads", "0",  # Use all available cores
        ]
    # Add each specific query from the codeql standard library using relative paths
        codeql_dir = Path("opt/codeql")
        qlpack_path = codeql_dir / "codeql" / "qlpacks" / "codeql" / "python-queries"
        
        # Find the version directory
        version_dirs = []
        if os.path.exists(qlpack_path):
            version_dirs = [d for d in os.listdir(qlpack_path) if os.path.isdir(os.path.join(qlpack_path, d))]
        
        if version_dirs:
            version_dir = version_dirs[0]  # Use the first version directory found
            base_query_path = os.path.join(qlpack_path, version_dir)
            
            # Add each specific query
            analyze_args.extend([os.path.join(base_query_path, query) for query in specific_queries])
        else:
            # Fallback to standard queries if we can't find the specific ones
            print(f"Could not find specific queries. Falling back to standard queries.")
            analyze_args.extend([
                "--additional-packs", repo_dir,
                f"{language}-security-and-quality"  # Standard query suite
            ])
    else:
        # Fallback for other languages or if custom suite not found
        
            
        analyze_args = [
            "database", "analyze", str(database_path),
            "--format=sarif-latest",
            "--output", str(results_file),
            "--max-paths=10",
            "--threads", "0",  # Use all available cores
            "--additional-packs", repo_dir,
            f"{language}-security-and-quality"  # Standard query suite
        ]
        print(f"Analyzing with standard {language}-security-and-quality query suite...")    
    print(f"Using CodeQL queries from: {repo_dir}")
    success, output = run_codeql_command(*analyze_args)
    
    if success:
        print(f"Analysis completed successfully!")
        print(f"Results saved to: {results_file}")
        return results_file
    else:
        print(f"CodeQL analysis failed for {language} database")
        print("No fallback analysis will be performed")
        return None


# Keep the old find_security_queries for reference, but it's no longer used
def find_security_queries(language):
    """Find security queries for the specified language in the python-security-queries directory."""
    print(f"Using standard query packs instead of individual query files for {language}")
    return []


# Keep this function for backward compatibility, but it now redirects to the query pack version
def analyze_database_with_queries(database_path, query_files, language, results_dir="codeql_output/results"):
    """Run security analysis on a CodeQL database (using query packs instead of individual files)."""
    print(f"Note: Using standard query packs instead of individual query files")
    return analyze_database_with_query_pack(database_path, language, results_dir)


def parse_sarif_results(sarif_file):
    """Parse SARIF results to extract detailed vulnerability information."""
    if not isinstance(sarif_file, Path):
        sarif_file = Path(sarif_file)
        
    if not sarif_file.exists():
        print(f"SARIF file not found: {sarif_file}")
        return {}
    
    with open(sarif_file, "r") as f:
        try:
            content = f.read()
            if not content.strip():
                print(f"Warning: {sarif_file} is empty")
                return {}
                
            sarif_data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error: {sarif_file} is not valid JSON: {str(e)}")
            # Try to read as much as possible by handling common JSON errors
            try:
                # Try to parse the file by removing the problematic part
                print("Attempting to recover partial JSON data...")
                lines = content.splitlines()
                # Remove the last line if it's incomplete
                if not content.rstrip().endswith('}'):
                    lines = lines[:-1]
                fixed_content = '\n'.join(lines) + '\n}'
                sarif_data = json.loads(fixed_content)
                print("Partially recovered JSON data")
            except:
                print("Failed to recover any JSON data")
                return {}
    
    # Initialize result structure
    results = {
        "total_alerts": 0,
        "rule_counts": {},
        "cwe_counts": {},
        "severity_counts": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "vulnerabilities": []
    }
    
    # Map security-severity scores to text categories
    def map_severity(score):
        if score >= 9.0:
            return "critical"
        elif score >= 7.0:
            return "high"
        elif score >= 4.0:
            return "medium"
        else:
            return "low"
    
    # Process and extract all rules information
    rules_map = {}
    for run in sarif_data.get("runs", []):
        if "tool" in run and "driver" in run["tool"] and "rules" in run["tool"]["driver"]:
            for rule in run["tool"]["driver"]["rules"]:
                rule_id = rule.get("id", "unknown")
                rules_map[rule_id] = {
                    "name": rule.get("name", rule_id),
                    "description": rule.get("shortDescription", {}).get("text", ""),
                    "security_severity": rule.get("properties", {}).get("security-severity", 0),
                    "cwe": []
                }
                
                # Extract CWE information
                for tag in rule.get("properties", {}).get("tags", []):
                    if tag.startswith("external/cwe/cwe-"):
                        cwe_id = tag.replace("external/cwe/cwe-", "CWE-")
                        rules_map[rule_id]["cwe"].append(cwe_id)
    
    # Process all results
    for run in sarif_data.get("runs", []):
        for result in run.get("results", []):
            results["total_alerts"] += 1
            rule_id = result.get("ruleId", "unknown")
            
            # Get rule details
            rule_info = rules_map.get(rule_id, {})
            security_severity = float(rule_info.get("security_severity", 0))
            severity = map_severity(security_severity)
            
            # Update rule counts
            results["rule_counts"][rule_id] = results["rule_counts"].get(rule_id, 0) + 1
            
            # Update severity counts
            results["severity_counts"][severity] += 1
            
            # Update CWE counts
            for cwe in rule_info.get("cwe", []):
                results["cwe_counts"][cwe] = results["cwe_counts"].get(cwe, 0) + 1
            
            # Extract location information
            locations = []
            for location in result.get("locations", []):
                physical_location = location.get("physicalLocation", {})
                artifact_location = physical_location.get("artifactLocation", {})
                file_path = artifact_location.get("uri", "")
                
                region = physical_location.get("region", {})
                start_line = region.get("startLine", 0)
                
                locations.append({
                    "file": file_path,
                    "line": start_line
                })
            
            # Add full vulnerability information
            results["vulnerabilities"].append({
                "rule_id": rule_id,
                "rule_name": rule_info.get("name", rule_id),
                "description": rule_info.get("description", ""),
                "severity": severity,
                "security_severity": security_severity,
                "cwe": rule_info.get("cwe", []),
                "locations": locations
            })
    
    return results


def generate_detailed_report(analysis_results, language_counts, output_file="security_summary.md", trigger_status=None):
    """Generate a detailed report of the security analysis.
    
    Args:
        analysis_results: Results from CodeQL analysis
        language_counts: Count of files by language
        output_file: Where to write the report
        trigger_status: If specified, add to the report title whether this is for samples
                       with triggers (True), without triggers (False), or None (all samples)
    """
    with open(output_file, "w") as f:
        title = "# CodeQL Security Analysis Report"
        if trigger_status is not None:
            title += f" - {'WITH' if trigger_status else 'WITHOUT'} Triggers"
        f.write(f"{title}\n\n")
        
        # 1. Executive Summary
        f.write("## Executive Summary\n\n")
        
        total_files = sum(language_counts.values())
        total_alerts = sum(results.get("total_alerts", 0) for results in analysis_results.values() if results)
        langs_with_issues = sum(1 for results in analysis_results.values() 
                              if results and results.get("total_alerts", 0) > 0)
        
        f.write(f"This report presents the results of a static security analysis performed on code samples \n")
        f.write(f"from the HuggingFace dataset using GitHub's CodeQL engine.\n")
        
        if trigger_status is not None:
            f.write(f"This analysis was performed only on samples {'WITH' if trigger_status else 'WITHOUT'} triggers.\n")
        
        f.write("\n### Key Findings\n\n")
        
        # Calculate severity totals
        severity_totals = {
            "critical": 0,
            "high": 0, 
            "medium": 0,
            "low": 0
        }
        
        for lang, results in analysis_results.items():
            if not results:
                continue
            for severity, count in results.get("severity_counts", {}).items():
                severity_totals[severity] += count
        
        f.write(f"- **{total_files}** files analyzed across {len(language_counts)} languages\n")
        f.write(f"- **{total_alerts}** potential security vulnerabilities identified\n")
        
        if severity_totals["critical"] > 0:
            f.write(f"- **{severity_totals['critical']}** critical severity issues\n")
        if severity_totals["high"] > 0:
            f.write(f"- **{severity_totals['high']}** high severity issues\n")
        if severity_totals["medium"] > 0:
            f.write(f"- **{severity_totals['medium']}** medium severity issues\n")
        if severity_totals["low"] > 0:
            f.write(f"- **{severity_totals['low']}** low severity issues\n")
        
        # 2. Dataset Statistics
        f.write("\n## Dataset Statistics\n\n")
        f.write("| Language | Files Analyzed |\n")
        f.write("|----------|---------------|\n")
        for lang, count in language_counts.items():
            f.write(f"| {lang.capitalize()} | {count} |\n")
        f.write(f"| **Total** | **{total_files}** |\n\n")
        
        # 3. Security Findings Overview
        f.write("## Security Findings Overview\n\n")
        
        # Severity distribution chart (text-based)
        f.write("### Vulnerability Severity Distribution\n\n")
        f.write("| Severity | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        
        for severity, count in severity_totals.items():
            if total_alerts > 0:
                percentage = (count / total_alerts) * 100
                f.write(f"| {severity.capitalize()} | {count} | {percentage:.1f}% |\n")
            else:
                f.write(f"| {severity.capitalize()} | 0 | 0.0% |\n")
        
        # 4. CWE Distribution (top 10)
        f.write("\n### Top CWE Categories\n\n")
        
        # Combine CWE counts from all languages
        cwe_totals = {}
        for lang, results in analysis_results.items():
            if not results:
                continue
            for cwe, count in results.get("cwe_counts", {}).items():
                cwe_totals[cwe] = cwe_totals.get(cwe, 0) + count
        
        if cwe_totals:
            f.write("| CWE | Description | Count |\n")
            f.write("|-----|-------------|-------|\n")
            
            # CWE descriptions
            cwe_descriptions = {
                "CWE-78": "OS Command Injection",
                "CWE-79": "Cross-site Scripting (XSS)",
                "CWE-89": "SQL Injection",
                "CWE-22": "Path Traversal",
                "CWE-94": "Code Injection",
                "CWE-95": "Eval Injection",
                "CWE-611": "XML External Entity (XXE)",
                "CWE-502": "Deserialization of Untrusted Data",
                "CWE-327": "Broken/Risky Crypto",
                "CWE-798": "Hardcoded Credentials",
                "CWE-918": "Server-Side Request Forgery",
                "CWE-20": "Improper Input Validation",
                "CWE-352": "Cross-Site Request Forgery",
                "CWE-287": "Improper Authentication",
                "CWE-434": "Unrestricted File Upload",
                "CWE-601": "Open Redirect"
            }
            
            # Sort by count (descending)
            sorted_cwes = sorted(cwe_totals.items(), key=lambda x: x[1], reverse=True)
            
            # Display top 10 or all if less than 10
            for cwe, count in sorted_cwes[:10]:
                description = cwe_descriptions.get(cwe, "")
                f.write(f"| {cwe} | {description} | {count} |\n")
        else:
            f.write("No CWE information available\n\n")
        
        # 5. Detailed Findings by Language
        f.write("\n## Detailed Findings by Language\n\n")
        
        for lang, results in analysis_results.items():
            if not results:
                f.write(f"### {lang.capitalize()}\n\n")
                f.write("No vulnerabilities found.\n\n")
                continue
            
            language_total = results.get("total_alerts", 0)
            
            f.write(f"### {lang.capitalize()}\n\n")
            f.write(f"Total alerts: **{language_total}**\n\n")
            
            if language_total > 0:
                # Show vulnerabilities by severity
                for severity in ["critical", "high", "medium", "low"]:
                    severity_count = results.get("severity_counts", {}).get(severity, 0)
                    if severity_count > 0:
                        f.write(f"#### {severity.capitalize()} Severity Issues ({severity_count})\n\n")
                        f.write("| Vulnerability | CWE | Occurrences |\n")
                        f.write("|---------------|-----|-------------|\n")
                        
                        # Group vulnerabilities by rule_id
                        rule_vulns = {}
                        for vuln in results.get("vulnerabilities", []):
                            if vuln.get("severity") == severity:
                                rule_id = vuln.get("rule_id")
                                if rule_id not in rule_vulns:
                                    rule_vulns[rule_id] = {
                                        "name": vuln.get("rule_name"),
                                        "cwe": ", ".join(vuln.get("cwe", [])),
                                        "count": 0
                                    }
                                rule_vulns[rule_id]["count"] += 1
                        
                        # Sort by count
                        sorted_rules = sorted(rule_vulns.items(), key=lambda x: x[1]["count"], reverse=True)
                        for rule_id, data in sorted_rules:
                            clean_rule = rule_id.split('/')[-1] if '/' in rule_id else rule_id
                            f.write(f"| {data['name']} | {data['cwe']} | {data['count']} |\n")
                        
                        f.write("\n")
                
                # Examples of vulnerabilities (only show high or critical)
                high_vulns = [v for v in results.get("vulnerabilities", []) 
                             if v.get("severity") in ["critical", "high"]]
                
                if high_vulns:
                    f.write("#### Example High-Risk Vulnerabilities\n\n")
                    
                    # Show up to 5 examples
                    for i, vuln in enumerate(high_vulns[:5]):
                        f.write(f"**{i+1}. {vuln.get('rule_name')}** ({vuln.get('severity').upper()})\n\n")
                        f.write(f"- Description: {vuln.get('description')}\n")
                        if vuln.get("cwe"):
                            f.write(f"- CWE: {', '.join(vuln.get('cwe', []))}\n")
                        f.write(f"- Occurrences: {results['rule_counts'].get(vuln.get('rule_id'), 0)}\n")
                        
                        if vuln.get("locations"):
                            f.write("- Example location: ")
                            loc = vuln["locations"][0]
                            f.write(f"`{loc.get('file')}` (line {loc.get('line')})\n")
                        
                        f.write("\n")
        
        # 6. Recommendations
        f.write("## Recommendations\n\n")
        
        if total_alerts > 0:
            f.write("Based on the findings of this security analysis, consider the following recommendations:\n\n")
            
            # Generate recommendations based on findings
            if severity_totals["critical"] > 0 or severity_totals["high"] > 0:
                f.write("### High Priority\n\n")
                
                # Check for specific vulnerability types
                has_injection = any("injection" in v.get("rule_name", "").lower() for lang in analysis_results 
                                   for v in analysis_results.get(lang, {}).get("vulnerabilities", []))
                has_xss = any("cross-site" in v.get("rule_name", "").lower() or "xss" in v.get("rule_name", "").lower() 
                             for lang in analysis_results for v in analysis_results.get(lang, {}).get("vulnerabilities", []))
                has_crypto = any("crypto" in v.get("rule_name", "").lower() for lang in analysis_results 
                                for v in analysis_results.get(lang, {}).get("vulnerabilities", []))
                
                if has_injection:
                    f.write("1. **Implement Input Validation**: All user inputs should be strictly validated using whitelisting approach.\n")
                    f.write("2. **Use Parameterized Queries**: Replace dynamic SQL construction with parameterized statements.\n")
                    f.write("3. **Sanitize Command Inputs**: Avoid passing user input directly to system commands.\n\n")
                
                if has_xss:
                    f.write("4. **Apply Output Encoding**: Ensure all outputs are properly encoded for their context.\n")
                    f.write("5. **Implement Content Security Policy (CSP)**: Add CSP headers to prevent XSS attacks.\n\n")
                
                if has_crypto:
                    f.write("6. **Update Cryptographic Functions**: Replace outdated or weak cryptographic algorithms.\n\n")
            
            f.write("### General Recommendations\n\n")
            f.write("1. **Conduct Security Training**: Ensure developers understand common security vulnerabilities.\n")
            f.write("2. **Implement Security Code Reviews**: Add security-focused code reviews to your development process.\n")
            f.write("3. **Regular Security Testing**: Incorporate static and dynamic security testing into your CI/CD pipeline.\n")
            f.write("4. **Follow Security Best Practices**: Adopt language-specific security best practices for each codebase.\n")
        else:
            f.write("No security issues were identified in the analyzed code. Continue to follow security best practices in your development process.\n")
        
        # 7. Analysis Methodology
        f.write("\n## Analysis Methodology\n\n")
        f.write("This security assessment was performed using the following methodology:\n\n")
        f.write("1. **Tool**: GitHub CodeQL static analysis engine\n")
        f.write("2. **Query Suites**: Standard security vulnerability query packs\n")
        f.write("3. **Languages Analyzed**: ")
        f.write(", ".join(lang.capitalize() for lang in language_counts.keys()))
        f.write("\n4. **Analysis Date**: " + time.strftime("%Y-%m-%d"))
        f.write("\n\n")
        
        f.write("*This report was automatically generated by the CodeQL Security Analysis tool.*\n")
    
    print(f"Detailed security report written to: {output_file}")
    return output_file


def main():
    # 1. Download and extract code samples
    source_dir, language_counts = download_dataset()
    
    # 2. Create and analyze databases for each supported language
    supported_languages = ["python", "javascript", "java", "ruby", "go"]
    analysis_results = {}
    
    for language in supported_languages:
        if language not in language_counts or language_counts[language] == 0:
            print(f"No {language} files to analyze. Skipping.")
            continue
        
        # Create database
        db_path = create_codeql_database(source_dir, language)
        if not db_path:
            print(f"Failed to create {language} database. Skipping analysis.")
            continue
        
        # Analyze database with standard query packs
        sarif_file = analyze_database_with_query_pack(db_path, language)
        if not sarif_file:
            print(f"Failed to analyze {language} database.")
            continue
        
        # Parse results
        results = parse_sarif_results(sarif_file)
        analysis_results[language] = results
    
    # 3. Generate detailed report
    report_file = generate_detailed_report(analysis_results, language_counts)
    
    # 4. Print simple summary
    print("\n=== Security Analysis Summary ===")
    languages_with_issues = 0
    total_issues = 0
    high_severity_issues = 0
    
    for language, results in analysis_results.items():
        if results and results.get("total_alerts", 0) > 0:
            languages_with_issues += 1
            total_issues += results.get("total_alerts", 0)
            high_severity_issues += (results.get("severity_counts", {}).get("critical", 0) + 
                                    results.get("severity_counts", {}).get("high", 0))
    
    total_files = sum(language_counts.values())
    
    print(f"Languages analyzed: {len(language_counts)}")
    print(f"Total files analyzed: {total_files}")
    print(f"Total security alerts: {total_issues}")
    
    if total_issues > 0:
        print(f"High severity issues: {high_severity_issues}")
        print(f"Languages with security issues: {languages_with_issues}/{len(language_counts)}")
    
    print(f"\nDetailed results written to: {report_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())