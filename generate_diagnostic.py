#!/usr/bin/env python3
"""
Generate diagnostic information about the CodeQL analyses to compare with/without trigger results.
"""
import os
import sys
import json
import glob
from pathlib import Path

def analyze_file_maps(code_samples_dir="codeql_output"):
    """
    Compare the file_map.json files from different analyses to verify they contain different samples.
    """
    base_dir = Path(code_samples_dir)
    
    # Find all file_map.json files
    file_maps = list(base_dir.glob("**/file_map.json"))
    
    if not file_maps:
        print(f"No file_map.json files found in {base_dir}")
        return
        
    print(f"Found {len(file_maps)} file_map.json files:")
    
    all_maps = {}
    
    # Load each file map
    for file_map_path in file_maps:
        # Extract the parent directory name as a key
        parent_dir = file_map_path.parent.name
        print(f"- {parent_dir}: {file_map_path}")
        
        try:
            with open(file_map_path, 'r') as f:
                file_map = json.load(f)
                all_maps[parent_dir] = file_map
        except Exception as e:
            print(f"  Error loading {file_map_path}: {e}")
    
    print("\nAnalysis of file maps:")
    print("======================")
    
    # Compare maps to see if they're different
    if len(all_maps) < 2:
        print("Not enough file maps to compare")
        return
    
    # Compare each pair of maps
    map_names = list(all_maps.keys())
    for i in range(len(map_names)):
        for j in range(i+1, len(map_names)):
            name1 = map_names[i]
            name2 = map_names[j]
            map1 = all_maps[name1]
            map2 = all_maps[name2]
            
            # Compare file paths
            files1 = set(map1.keys())
            files2 = set(map2.keys())
            common_files = files1.intersection(files2)
            unique_to_1 = files1 - files2
            unique_to_2 = files2 - files1
            
            print(f"\nComparing {name1} vs {name2}:")
            print(f"- {name1} has {len(files1)} files")
            print(f"- {name2} has {len(files2)} files")
            print(f"- Files in common: {len(common_files)}")
            print(f"- Files unique to {name1}: {len(unique_to_1)}")
            print(f"- Files unique to {name2}: {len(unique_to_2)}")
            
            # Check trigger attribute for files in common
            trigger_differences = 0
            if common_files:
                print("\nChecking 'with_trigger' attribute for common files:")
                for file_path in common_files:
                    if "with_trigger" in map1[file_path] and "with_trigger" in map2[file_path]:
                        trigger1 = map1[file_path]["with_trigger"]
                        trigger2 = map2[file_path]["with_trigger"]
                        if trigger1 != trigger2:
                            trigger_differences += 1
                
                print(f"- Files with different 'with_trigger' values: {trigger_differences}")
            
            # Show sample paths unique to each
            if unique_to_1:
                print(f"\nSample paths unique to {name1} (first 5):")
                for path in list(unique_to_1)[:5]:
                    trigger = map1[path].get("with_trigger", "unknown")
                    print(f"- {path} (with_trigger={trigger})")
                    
            if unique_to_2:
                print(f"\nSample paths unique to {name2} (first 5):")
                for path in list(unique_to_2)[:5]:
                    trigger = map2[path].get("with_trigger", "unknown")
                    print(f"- {path} (with_trigger={trigger})")

def analyze_results_files(results_dir="codeql_output"):
    """
    Compare the SARIF results from different analyses.
    """
    base_dir = Path(results_dir)
    
    # Find all SARIF result files
    sarif_files = []
    for pattern in ["**/results_with_triggers/**/*.sarif", "**/results_without_triggers/**/*.sarif"]:
        sarif_files.extend(base_dir.glob(pattern))
    
    if not sarif_files:
        print(f"No SARIF files found in {base_dir}")
        return
        
    print(f"Found {len(sarif_files)} SARIF files:")
    
    sarif_data = {}
    
    # Load each SARIF file
    for sarif_path in sarif_files:
        # Extract the parent directory name as a key
        trigger_type = "with_triggers" if "with_triggers" in str(sarif_path) else "without_triggers"
        print(f"- {trigger_type}: {sarif_path}")
        
        try:
            with open(sarif_path, 'r') as f:
                sarif = json.load(f)
                sarif_data[trigger_type] = sarif
        except Exception as e:
            print(f"  Error loading {sarif_path}: {e}")
    
    # Compare results
    if len(sarif_data) < 2:
        print("Not enough SARIF files to compare")
        return
    
    print("\nAnalysis of SARIF results:")
    print("=========================")
    
    # Extract and compare results from each SARIF file
    for trigger_type, sarif in sarif_data.items():
        result_count = 0
        rule_counts = {}
        
        # Process each run in the SARIF file
        for run in sarif.get("runs", []):
            for result in run.get("results", []):
                result_count += 1
                rule_id = result.get("ruleId", "unknown")
                rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
        
        print(f"\n{trigger_type} results:")
        print(f"- Total alerts: {result_count}")
        print(f"- Unique rules: {len(rule_counts)}")
        
        # Show top rules by count
        if rule_counts:
            print("- Top rules:")
            sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)
            for rule, count in sorted_rules[:5]:
                print(f"  - {rule}: {count}")

def main():
    print("CodeQL Analysis Diagnostic")
    print("=========================\n")
    
    base_dir = "codeql_output"
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    
    print(f"Analyzing CodeQL output in {base_dir}\n")
    
    # Analyze file maps
    print("\n=== File Map Analysis ===\n")
    analyze_file_maps(base_dir)
    
    # Analyze results
    print("\n=== Results Analysis ===\n")
    analyze_results_files(base_dir)

if __name__ == "__main__":
    main()