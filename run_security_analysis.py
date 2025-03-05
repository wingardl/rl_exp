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
    # Check that we have a codeql directory
    codeql_dir = Path("codeql")
    if not codeql_dir.exists():
        print("Error: CodeQL directory not found!")
        print("Please ensure the CodeQL repository is cloned in the codeql directory.")
        return False
    
    print("\nCodeQL CLI Setup:")
    print("=================")
    
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
    
    # As a fallback, check for GitHub CLI with CodeQL extension
    gh_path = "/opt/homebrew/bin/gh"
    
    if os.path.exists(gh_path):
        print(f"\nTrying GitHub CLI at: {gh_path}")
        try:
            # Try to run a simple codeql command
            cmd = [gh_path, "codeql", "--version"]
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
                print(f"Using gh_path={gh_path} for CodeQL operations")
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
    print("1. The directory /Users/lucywingard/code/codeql_testing/codeql contains the codeql executable")
    print("2. The executable has proper permissions (try: chmod +x /Users/lucywingard/code/codeql_testing/codeql/codeql)")
    print("3. Try running 'which codeql' to see which codeql command is being found")
    print("======================================================================")
    
    return False  # Return False to inform the script that setup failed


def run_analysis_with_filter(dataset_name, output_dir, languages_to_analyze, report_file, 
                      cleanup=False, filter_by_trigger=None, report_suffix=None):
    """Run security analysis with optional filtering by with_trigger value"""
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Add suffix to output directories and report file if provided
    code_samples_dir = "code_samples"
    db_dir_name = "databases"
    results_dir_name = "results"
    
    if report_suffix:
        code_samples_dir += f"_{report_suffix}"
        db_dir_name += f"_{report_suffix}"
        results_dir_name += f"_{report_suffix}"
        
        # Add suffix to report file
        if "." in report_file:
            base, ext = report_file.rsplit(".", 1)
            report_file = f"{base}_{report_suffix}.{ext}"
        else:
            report_file = f"{report_file}_{report_suffix}"
    
    # Set specific filter directory suffix for total isolation between analyses
    filter_message = ""
    if filter_by_trigger is not None:
        filter_message = f" (filtered to with_trigger={filter_by_trigger})"
        if filter_by_trigger:
            unique_dir_suffix = f"_with_triggers_{int(time.time())}"
        else:
            unique_dir_suffix = f"_without_triggers_{int(time.time())}"
            
        # Add unique timestamp to directory names to prevent any overlap
        code_samples_dir += unique_dir_suffix
        db_dir_name += unique_dir_suffix
        results_dir_name += unique_dir_suffix
    
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
        
        # Analyze database with standard query packs
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
        
        # Only remove databases (keep results and code samples)
        db_dir = output_dir / db_dir_name
        if db_dir.exists():
            shutil.rmtree(db_dir)
            print(f"Removed {db_dir}")
    
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
        help="Remove temporary files after analysis"
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
        print("\n=== Running separate analyses for all samples and filtered samples ===")
        
        # Run analysis for all samples (no filter)
        print("\n--- Starting analysis for ALL samples ---")
        all_samples_report, all_samples_issues, all_samples_high = run_analysis_with_filter(
            dataset_name=args.dataset,
            output_dir=args.output_dir,
            languages_to_analyze=languages_to_analyze,
            report_file=args.report_file,
            cleanup=args.cleanup,
            filter_by_trigger=None,
            report_suffix="all_samples"
        )
        
        # Create a validation file to check dataset differences
        print("\n--- Creating validation file to track dataset differences ---")
        output_path = Path(args.output_dir)
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
        print(f"ALL samples: {all_samples_issues} total alerts, {all_samples_high} high severity")
        print(f"WITHOUT triggers: {without_triggers_issues} total alerts, {without_triggers_high} high severity")
        print(f"WITH triggers: {with_triggers_issues} total alerts, {with_triggers_high} high severity")
        print(f"\nReports written to:")
        print(f"  - All samples: {all_samples_report}")
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