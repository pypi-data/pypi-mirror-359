#!/usr/bin/env python3
"""
Example: Using Enum types from php_app_lib_classifier
"""

from php_app_lib_classifier import classify, ProjectType, ConfidenceLevel, ConfidenceColor
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python enum_usage.py <PHP project path>")
        print("Example: python enum_usage.py /path/to/php/project")
        sys.exit(1)
    
    path = sys.argv[1]
    
    try:
        print(f"Analyzing project: {path}")
        result = classify(path)
        
        print("\n=== Analysis Result ===")
        print(f"Project path: {result.path}")
        
        # Using Enum types
        print(f"\nProject type (Enum): {result.project_type}")
        print(f"Project type (value): {result.project_type.value}")
        
        # Check specific project type
        if result.project_type == ProjectType.LIBRARY:
            print("✅ This is a library project")
        elif result.project_type == ProjectType.WEB_APPLICATION:
            print("🌐 This is a web application")
        elif result.project_type == ProjectType.HYBRID_UNCLEAR:
            print("❓ This is a hybrid or unclear project type")
        
        # Confidence level using Enums
        confidence_level, confidence_color = result.get_confidence_level()
        print(f"\nConfidence level (Enum): {confidence_level}")
        print(f"Confidence level (value): {confidence_level.value}")
        print(f"Confidence color (Enum): {confidence_color}")
        print(f"Confidence color (value): {confidence_color.value}")
        
        # Check confidence level
        if confidence_level == ConfidenceLevel.HIGH:
            print("🟢 High confidence in classification")
        elif confidence_level == ConfidenceLevel.MEDIUM:
            print("🟡 Medium confidence in classification")
        elif confidence_level == ConfidenceLevel.LOW:
            print("🔴 Low confidence in classification")
        
        # Scores
        print(f"\nScores:")
        print(f"  Library score: {result.library_score}")
        print(f"  Web application score: {result.webapp_score}")
        print(f"  Total score: {result.total_score}")
        
        # Indicators
        if result.indicators_found:
            print(f"\nFound indicators ({len(result.indicators_found)}):")
            for indicator in result.indicators_found:
                print(f"  - {indicator.name}: {indicator.description}")
        
    except FileNotFoundError:
        print(f"Error: Path does not exist - {path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error occurred during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 