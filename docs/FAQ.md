# Frequently Asked Questions (FAQ)

Common questions and answers about the Imou Life project.

## 🚀 General Questions

### What is Imou Life?

Imou Life is a Home Assistant integration that provides comprehensive monitoring and control capabilities for Imou cameras and devices.

### How do I install it?

See our [Installation Guide](INSTALLATION.md) for complete setup instructions.

### Is it HACS compatible?

Yes! Imou Life is fully HACS compatible and available in the default HACS repository.

## 🛠️ Development Questions

### How do I set up the development environment?

1. Clone the repository
2. Activate virtual environment: `.\tools\scripts\activate_venv.ps1`
3. Install dependencies: `pip install -r config/requirements_dev.txt`
4. Run tests: `python -m pytest tests/`

### How do I run tests?

```bash
# All tests
python -m pytest tests/

# Unit tests only
python -m pytest tests/unit/

# With coverage
python -m pytest tests/ --cov=custom_components/imou_life
```

### How do I update the version?

Use the automated version management:

```bash
# Auto-increment
.\tools\scripts\git-bump.ps1

# Specific version
.\tools\scripts\git-bump.ps1 1.0.30
```

## 📁 Project Structure

### Where are the main files located?

- **Integration Code**: `custom_components/imou_life/`
- **Tests**: `tests/`
- **Scripts**: `tools/scripts/`
- **Documentation**: `docs/`
- **Configuration**: `config/`

### What's the difference between unit and integration tests?

- **Unit Tests** (`tests/unit/`): Test individual functions in isolation
- **Integration Tests** (`tests/integration/`): Test component interactions

## 🔧 Configuration

### How do I configure testing?

Edit `config/.coveragerc` for coverage settings and `config/setup.cfg` for pytest configuration.

### Where are dependencies defined?

- **Runtime**: `config/requirements.txt`
- **Development**: `config/requirements_dev.txt`
- **Testing**: `config/requirements_test.txt`

## 🐳 Docker

### How do I run tests in Docker?

```bash
.\tools\scripts\run_docker_tests.ps1
```

### Can I customize the Docker setup?

Yes, edit `tools/docker/docker-compose.test.yml` and `tools/docker/Dockerfile.test`.

## 🚨 Troubleshooting

### Tests are failing with import errors

1. Ensure you're in the project root directory
2. Activate virtual environment: `.\tools\scripts\activate_venv.ps1`
3. Install dependencies: `pip install -r config/requirements_dev.txt`

### Coverage reports aren't generating

1. Run tests with coverage: `python -m pytest tests/ --cov=custom_components/imou_life --cov-report=html`
2. Check `tools/htmlcov/index.html` for the report

### Git bump script isn't working

1. Ensure you're in a git repository
2. Check that `tools/scripts/git-bump.ps1` exists
3. Verify PowerShell execution policy allows scripts

## 📚 Documentation

### Where can I find more information?

- **Main Documentation**: [docs/README.md](README.md)
- **Development Guide**: [docs/DEVELOPMENT.md](DEVELOPMENT.md)
- **Testing Guide**: [docs/TESTING.md](TESTING.md)
- **Performance Guide**: [docs/PERFORMANCE_TROUBLESHOOTING.md](PERFORMANCE_TROUBLESHOOTING.md)

### How do I contribute to documentation?

1. Edit files in the `docs/` directory
2. Follow the existing format and style
3. Submit a pull request

## 🤝 Contributing

### How can I contribute?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### What are the coding standards?

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Write tests for new functionality
- Maintain test coverage above 80%

### How do I report bugs?

Use [GitHub Issues](https://github.com/maximunited/imou_life/issues) and include:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details

## 📞 Support

### Where can I get help?

- **GitHub Issues**: [Report bugs and request features](https://github.com/maximunited/imou_life/issues)
- **GitHub Discussions**: [Ask questions and discuss](https://github.com/maximunited/imou_life/discussions)
- **Documentation**: Check the guides in the `docs/` directory

### How do I contact the maintainers?

- Open an [issue](https://github.com/maximunited/imou_life/issues) on GitHub
- Use [GitHub Discussions](https://github.com/maximunited/imou_life/discussions)
- Check the [Contributing Guide](DEVELOPMENT.md) for guidelines

---

**Still have questions?** Open an [issue](https://github.com/maximunited/imou_life/issues) or start a [discussion](https://github.com/maximunited/imou_life/discussions) on GitHub!
