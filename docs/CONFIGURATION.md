# Configuration Guide

This guide covers the configuration files and settings for the Imou Life project.

## 📁 Configuration Files

### Project Configuration

- **`pyproject.toml`** - Project metadata and build settings
- **`setup.cfg`** - Python package configuration
- **`.pre-commit-config.yaml`** - Pre-commit hooks configuration

### Testing Configuration

- **`config/.coveragerc`** - Coverage reporting configuration
- **`config/setup.cfg`** - Test and build configuration

### Dependencies

- **`config/requirements.txt`** - Runtime dependencies
- **`config/requirements_dev.txt`** - Development dependencies
- **`config/requirements_test.txt`** - Testing dependencies

## 🔧 Key Settings

### Coverage Configuration

```ini
# config/.coveragerc
[run]
source = custom_components/imou_life
omit = 
    */tests/*
    */__pycache__/*
    */venv/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

## 🚀 Environment Setup

### Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\tools\scripts\activate_venv.ps1

# Activate (Linux/macOS)
source venv/bin/activate
```

### Install Dependencies

```bash
# Development dependencies
pip install -r config/requirements_dev.txt

# Testing dependencies
pip install -r config/requirements_test.txt

# Runtime dependencies
pip install -r config/requirements.txt
```

## 📊 Testing Configuration

### Pytest Settings

```ini
# config/setup.cfg
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
```

### Coverage Targets

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%+
- **Critical Paths**: 95%+

## 🔍 Customization

### Adding New Dependencies

1. **Add to requirements file**:
   ```bash
   echo "new-package==1.0.0" >> config/requirements_dev.txt
   ```

2. **Install and test**:
   ```bash
   pip install -r config/requirements_dev.txt
   python -m pytest tests/
   ```

3. **Commit changes**:
   ```bash
   git add config/requirements_dev.txt
   git commit -m "Add new-package dependency"
   ```

### Modifying Test Configuration

1. **Edit `config/setup.cfg`** for pytest settings
2. **Edit `config/.coveragerc`** for coverage settings
3. **Run tests** to verify changes

## 🚨 Common Issues

### Configuration Errors

```bash
# Check configuration syntax
python -c "import configparser; configparser.ConfigParser().read('config/.coveragerc')"

# Validate YAML
python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml'))"
```

### Missing Dependencies

```bash
# Reinstall all dependencies
pip install -r config/requirements_dev.txt
pip install -r config/requirements_test.txt
```

## 📚 Additional Resources

- **[Python Configuration Guide](https://docs.python.org/3/library/configparser.html)**
- **[Pytest Configuration](https://docs.pytest.org/en/stable/customize.html)**
- **[Coverage.py Configuration](https://coverage.readthedocs.io/en/latest/config.html)**

---

**Need help with configuration?** Check the [Development Guide](DEVELOPMENT.md) or open an [issue](https://github.com/maximunited/imou_life/issues).
