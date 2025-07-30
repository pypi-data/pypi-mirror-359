"""
php_app_lib_classifier
---------------------
A modern, async PHP app/library classifier package.

php_app_lib_classifier package initialization.
"""

from .analysis import PHPProjectAnalyzer, AnalysisResult
from .enums import ProjectType, ConfidenceLevel, ConfidenceColor

# Alias for backward compatibility and expected API
LibraryClassifier = PHPProjectAnalyzer

def classify(path: str, output_json: bool = False, verbose: bool = False):
    """
    Classify a PHP project as either a library or web application.
    
    This is a convenience function that provides a simple interface for classification.
    
    Args:
        path: Path to the PHP project directory
        output_json: If True, return results as JSON string
        verbose: Enable verbose logging
        
    Returns:
        AnalysisResult or JSON string depending on output_json parameter
        
    Example:
        >>> from php_app_lib_classifier import classify
        >>> result = classify("/path/to/php/project")
        >>> print(result.project_type)
        >>> 
        >>> # Or get JSON output
        >>> json_result = classify("/path/to/php/project", output_json=True)
        >>> print(json_result)
    """
    return LibraryClassifier.classify(path, output_json=output_json, verbose=verbose)

__all__ = ['LibraryClassifier', 'PHPProjectAnalyzer', 'AnalysisResult', 'classify', 'ProjectType', 'ConfidenceLevel', 'ConfidenceColor']
