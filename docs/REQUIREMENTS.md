# Requirements Documentation

This document outlines all the dependencies required for the Imou Life integration project.

## Core Dependencies

### Runtime Dependencies (manifest.json)
- **imouapi==1.0.15** - Core Imou API client library

### Development Dependencies (requirements_dev.txt)
- **homeassistant** - Home Assistant core for development
- **voluptuous** - Data validation library used in camera.py
- **imouapi==1.0.15** - Core Imou API client library

### Testing Dependencies (requirements_test.txt)
- **homeassistant>=2024.2.0** - Home Assistant core for testing (Python 3.11-3.13 compatible)
- **pytest>=8.0.0** - Testing framework
- **pytest-asyncio>=0.24.0** - Async testing support
- **pytest-cov>=6.0.0** - Coverage testing
- **coverage>=7.4.0** - Code coverage tool
- **imouapi==1.0.15** - Core Imou API client library

## Linting and Code Quality

### Pre-commit Hooks (.pre-commit-config.yaml)
- **pre-commit-hooks** - Basic git hooks (trailing whitespace, end of files, etc.)
- **black** - Code formatter
- **flake8** - Linter
- **isort** - Import sorter
- **codespell** - Spell checker

## Platform-Specific Dependencies

### Linux (CI/CD)
- **Standard Python packages only** - No system dependencies required

### Windows (Development)
- **Standard Python packages only** - No system dependencies required

## Installation Notes

### For Development
```bash
        pip install -r config/requirements_dev.txt
```

### For Testing
```bash
        pip install -r config/requirements_test.txt
```

### For CI/CD
The GitHub Actions workflow automatically installs Python packages.

## Version Constraints

### Python Version Support
- **Python 3.11**: Home Assistant 2023.3+ (our requirement: 2024.2.0+)
- **Python 3.12**: Home Assistant 2024.2+ (our requirement: 2024.2.0+)
- **Python 3.13**: Home Assistant 2024.12+ (our requirement: 2024.2.0+)

### Development Dependencies
- **pip**: 25.2.0
- **pre-commit**: 4.3.0
- **black**: 25.1.0
- **flake8**: 7.3.0
- **isort**: 6.0.1

## Testing Strategy

### Camera Component Testing
Due to compatibility issues with the `turbojpeg` package across different Python versions and platforms:

1. **Basic functionality tests** - Test camera component structure and imports
2. **Integration tests** - Test camera component within the Home Assistant framework
3. **Mock-based tests** - Use mocks for camera-specific functionality
4. **CI/CD testing** - Full test suite runs on Linux runners

### Platform-Specific Testing
- **Linux/macOS**: Full test suite available
- **Windows**: Limited pytest functionality due to platform dependencies
- **CI/CD**: Full testing on Linux runners with Python 3.11, 3.12, and 3.13

## Troubleshooting

### Camera Component Issues
If you encounter issues with camera component testing:

1. **Use the test runner script**: `python tools/validation/run_tests.py`
2. **Focus on basic tests**: The core functionality tests should work
3. **Check CI logs**: Full tests run successfully on Linux in GitHub Actions

### Import Errors
If you get import errors:

1. **Ensure virtual environment is activated**
2. **Install requirements**: `pip install -r config/requirements_dev.txt`
3. **Check Python version**: Use Python 3.11+ (3.11, 3.12, or 3.13 supported)

### Platform-Specific Testing
- **Linux/macOS**: Full test suite available
- **Windows**: Limited pytest functionality due to platform dependencies
- **CI/CD**: Full testing on Linux runners
