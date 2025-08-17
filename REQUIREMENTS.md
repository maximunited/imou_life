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
- **pytest-homeassistant-custom-component==0.13.271** - Home Assistant testing framework
- **pytest>=8.0.0** - Testing framework
- **pytest-asyncio>=0.21.0** - Async testing support
- **pytest-cov>=6.0.0** - Coverage testing
- **coverage>=7.0.0** - Code coverage tool
- **turbojpeg==0.0.2** - JPEG processing library for camera component testing

## Linting and Code Quality

### Pre-commit Hooks (.pre-commit-config.yaml)
- **pre-commit-hooks** - Basic git hooks (trailing whitespace, end of files, etc.)
- **black** - Code formatter
- **flake8** - Linter
- **isort** - Import sorter
- **codespell** - Spell checker

## Platform-Specific Dependencies

### Linux (CI/CD)
- **libturbojpeg0-dev** - System package for turbojpeg development headers

### Windows (Development)
- **turbojpeg** - Python package (may have installation challenges)

## Installation Notes

### For Development
```bash
pip install -r requirements_dev.txt
```

### For Testing
```bash
pip install -r requirements_test.txt
```

### For CI/CD
The GitHub Actions workflow automatically installs system dependencies and Python packages.

## Version Constraints

All dependencies are pinned to specific versions to ensure reproducible builds:
- **pip**: 25.2.0
- **pre-commit**: 4.3.0
- **black**: 25.1.0
- **flake8**: 7.3.0
- **isort**: 6.0.1
- **turbojpeg**: 0.0.2

## Troubleshooting

### turbojpeg Installation Issues
If you encounter issues installing turbojpeg on Windows:
1. Try installing from a wheel: `pip install turbojpeg --only-binary=all`
2. Use the test runner script: `python run_tests.py` (avoids camera component import)
3. Focus on basic functionality tests that don't require camera components

### Platform-Specific Testing
- **Linux/macOS**: Full test suite available
- **Windows**: Limited pytest functionality due to platform dependencies
- **CI/CD**: Full testing on Linux runners
