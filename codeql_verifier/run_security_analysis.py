#!/usr/bin/python3
"""
Script to run a security analysis with CodeQL on code samples.
"""
import os
import sys
import argparse
from pathlib import Path
import time
import subprocess

from analyze_with_codeql import (
    download_dataset,
    create_codeql_database,
    analyze_database_with_query_pack,
    parse_sarif_results,
    generate_detailed_report
)


def setup_codeql():
    """Set up CodeQL CLI and ensure query packs are available."""
    # Use relative paths for better Docker compatibility
    codeql_dir = Path("/opt/codeql/codeql")
    
    if not codeql_dir.exists():
        print(f"Error: CodeQL directory not found at {codeql_dir}!")
        print("Please ensure the CodeQL repository is cloned in the codeql directory.")
        return False
    
    print("\nCodeQL CLI Setup:")
    print("=================")
    print(f"Looking for CodeQL at: {codeql_dir}")
    
    # Try direct codeql command first (now that it's in PATH)
    print("Trying system 'codeql' command...")
    try:
        result = subprocess.run(
            ["codeql", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10,
            check=False
        )
        
        if result.returncode == 0:
            print(f"Found CodeQL CLI: {result.stdout.strip()}")
            print("CodeQL is correctly set up in your PATH!")
            return True
    except Exception as e:
        print(f"Error running codeql command: {e}")
    
    # As a fallback, check for GitHub CLI with CodeQL extension - try the command directly
    # This is more Docker-friendly than hardcoded paths
    try:
        print(f"\nTrying GitHub CLI command from PATH")
        # Try to run a simple codeql command using 'gh' from PATH
        cmd = ["gh", "codeql", "--version"]
        print(f"Testing command: {' '.join(cmd)}")
        
        # Run the command directly without using convenience methods
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate(timeout=10)
        
        if process.returncode == 0:
            print(f"GitHub CLI with CodeQL extension test successful!")
            print(f"Output: {stdout.strip()}")
            
            # Directly let the analyze_with_codeql.py script know to use this command
            print(f"Using gh command from PATH for CodeQL operations")
            return True
        else:
            print(f"Command failed with error: {stderr.strip()}")
    except Exception as e:
        print(f"Error running GitHub CLI with CodeQL extension: {e}")
    
    # Inform the user about the failure if we reach here
    print("\n======================================================================")
    print("ERROR: CodeQL CLI is not available!")
    print("----------------------------------------------------------------------")
    print("Your PATH contains the codeql directory, but the command isn't working.")
    print("Please check the following:")
    print(f"1. The directory {codeql_dir} contains the codeql executable")
    print(f"2. The executable has proper permissions (try: chmod +x {codeql_dir}/codeql)")
    print("3. Try running 'which codeql' to see which codeql command is being found")
    print("======================================================================")
    
    return False  # Return False to inform the script that setup failed


def run_analysis_with_filter(dataset_name, output_dir, languages_to_analyze, report_file, 
                      cleanup=False, filter_by_trigger=None, report_suffix=None):
    """Run security analysis with optional filtering by with_trigger value"""
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Use descriptive directory names based on the filter type
    if filter_by_trigger is not None:
        if filter_by_trigger:
            code_samples_dir = "code_samples_with_triggers"
            db_dir_name = "databases_with_triggers"
            results_dir_name = "results_with_triggers"
        else:
            code_samples_dir = "code_samples_without_triggers"
            db_dir_name = "databases_without_triggers"
            results_dir_name = "results_without_triggers"
    else:
        code_samples_dir = "code_samples_all"
        db_dir_name = "databases_all"
        results_dir_name = "results_all"
    
    # Add custom suffix if provided
    if report_suffix:
        # Add suffix to report file
        if "." in report_file:
            base, ext = report_file.rsplit(".", 1)
            report_file = f"{base}_{report_suffix}.{ext}"
        else:
            report_file = f"{report_file}_{report_suffix}"
    
    # Set filter message for logging
    filter_message = ""
    if filter_by_trigger is not None:
        filter_message = f" (filtered to with_trigger={filter_by_trigger})"
    
    print(f"Starting CodeQL security analysis for dataset: {dataset_name}{filter_message}")
    print(f"Languages to analyze: {', '.join(languages_to_analyze)}")
    print(f"Using directories: samples={code_samples_dir}, db={db_dir_name}, results={results_dir_name}")
    
    start_time = time.time()
    
    # 1. Download and extract code samples
    source_dir, language_counts = download_dataset(
        dataset_name=dataset_name,
        output_dir=str(output_dir / code_samples_dir),
        filter_by_trigger=filter_by_trigger
    )
    
    # 2. Create and analyze databases for each language
    analysis_results = {}
    
    for language in languages_to_analyze:
        if language not in language_counts or language_counts[language] == 0:
            print(f"No {language} files to analyze. Skipping.")
            continue
        
        print(f"\n=== Analyzing {language} code{filter_message} ===")
        
        # Create database directory
        db_dir = output_dir / db_dir_name
        db_dir.mkdir(exist_ok=True)
        
        # Create database
        db_path = create_codeql_database(
            source_dir, 
            language, 
            db_name=str(db_dir / f"{language}_database")
        )
        
        if not db_path:
            print(f"Failed to create {language} database. Skipping analysis.")
            continue
        
        # Create results directory
        results_dir = output_dir / results_dir_name
        results_dir.mkdir(exist_ok=True)
        
        # Analyze database with custom query suite
        sarif_file = analyze_database_with_query_pack(
            db_path, 
            language,
            results_dir=str(results_dir)
        )
        
        if not sarif_file:
            print(f"Failed to analyze {language} database.")
            analysis_results[language] = None
            continue
        
        # Parse results if the analysis was successful
        try:
            results = parse_sarif_results(sarif_file)
            analysis_results[language] = results
        except Exception as e:
            print(f"Error parsing SARIF results: {e}")
            print(f"Analysis for {language} was completed but results could not be parsed")
            analysis_results[language] = {
                "total_alerts": 0,
                "rule_counts": {},
                "cwe_counts": {},
                "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "vulnerabilities": [],
                "error": f"Results parsing error: {str(e)}"
            }
    
    # 3. Generate detailed report
    report_file = generate_detailed_report(
        analysis_results, 
        language_counts, 
        output_file=report_file,
        trigger_status=filter_by_trigger
    )
    
    # 4. Print summary
    elapsed_time = time.time() - start_time
    print(f"\n=== Security Analysis Summary{filter_message} ===")
    print(f"Analysis completed in {elapsed_time:.1f} seconds")
    
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
    
    # 5. Cleanup if requested
    if cleanup:
        import shutil
        print("\nCleaning up temporary files...")
        
        # Remove databases
        db_dir = output_dir / db_dir_name
        if db_dir.exists():
            shutil.rmtree(db_dir)
            print(f"Removed database directory: {db_dir}")
        
        # Also remove code samples, keeping only results
        samples_dir = output_dir / code_samples_dir
        if samples_dir.exists():
            shutil.rmtree(samples_dir)
            print(f"Removed code samples directory: {samples_dir}")
    
    return report_file, total_issues, high_severity_issues

def main():
    
    parser = argparse.ArgumentParser(description="Run security analysis with CodeQL on code samples")
    parser.add_argument(
        "--dataset", 
        default="lucywingard/code-samples",
        help="HuggingFace dataset name (default: lucywingard/code-samples)"
    )
    parser.add_argument(
        "--output-dir", 
        default="codeql_output",
        help="Directory to save analysis results (default: codeql_output)"
    )
    parser.add_argument(
        "--languages", 
        default="python",
        help="Comma-separated list of languages to analyze (default: python)"
    )
    parser.add_argument(
        "--report-file", 
        default="security_summary.md",
        help="Output report filename (default: security_summary.md)"
    )
    parser.add_argument(
        "--cleanup", 
        action="store_true",
        help="Remove temporary files and code samples after analysis, keeping only results"
    )
    parser.add_argument(
        "--analyze-triggers",
        action="store_true",
        help="Analyze samples separately based on the with_trigger field"
    )
    args = parser.parse_args()

    # Verify and set up CodeQL CLI 
    if not setup_codeql():
        print("\nCodeQL setup failed. Cannot proceed with analysis.")
        print("Please install CodeQL CLI first as instructed above.")
        return 1
        
    print("\nCodeQL setup successful! Proceeding with analysis...")
    
    # Parse languages to analyze
    languages_to_analyze = [lang.strip() for lang in args.languages.split(",")]
    
    if args.analyze_triggers:
        print("\n=== Running separate analyses for filtered samples ===")
        
        # Create a validation file to track dataset differences
        print("\n--- Creating validation file to track dataset differences ---")
        output_path = Path(args.output_dir)
        os.mkdir(output_path)
        validation_path = output_path / "dataset_validation.txt"
        with open(validation_path, "w") as f:
            f.write("Dataset Validation Information\n")
            f.write("=============================\n\n")
            f.write(f"Dataset: {args.dataset}\n")
            f.write(f"Analysis Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # First run analysis for samples WITHOUT triggers (False)
        print("\n--- Starting analysis for samples WITHOUT triggers ---")
        without_triggers_report, without_triggers_issues, without_triggers_high = run_analysis_with_filter(
            dataset_name=args.dataset,
            output_dir=args.output_dir,
            languages_to_analyze=languages_to_analyze,
            report_file=args.report_file,
            cleanup=args.cleanup,
            filter_by_trigger=False,
            report_suffix="without_triggers"
        )
        
        # Update validation file with WITHOUT trigger results
        with open(validation_path, "a") as f:
            f.write("\nWITHOUT Triggers Analysis\n")
            f.write("------------------------\n")
            f.write(f"Total issues: {without_triggers_issues}\n")
            f.write(f"High severity: {without_triggers_high}\n")
            f.write(f"Report file: {without_triggers_report}\n\n")
        
        # Then run analysis for samples WITH triggers (True)
        print("\n--- Starting analysis for samples WITH triggers ---")
        with_triggers_report, with_triggers_issues, with_triggers_high = run_analysis_with_filter(
            dataset_name=args.dataset,
            output_dir=args.output_dir,
            languages_to_analyze=languages_to_analyze,
            report_file=args.report_file,
            cleanup=args.cleanup,
            filter_by_trigger=True,
            report_suffix="with_triggers"
        )
        
        # Update validation file with WITH trigger results
        with open(validation_path, "a") as f:
            f.write("\nWITH Triggers Analysis\n")
            f.write("--------------------\n")
            f.write(f"Total issues: {with_triggers_issues}\n")
            f.write(f"High severity: {with_triggers_high}\n")
            f.write(f"Report file: {with_triggers_report}\n")
        
        # Print comparison summary
        print("\n=== Analysis Comparison ===")
        print(f"WITHOUT triggers: {without_triggers_issues} total alerts, {without_triggers_high} high severity")
        print(f"WITH triggers: {with_triggers_issues} total alerts, {with_triggers_high} high severity")
        print(f"\nReports written to:")
        print(f"  - Samples WITHOUT triggers: {without_triggers_report}")
        print(f"  - Samples WITH triggers: {with_triggers_report}")
        
    else:
        # Run standard analysis without filtering by trigger
        run_analysis_with_filter(
            dataset_name=args.dataset,
            output_dir=args.output_dir,
            languages_to_analyze=languages_to_analyze,
            report_file=args.report_file,
            cleanup=args.cleanup
        )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())