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

```python
from php_app_lib_classifier import LibraryClassifier

result = LibraryClassifier.classify("/path/to/php/app", output_json=True)
print(result)
```

- `LibraryClassifier.classify(path, output_json=True)`: Analyze the specified PHP application and return the results (optionally as JSON).

## Requirements

- Docker

## Architecture

- **LibraryClassifier**: Core logic for detecting and classifying PHP libraries
- **CLI Interface**: Simple command-line usage via Docker
- **JSON Output**: Structured results for downstream processing
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