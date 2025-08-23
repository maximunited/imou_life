# Development Guide - Imou Life Integration

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
[![Buy Me a Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-%23FFDD00.svg?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/maxim_united)
[![Coverage Status](https://coveralls.io/repos/github/maximunited/imou_life/badge.svg?branch=master)](https://coveralls.io/github/maximunited/imou_life?branch=master)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

This guide covers development setup, testing, and contribution guidelines for the Imou Life Home Assistant integration.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Testing](#testing)
5. [Code Quality](#code-quality)
6. [Automated Workflows](#automated-workflows)
7. [Version Management](#version-management)
8. [Contributing Guidelines](#contributing-guidelines)

## 🔑 Prerequisites

Before setting up the development environment, ensure you have:

- **Python**: 3.9 or later
- **Home Assistant**: 2023.8.0 or later
- **Git**: Latest version
- **Docker**: For containerized testing (optional)

## 🛠️ Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/maximunited/imou_life.git
cd imou_life
```

### 2. Set Up Virtual Environment

#### Windows
```bash
# Command Prompt
.\tools\scripts\activate_venv.bat

# PowerShell
.\tools\scripts\activate_venv.ps1
```

#### Linux/macOS
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Development dependencies
pip install -r config/requirements_dev.txt

# Test dependencies
pip install -r config/requirements_test.txt
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

## 📁 Project Structure

```
imou_life/
├── 📁 custom_components/imou_life/    # Home Assistant integration
│   ├── __init__.py                    # Integration setup and coordinator
│   ├── config_flow.py                 # Configuration flow
│   ├── entity.py                      # Base entity class
│   ├── camera.py                      # Camera platform
│   ├── switch.py                      # Switch platform
│   ├── sensor.py                      # Sensor platform
│   ├── binary_sensor.py               # Binary sensor platform
│   ├── select.py                      # Select platform
│   ├── button.py                      # Button platform
│   ├── siren.py                       # Siren platform
│   ├── coordinator.py                 # Data coordinator
│   ├── diagnostics.py                 # Diagnostics support
│   ├── const.py                       # Constants and configuration
│   └── manifest.json                  # Integration manifest
├── 📁 tools/                          # Development and utility tools
│   ├── 📁 scripts/                    # PowerShell/Batch scripts
│   ├── 📁 docker/                     # Docker testing files
│   └── 📁 validation/                 # Setup validation tools
├── 📁 tests/                          # Test suite
│   ├── 📁 unit/                       # Unit tests
│   ├── 📁 integration/                # Integration tests
│   └── 📁 fixtures/                   # Test data and fixtures
├── 📁 docs/                           # Documentation
├── 📁 scripts/                        # Build and deployment scripts
└── 📁 config/                         # Configuration files
```

## 🧪 Testing

### Running Tests

#### Simple Test Runner (Recommended for Windows)
```bash
# Windows Command Prompt
run_tests.bat

# Windows PowerShell
.\run_tests.ps1

# Direct Python execution
python tools/validation/run_simple_tests.py
```

#### Advanced Test Runner (Linux/macOS)
```bash
# Install test dependencies
pip install -r config/requirements_test.txt

# Run tests with coverage
python run_tests_with_coverage.py

# Run pytest directly
python -m pytest tests/ -v --cov=custom_components/imou_life
```

#### Test Categories
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/           # Unit tests only
python -m pytest tests/integration/    # Integration tests only

# Run with coverage
python -m pytest tests/ --cov=custom_components/imou_life --cov-report=html
```

### Docker Testing

```bash
# Run tests in Docker
.\tools\scripts\run_docker_tests.ps1

# Or manually
docker-compose -f tools/docker/docker-compose.test.yml up --build
```

### Test Coverage

- **Minimum Coverage**: 70% required
- **Coverage Reports**: Generated in HTML and XML formats
- **CI Integration**: Automatically uploaded to Codecov

## ✨ Code Quality

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install hooks
pre-commit install

# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

### Available Hooks

- **black**: Code formatting
- **flake8**: Linting and style checking
- **isort**: Import sorting
- **mypy**: Type checking
- **codespell**: Spell checking

### Code Style

- **Line Length**: 88 characters (black default)
- **Python Version**: 3.9+ compatibility
- **Import Style**: isort configuration
- **Type Hints**: mypy compliance

## 🤖 Automated Workflows

### GitHub Actions

The project uses GitHub Actions for continuous integration and deployment:

#### Test Workflow (`test.yaml`)
- **Triggers**: On push to main/master branch and pull requests
- **Jobs**:
  - Pre-commit checks (code formatting, linting)
  - Python tests with pytest
  - HACS validation
  - Hassfest validation
- **Status**: All jobs must pass for the workflow to succeed

#### CI Release Workflow (`ci-release.yml`)
- **Triggers**: Automatically after successful test workflow completion
- **Purpose**: Creates draft releases when all tests pass
- **Features**:
  - Automatic draft release creation
  - Includes test artifacts (ZIP file)
  - Prevents duplicate releases
  - Only runs on main/master branch

#### Manual Release Workflow (`release.yaml`)
- **Triggers**: Manual workflow dispatch
- **Purpose**: Create draft releases on demand
- **Use case**: When you want to create a release without waiting for CI

#### Tagged Release Workflow (`release.yml`)
- **Triggers**: When git tags are pushed (e.g., `v1.0.0`)
- **Purpose**: Create official releases from version tags
- **Features**: Updates manifest version and creates published releases

## 🏷️ Version Management

### Automated Version Management

Use the `git bump` command for automatic version management:

```bash
# Auto-increment patch version
git bump

# Specific version
git bump 1.0.30

# With custom message
git bump 1.0.30 "Added new feature"
```

### What the Script Does

The `git bump` script automatically:
- Updates `manifest.json` version
- Generates changelog entries
- Commits changes with appropriate message
- Creates and pushes git tags
- Triggers GitHub Actions workflows

### Version Bumping Strategy

- **Patch**: Bug fixes and minor improvements
- **Minor**: New features, backward compatible
- **Major**: Breaking changes

## 🤝 Contributing Guidelines

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Ensure all tests pass**:
   ```bash
   python -m pytest tests/
   ```
6. **Run pre-commit hooks**:
   ```bash
   pre-commit run --all-files
   ```
7. **Submit a pull request**

### Code Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer must approve
3. **Testing**: Changes must include appropriate tests
4. **Documentation**: Update relevant documentation

### Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Detailed description of changes
- **Testing**: Include test results and coverage
- **Breaking Changes**: Clearly mark any breaking changes
- **Related Issues**: Link to relevant issues

### Code Standards

- **Documentation**: Clear docstrings for all functions
- **Type Hints**: Use type hints where appropriate
- **Error Handling**: Proper exception handling
- **Logging**: Appropriate logging levels
- **Testing**: High test coverage for new code

## 📊 Code Coverage

### Coverage Requirements

This project maintains comprehensive test coverage for all custom components:

- **Integration Module** (`__init__.py`) - Setup and coordinator logic
- **Configuration Flow** (`config_flow.py`) - User setup wizard
- **Camera Platform** (`camera.py`) - Video streaming and snapshots
- **Switch Platform** (`switch.py`) - Device controls and toggles
- **Sensor Platform** (`sensor.py`) - Status monitoring
- **Binary Sensor Platform** (`binary_sensor.py`) - Motion detection
- **Select Platform** (`select.py`) - Dropdown controls
- **Button Platform** (`button.py`) - Action triggers
- **Siren Platform** (`siren.py`) - Alarm controls

### Coverage Reports

- **HTML Reports**: Generated in `htmlcov/` directory
- **XML Reports**: Generated for CI integration
- **Coveralls**: Automatic upload on every test run

## 🔧 Development Tools

### Validation Scripts

```bash
# Validate setup
.\tools\scripts\validate_setup.ps1

# Project information
.\tools\scripts\project-info.ps1

# Run tests
.\tools\scripts\run_tests.ps1
```

### Docker Development

```bash
# Build development container
docker build -f tools/docker/Dockerfile.test -t imou_life_test .

# Run tests in container
docker run --rm imou_life_test
```

## 📚 Additional Resources

- **[Performance Guide](PERFORMANCE_TROUBLESHOOTING.md)**: Optimization tips
- **[HACS Guide](HACS_ENHANCEMENTS.md)**: HACS-specific features
- **[Contributing Guide](CONTRIBUTING.md)**: Detailed contribution guidelines
- **[Project Wiki](https://github.com/maximunited/imou_life/wiki)**: Additional development resources

## 🆘 Getting Help

### Development Issues

- **Code Problems**: Check the logs and test output
- **Setup Issues**: Review prerequisites and setup steps
- **GitHub Issues**: Search existing issues or create new ones
- **Discussions**: Use GitHub Discussions for questions

### Support Channels

- **Issues**: [GitHub Issues](https://github.com/maximunited/imou_life/issues)
- **Discussions**: [GitHub Discussions](https://github.com/maximunited/imou_life/discussions)
- **Wiki**: [Project Wiki](https://github.com/maximunited/imou_life/wiki)

---

**Happy coding! 🚀**
