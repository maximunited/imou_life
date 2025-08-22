# Testing Guide

This guide covers how to run tests, understand the testing structure, and ensure code quality in the Imou Life project.

## 🏗️ Test Structure

```
tests/
├── 📁 unit/                    # Unit tests for individual components
│   ├── test_init.py           # Integration initialization tests
│   ├── test_config_flow.py    # Configuration flow tests
│   └── test_switch.py         # Switch entity tests
├── 📁 integration/             # Integration tests (end-to-end)
├── 📁 fixtures/                # Test data and mock objects
│   ├── mocks.py               # Mock objects and fixtures
│   └── const.py               # Test constants
├── conftest.py                 # Pytest configuration and fixtures
└── __init__.py                 # Package initialization
```

## 🚀 Quick Start

### Prerequisites

1. **Activate virtual environment**:
   ```bash
   # Windows
   .\tools\scripts\activate_venv.bat
   
   # PowerShell
   .\tools\scripts\activate_venv.ps1
   
   # Linux/macOS
   source venv/bin/activate
   ```

2. **Install test dependencies**:
   ```bash
   pip install -r config/requirements_test.txt
   ```

### Running Tests

#### Basic Test Execution

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=custom_components/imou_life
```

#### Test Categories

```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# Specific test file
python -m pytest tests/unit/test_switch.py

# Specific test function
python -m pytest tests/unit/test_switch.py::test_switch_turn_on
```

#### Coverage Reporting

```bash
# Generate coverage report
python -m pytest tests/ --cov=custom_components/imou_life --cov-report=html

# View coverage in browser
# Open tools/htmlcov/index.html

# Generate XML coverage report
python -m pytest tests/ --cov=custom_components/imou_life --cov-report=xml
```

## 🐳 Docker Testing

For consistent testing environments, use Docker:

```bash
# Run tests in Docker
.\tools\scripts\run_docker_tests.ps1

# Manual Docker execution
docker-compose -f tools/docker/docker-compose.test.yml up --build

# Run specific tests in Docker
docker-compose -f tools/docker/docker-compose.test.yml run --rm test python -m pytest tests/unit/
```

## 🧪 Test Types

### Unit Tests

Unit tests focus on testing individual functions and classes in isolation:

- **Location**: `tests/unit/`
- **Scope**: Individual functions, methods, and classes
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution

Example:
```python
def test_switch_turn_on():
    """Test that switch turns on correctly."""
    switch = ImouSwitch("test_switch", "test_device")
    switch.turn_on()
    assert switch.is_on is True
```

### Integration Tests

Integration tests verify that components work together:

- **Location**: `tests/integration/`
- **Scope**: Component interactions and workflows
- **Dependencies**: Real or realistic test data
- **Speed**: Slower than unit tests

### Fixtures

Test fixtures provide reusable test data and mock objects:

- **Location**: `tests/fixtures/`
- **Purpose**: Shared test data, mock objects, and utilities
- **Usage**: Imported by test files

## 🔧 Test Configuration

### Pytest Configuration

The project uses `conftest.py` for shared pytest configuration:

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_imou_api():
    """Mock Imou API client."""
    api = Mock()
    api.get_devices.return_value = []
    return api
```

### Coverage Configuration

Coverage settings are configured in `config/.coveragerc`:

```ini
[run]
source = custom_components/imou_life
omit = 
    */tests/*
    */__pycache__/*
    */venv/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## 📊 Test Results

### Coverage Reports

After running tests with coverage, view results:

- **HTML Report**: `tools/htmlcov/index.html`
- **XML Report**: `tools/coverage.xml`
- **Console Output**: Coverage summary in terminal

### Test Results

Test results are stored in:

- **Test Results**: `tools/test-results/`
- **Coverage Data**: `tools/coverage/`
- **Pytest Cache**: `tools/.pytest_cache/`

## 🚨 Common Issues

### Import Errors

If you encounter import errors:

```bash
# Ensure you're in the project root
cd /path/to/imou_life

# Activate virtual environment
.\tools\scripts\activate_venv.ps1

# Install dependencies
pip install -r config/requirements_test.txt
```

### Missing Dependencies

If tests fail due to missing dependencies:

```bash
# Install all development dependencies
pip install -r config/requirements_dev.txt
pip install -r config/requirements_test.txt

# Or install specific packages
pip install pytest pytest-cov pytest-mock
```

### Docker Issues

If Docker tests fail:

```bash
# Clean up Docker containers
docker-compose -f tools/docker/docker-compose.test.yml down

# Rebuild Docker image
docker-compose -f tools/docker/docker-compose.test.yml build --no-cache

# Check Docker logs
docker-compose -f tools/docker/docker-compose.test.yml logs
```

## 📝 Writing Tests

### Test Naming Convention

- **File names**: `test_*.py`
- **Test functions**: `test_*`
- **Descriptive names**: Use clear, descriptive test names

### Test Structure

```python
def test_function_name():
    """Brief description of what the test verifies."""
    # Arrange - Set up test data
    test_data = "test_value"
    
    # Act - Execute the function being tested
    result = function_under_test(test_data)
    
    # Assert - Verify the expected outcome
    assert result == "expected_value"
```

### Mocking

Use mocks to isolate units under test:

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test using mocked dependencies."""
    mock_api = Mock()
    mock_api.get_data.return_value = {"key": "value"}
    
    with patch('module.api_client', mock_api):
        result = function_under_test()
        assert result == {"key": "value"}
```

## 🔍 Debugging Tests

### Verbose Output

```bash
# Increase verbosity
python -m pytest tests/ -v -s

# Show local variables on failure
python -m pytest tests/ --tb=long
```

### Debugging Specific Tests

```bash
# Run single test with debugger
python -m pytest tests/unit/test_switch.py::test_switch_turn_on -s

# Add breakpoint() in test code for debugging
```

### Test Isolation

```bash
# Run tests in isolation
python -m pytest tests/ --maxfail=1

# Stop on first failure
python -m pytest tests/ -x
```

## 📚 Additional Resources

- **[Pytest Documentation](https://docs.pytest.org/)** - Official pytest guide
- **[Coverage.py Documentation](https://coverage.readthedocs.io/)** - Coverage tool guide
- **[Python Testing Guide](https://docs.python-guide.org/writing/tests/)** - Python testing best practices

---

**Need help with testing?** Check the [Development Guide](DEVELOPMENT.md) or open an [issue](https://github.com/maximunited/imou_life/issues) on GitHub.
