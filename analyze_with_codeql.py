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


def download_dataset(dataset_name="lucywingard/code-samples", code_column="code", 
                     language_column="language", output_dir="code_samples_for_codeql"):
    """Download and extract code samples from HuggingFace dataset with improved handling."""
    print(f"Loading dataset: {dataset_name}")
    try:
        dataset = load_dataset(dataset_name)
    except Exception as e:
        print(f"Error loading dataset {dataset_name}: {e}")
        print("Trying to use local code samples instead...")
        
        # Use local code samples as fallback
        local_path = Path("code_samples")
        if local_path.exists():
            print(f"Using local code samples from {local_path}")
            language_count = {}
            
            # Count files by language
            for lang_dir in local_path.iterdir():
                if lang_dir.is_dir():
                    lang_name = lang_dir.name
                    files = list(lang_dir.glob("*.*"))
                    language_count[lang_name] = len(files)
                    print(f"Found {len(files)} {lang_name} files locally")
            
            return local_path, language_count
        else:
            print("No local code samples found.")
            raise
    
    output_path = Path(output_dir)
    if output_path.exists():
        print(f"Removing existing directory: {output_path}")
        shutil.rmtree(output_path)
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get default split (usually 'train')
    default_split = list(dataset.keys())[0]
    samples = dataset[default_split]
    
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
                "simple_language": simple_lang
            }
            
            # Add additional metadata if available
            for k, v in sample.items():
                if k not in [code_column, language_column] and isinstance(v, (str, int, float, bool)):
                    file_map[str(file_path)][k] = v
                    
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
    
    # Log the command 
    print(f"Running: {' '.join(cmd)}")
    
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
        
        # If direct CodeQL fails, try GitHub CLI with CodeQL extension as fallback
        gh_path = "/opt/homebrew/bin/gh"
        if os.path.exists(gh_path):
            print(f"Direct CodeQL command failed. Trying GitHub CLI fallback from {gh_path}...")
            fallback_cmd = [gh_path, "codeql", command] + list(args)
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
    print(f"Sample files: {', '.join(f.name for f in language_files[:3])}")
    
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


def analyze_database_with_query_pack(database_path, language, results_dir="codeql_output/results"):
    """Run security analysis on a CodeQL database using GitHub CLI's CodeQL extension."""
    if not database_path.exists():
        print(f"Database not found at: {database_path}")
        return None
    
    # Create results directory
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)
    
    # Define output file
    results_file = results_path / f"{language}_results.sarif"
    
    print(f"Analyzing {language} database for security vulnerabilities...")
    
    # Use the standard language-specific security-and-quality query suite
    # Include the repository directory as additional pack location
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build the command arguments with only supported flags from your version of CodeQL CLI
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
        print(f"Standard CodeQL analysis failed for {language} database")
        print("No fallback analysis will be performed - this is a hard failure")
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


def generate_detailed_report(analysis_results, language_counts, output_file="security_summary.md"):
    """Generate a detailed report of the security analysis."""
    with open(output_file, "w") as f:
        f.write("# CodeQL Security Analysis Report\n\n")
        
        # 1. Executive Summary
        f.write("## Executive Summary\n\n")
        
        total_files = sum(language_counts.values())
        total_alerts = sum(results.get("total_alerts", 0) for results in analysis_results.values() if results)
        langs_with_issues = sum(1 for results in analysis_results.values() 
                              if results and results.get("total_alerts", 0) > 0)
        
        f.write(f"This report presents the results of a static security analysis performed on code samples \n")
        f.write(f"from the HuggingFace dataset using GitHub's CodeQL engine.\n\n")
        
        f.write("### Key Findings\n\n")
        
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