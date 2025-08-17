# Development Setup

This guide will help you set up a development environment for the Imou Life integration.

## Prerequisites

- Python 3.9+ (3.13 recommended)
- Git
- PowerShell (Windows) or Bash (Linux/macOS)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/maximunited/imou_life.git
cd imou_life
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements_dev.txt
pip install black flake8 isort codespell pre-commit
```

### 5. Install Pre-commit Hooks

```bash
pre-commit install
```

## Testing

### Platform-Specific Testing

**Note**: The full pytest suite may not work on Windows due to platform-specific dependencies (specifically the `resource` module). This is normal and expected.

### Running Tests

#### Option 1: Test Runner Script (Recommended for Windows)
```bash
python run_tests.py
```

This script will:
- Run basic import and structure tests
- Attempt to run pytest with minimal configuration
- Provide clear feedback about what's working

#### Option 2: Direct Pytest (Linux/macOS)
```bash
pytest tests/ -v
```

#### Option 3: Pre-commit Hooks
```bash
pre-commit run --all-files
```

## Code Quality

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

- **black**: Code formatting
- **flake8**: Linting
- **isort**: Import sorting
- **codespell**: Spelling checks

### Manual Code Quality Checks

```bash
# Format code
black custom_components/imou_life/

# Check linting
flake8 custom_components/imou_life/

# Sort imports
isort custom_components/imou_life/
```

## Troubleshooting

### Windows-Specific Issues

If you encounter issues with pytest on Windows:

1. **Use the test runner script**: `python run_tests.py`
2. **Focus on basic tests**: The core functionality tests should work
3. **CI/CD**: Tests run successfully on Linux in GitHub Actions

### Import Errors

If you get import errors:

1. **Ensure virtual environment is activated**
2. **Install requirements**: `pip install -r requirements_dev.txt`
3. **Check Python version**: Use Python 3.9+ (3.13 recommended)

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Run tests**: `python run_tests.py`
5. **Run pre-commit**: `pre-commit run --all-files`
6. **Submit a pull request**

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Pre-commit**: Code quality checks
- **Tests**: Automated testing (Linux)
- **HACS**: Integration validation
- **Hassfest**: Home Assistant manifest validation

All checks must pass before merging.
