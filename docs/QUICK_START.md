# Quick Start Guide

Get up and running with the Imou Life project in minutes! This guide covers the essential steps to start developing and testing.

## ⚡ 5-Minute Setup

### 1. Clone and Navigate

```bash
git clone https://github.com/maximunited/imou_life.git
cd imou_life
```

### 2. Activate Environment

```bash
# Windows
.\tools\scripts\activate_venv.bat

# PowerShell
.\tools\scripts\activate_venv.ps1

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r config/requirements_dev.txt
pip install -r config/requirements_test.txt
```

### 4. Run Tests

```bash
# Quick test run
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=custom_components/imou_life
```

### 5. Start Developing!

You're ready to go! 🎉

## 🚀 Development Workflow

### Daily Development

```bash
# 1. Activate environment
.\tools\scripts\activate_venv.ps1

# 2. Make your changes
# Edit files in custom_components/imou_life/

# 3. Run tests
python -m pytest tests/unit/

# 4. Check coverage
python -m pytest tests/ --cov=custom_components/imou_life --cov-report=html

# 5. Commit changes
git add .
git commit -m "Your commit message"
```

### Version Management

```bash
# Auto-increment version
.\tools\scripts\git-bump.ps1

# Or specific version
.\tools\scripts\git-bump.ps1 1.0.30

# With message
.\tools\scripts\git-bump.ps1 1.0.30 "Added new feature"
```

## 🧪 Testing Quick Commands

### Basic Testing

```bash
# All tests
python -m pytest tests/

# Unit tests only
python -m pytest tests/unit/

# Specific test file
python -m pytest tests/unit/test_switch.py

# With verbose output
python -m pytest tests/ -v -s
```

### Coverage

```bash
# Generate HTML report
python -m pytest tests/ --cov=custom_components/imou_life --cov-report=html

# View in browser
# Open tools/htmlcov/index.html
```

### Docker Testing

```bash
# Run in Docker
.\tools\scripts\run_docker_tests.ps1

# Manual Docker
docker-compose -f tools/docker/docker-compose.test.yml up --build
```

## 🔧 Common Tasks

### Adding New Tests

```bash
# Create new test file
touch tests/unit/test_new_feature.py

# Run new tests
python -m pytest tests/unit/test_new_feature.py -v
```

### Code Quality

```bash
# Pre-commit hooks (if configured)
git commit -m "Your message"

# Manual linting
python -m flake8 custom_components/imou_life/
python -m black custom_components/imou_life/
```

### Documentation

```bash
# Update docs
# Edit files in docs/

# View project structure
tree /f
```

## 📁 Key Directories

- **`custom_components/imou_life/`** - Main integration code
- **`tests/`** - Test suite
- **`tools/scripts/`** - Development scripts
- **`docs/`** - Documentation
- **`config/`** - Configuration files

## 🚨 Troubleshooting

### Import Errors

```bash
# Ensure you're in project root
pwd  # Should show /path/to/imou_life

# Reinstall dependencies
pip install -r config/requirements_dev.txt
```

### Test Failures

```bash
# Check test output
python -m pytest tests/ -v -s

# Run single failing test
python -m pytest tests/unit/test_file.py::test_function -v -s
```

### Environment Issues

```bash
# Recreate virtual environment
deactivate
Remove-Item -Recurse -Force venv
python -m venv venv
.\tools\scripts\activate_venv.ps1
pip install -r config/requirements_dev.txt
```

## 📚 Next Steps

1. **Read the [Testing Guide](TESTING.md)** for detailed testing information
2. **Check [Development Guide](DEVELOPMENT.md)** for contribution guidelines
3. **Explore [Performance Guide](PERFORMANCE_TROUBLESHOOTING.md)** for optimization tips
4. **Review [HACS Guide](HACS_ENHANCEMENTS.md)** for HACS-specific features

## 🆘 Need Help?

- **Quick Questions**: Check [FAQ](FAQ.md)
- **Bugs**: [Open an issue](https://github.com/maximunited/imou_life/issues)
- **Discussions**: [GitHub Discussions](https://github.com/maximunited/imou_life/discussions)

---

**Ready to contribute?** Check out our [Development Guide](DEVELOPMENT.md) for detailed guidelines! 🚀
