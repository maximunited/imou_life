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

## Linting and Code Quality

### Pre-commit Hooks (.pre-commit-config.yaml)
- **black** - Code formatter
- **flake8** - Linter
- **isort** - Import sorter
- **codespell** - Spell checker

## Import Analysis

### Standard Library Imports
- `collections.abc` - Abstract base classes
- `logging` - Logging framework
- `asyncio` - Async I/O support
- `datetime` - Date/time utilities
- `typing` - Type hints
- `unittest.mock` - Testing mocks

### Home Assistant Imports
- `homeassistant.components.*` - HA component interfaces
- `homeassistant.config_entries` - Configuration management
- `homeassistant.core` - Core HA functionality
- `homeassistant.helpers.*` - Helper utilities
- `homeassistant.exceptions` - HA exceptions

### Third-party Imports
- `imouapi.*` - Imou API client and utilities
- `voluptuous` - Data validation
- `pytest.*` - Testing framework

## Installation Commands

### Development Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install development dependencies
pip install -r requirements_dev.txt

# Install linting tools
pip install black flake8 isort codespell pre-commit

# Install pre-commit hooks
pre-commit install
```

### Testing Environment
```bash
# Install test dependencies
pip install -r requirements_test.txt
```

## Version Compatibility

- **Python**: 3.9+ (3.13 recommended)
- **Home Assistant**: 2025.8.2 (latest stable)
- **imouapi**: 1.0.15 (exact version required)
- **pytest-homeassistant-custom-component**: 0.13.271

## Dependency Management

### Adding New Dependencies
1. Add to appropriate requirements file:
   - `requirements_dev.txt` for development dependencies
   - `requirements_test.txt` for testing dependencies
   - `manifest.json` for runtime dependencies

2. Install in virtual environment:
   ```bash
   pip install -r requirements_dev.txt
   pip install -r requirements_test.txt
   ```

3. Update this documentation

### Updating Dependencies
1. Update version in requirements file
2. Install updated package: `pip install -r requirements_*.txt`
3. Test functionality
4. Update this documentation

## Troubleshooting

### Import Errors
- Ensure virtual environment is activated
- Verify all requirements are installed: `pip list`
- Check Python version compatibility

### Version Conflicts
- Use exact versions for critical dependencies (e.g., `imouapi==1.0.15`)
- Use version ranges for flexible dependencies (e.g., `pytest>=8.0.0`)

### Missing Dependencies
- Check `pip list` output
- Reinstall requirements: `pip install -r requirements_*.txt`
- Clear pip cache if needed: `pip cache purge`
