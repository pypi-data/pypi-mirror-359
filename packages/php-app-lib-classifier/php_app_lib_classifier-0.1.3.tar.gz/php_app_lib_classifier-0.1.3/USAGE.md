# PHP App Library Classifier Usage Guide

## Quick Start

### 1. Installation

```bash
pip install php-app-lib-classifier
```

### 2. Basic Usage

```python
from php_app_lib_classifier import classify

# Analyze PHP project
result = classify("/path/to/your/php/project")
print(f"Project type: {result.project_type}")
```

## Detailed Usage

### Function Interface

The `classify()` function provides the simplest way to use the library:

```python
from php_app_lib_classifier import classify

# Basic usage
result = classify("/path/to/php/project")

# Get JSON output
json_result = classify("/path/to/php/project", output_json=True)

# Enable verbose logging
result = classify("/path/to/php/project", verbose=True)
```

### Parameters

- `path` (str): Path to the PHP project
- `output_json` (bool, optional): Whether to return JSON string, defaults to False
- `verbose` (bool, optional): Whether to enable verbose logging, defaults to False

### Return Values

#### Object Output (output_json=False)

Returns an `AnalysisResult` object with the following attributes:

```python
result = classify("/path/to/php/project")

# Basic attributes
print(result.path)                    # Project path
print(result.project_type.value)      # Project type: "Library", "Web Application", "Hybrid/Unclear"
print(result.library_score)           # Library score
print(result.webapp_score)            # Web application score
print(result.total_score)             # Total score

# Computed attributes
print(result.normalized_library_score)  # Normalized library score (0-1)
print(result.normalized_webapp_score)   # Normalized web application score (0-1)

# Confidence level
confidence_level, color = result.get_confidence_level()
print(confidence_level.value)  # "High", "Medium", "Low"
print(color.value)            # "green", "yellow", "red"

# Found indicators
for indicator in result.indicators_found:
    print(f"- {indicator.name}: {indicator.description}")
```

#### JSON Output (output_json=True)

Returns a formatted JSON string:

```json
{
  "path": "/path/to/php/project",
  "project_type": "Library",
  "library_score": 2.5,
  "webapp_score": 0.3,
  "total_score": 2.8,
  "normalized_library_score": 0.89,
  "normalized_webapp_score": 0.11,
  "confidence_level": "High",
  "indicators_found": [
    "composer_type_library",
    "has_psr4_autoload",
    "src_directory"
  ]
}
```

## Usage Examples

### Example 1: Basic Analysis

```python
from php_app_lib_classifier import classify

def analyze_project(project_path):
    try:
        result = classify(project_path)
        
        print(f"Project: {result.path}")
        print(f"Type: {result.project_type}")
        print(f"Confidence: {result.get_confidence_level()[0]}")
        print(f"Library score: {result.library_score}")
        print(f"Web application score: {result.webapp_score}")
        
        if result.indicators_found:
            print("Found indicators:")
            for indicator in result.indicators_found:
                print(f"  - {indicator.name}")
                
    except FileNotFoundError:
        print(f"Error: Path does not exist - {project_path}")
    except Exception as e:
        print(f"Analysis error: {e}")

# Usage
analyze_project("/path/to/php/project")
```

### Example 2: Batch Analysis

```python
from php_app_lib_classifier import classify
import os

def batch_analyze(projects_dir):
    results = []
    
    for item in os.listdir(projects_dir):
        item_path = os.path.join(projects_dir, item)
        if os.path.isdir(item_path):
            try:
                result = classify(item_path)
                confidence_level, _ = result.get_confidence_level()
                results.append({
                    'name': item,
                    'type': result.project_type.value,
                    'confidence': confidence_level.value,
                    'library_score': result.library_score,
                    'webapp_score': result.webapp_score
                })
            except Exception as e:
                print(f"Error analyzing {item}: {e}")
    
    return results

# Usage
projects = batch_analyze("/path/to/projects/directory")
for project in projects:
    print(f"{project['name']}: {project['type']} (confidence: {project['confidence']})")
```

### Example 3: JSON Output for API

```python
from php_app_lib_classifier import classify
import json

def get_project_analysis_json(project_path):
    try:
        json_result = classify(project_path, output_json=True)
        return json.loads(json_result)
    except Exception as e:
        return {
            "error": str(e),
            "path": project_path
        }

# Usage
result = get_project_analysis_json("/path/to/php/project")
print(json.dumps(result, indent=2, ensure_ascii=False))
```

## Enum Types

The library uses Enums for type safety and better code organization:

```python
from php_app_lib_classifier import ProjectType, ConfidenceLevel, ConfidenceColor

# Project types
ProjectType.LIBRARY           # "Library"
ProjectType.WEB_APPLICATION   # "Web Application"
ProjectType.HYBRID_UNCLEAR    # "Hybrid/Unclear"

# Confidence levels
ConfidenceLevel.HIGH          # "High"
ConfidenceLevel.MEDIUM        # "Medium"
ConfidenceLevel.LOW           # "Low"

# Confidence colors
ConfidenceColor.GREEN         # "green"
ConfidenceColor.YELLOW        # "yellow"
ConfidenceColor.RED           # "red"
```

## Project Type Explanation

- **Library**: Library project, mainly used to be referenced by other projects
- **Web Application**: Web application project, mainly used to provide web services
- **Hybrid/Unclear**: Hybrid type or projects that cannot be clearly classified

## Confidence Level Explanation

- **High**: High confidence, classification result is reliable
- **Medium**: Medium confidence, classification result has some reference value
- **Low**: Low confidence, classification result is for reference only

## Error Handling

```python
from php_app_lib_classifier import classify

try:
    result = classify("/path/to/php/project")
    # Process result
except FileNotFoundError:
    print("Project path does not exist")
except Exception as e:
    print(f"Error occurred during analysis: {e}")
```

## Performance Notes

- Analysis process is asynchronous and can complete quickly even for large projects
- Supports concurrent analysis of multiple indicators
- Recommended to use `verbose=False` in production environment for best performance 