# PHP App Library Classifier

Analyze and classify PHP libraries used in any project directory with a modern, containerized tool. Outputs structured JSON for easy integration and analysis.

## Features

- **Automatic library detection** for PHP projects
- **Structured JSON output**
- **Dockerized for easy use**
- **No dependencies on host system**
- **Fast and efficient analysis**

## Usage

### CLI

```sh
php-app-lib-classifier /path/to/php/app [--json] [--verbose]
php-app-lib-classifier version
```

- `/path/to/php/app`: Path to the PHP application to analyze.
- `--json`: Output results in JSON format.
- `--verbose`: Enable verbose logging.

### Docker

```sh
docker run --rm -it -v /path/to/your/php/app:/var/www/html ghcr.io/wangyihang/php-app-lib-classifier:main /var/www/html --json
```

- `/path/to/your/php/app`: Local path to your PHP application.
- The output will be in JSON format.

### Python API

#### Simple Function Interface (Recommended)

```python
from php_app_lib_classifier import classify, ProjectType, ConfidenceLevel

# Get object result
result = classify("/path/to/php/app")
print(f"Project type: {result.project_type.value}")  # Enum value
print(f"Confidence: {result.get_confidence_level()[0].value}")  # Enum value

# Check specific types
if result.project_type == ProjectType.LIBRARY:
    print("This is a library project")

# Get JSON result
json_result = classify("/path/to/php/app", output_json=True)
print(json_result)
```

#### Class Interface

```python
from php_app_lib_classifier import LibraryClassifier

result = LibraryClassifier.classify("/path/to/php/app", output_json=True)
print(result)
```

- `classify(path, output_json=False, verbose=False)`: Simple function interface to analyze PHP applications and return results
- `LibraryClassifier.classify(path, output_json=True)`: Class interface to analyze PHP applications and return results (optionally as JSON)

## Requirements

- Docker

## Architecture

- **LibraryClassifier**: Core logic for detecting and classifying PHP libraries
- **CLI Interface**: Simple command-line usage via Docker
- **JSON Output**: Structured results for downstream processing
- **Enum Types**: Type-safe project types and confidence levels

## Enum Types

The library provides Enum types for better type safety:

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
```
- **Detection Strategies**:
  - Composer dependency analysis
  - File and directory pattern matching
  - Content-based heuristics

## Contributing

- Fork & branch
- Add features or tests
- Ensure all tests pass (if applicable)
- Submit a pull request

## License

MIT License. See LICENSE.

## Changelog

### v0.2.0
- Improved detection logic, structured output, and Docker usability

### v0.1.0
- Initial release