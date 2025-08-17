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

## Development Workflow

### Running Linters

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run individual tools
black custom_components/imou_life/
flake8 custom_components/imou_life/
isort custom_components/imou_life/
codespell custom_components/imou_life/
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=custom_components/imou_life
```

### Code Quality

All code must pass the pre-commit hooks before committing:

- **black**: Code formatting
- **flake8**: Linting and style checking
- **isort**: Import sorting
- **codespell**: Spelling check

## Project Structure

```
imou_life/
├── custom_components/imou_life/    # Main integration code
├── tests/                          # Test files
├── requirements_dev.txt            # Development dependencies
├── requirements_test.txt           # Test dependencies
├── .pre-commit-config.yaml        # Pre-commit configuration
└── setup.cfg                      # Project configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all pre-commit hooks pass
5. Submit a pull request

## Troubleshooting

### Import Errors

If you get import errors for `homeassistant`, ensure the virtual environment is activated and dependencies are installed:

```bash
pip install -r requirements_dev.txt
```

### Pre-commit Issues

If pre-commit fails, try:

```bash
pre-commit clean
pre-commit install
pre-commit run --all-files
```

### Virtual Environment Issues

If the virtual environment becomes corrupted:

```bash
# Remove and recreate
rm -rf venv
python -m venv venv
# Then follow setup steps 3-4
```
