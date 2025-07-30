#!/usr/bin/env python3
"""
Example: Using the classify function from php_app_lib_classifier
"""

from php_app_lib_classifier import classify
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python usage.py <PHP project path> [--json]")
        print("Example: python usage.py /path/to/php/project")
        print("Example: python usage.py /path/to/php/project --json")
        sys.exit(1)
    
    path = sys.argv[1]
    output_json = "--json" in sys.argv
    
    try:
        print(f"Analyzing project: {path}")
        
        if output_json:
            # JSON output
            result = classify(path, output_json=True)
            print("Analysis result (JSON):")
            print(result)
        else:
            # Object output
            result = classify(path)
            print("Analysis result:")
            print(f"  Project path: {result.path}")
            print(f"  Project type: {result.project_type.value}")
            print(f"  Library score: {result.library_score}")
            print(f"  Web application score: {result.webapp_score}")
            print(f"  Total score: {result.total_score}")
            confidence_level, confidence_color = result.get_confidence_level()
            print(f"  Confidence: {confidence_level.value}")
            print(f"  Found indicators: {[indicator.name for indicator in result.indicators_found]}")
            
    except FileNotFoundError:
        print(f"Error: Path does not exist - {path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error occurred during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 