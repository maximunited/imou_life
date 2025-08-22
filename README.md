
# Imou Life - Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Quality Scale](https://img.shields.io/badge/Quality%20Scale-Platinum-brightgreen.svg)](https://github.com/custom-components/hacs#quality-scale)
[![Maintainer](https://img.shields.io/badge/maintainer-@maximunited-blue.svg)](https://github.com/maximunited)

A Home Assistant integration for Imou Life cameras and devices, providing comprehensive monitoring and control capabilities.

## 🚀 Features

- **Camera Integration**: Live video streaming and snapshot capture
- **Motion Detection**: Real-time motion alerts and notifications
- **Device Control**: PTZ control, recording management, and more
- **Automation Ready**: Full Home Assistant automation support
- **HACS Compatible**: Easy installation through HACS

## 📁 Project Structure

```
imou_life/
├── 📁 custom_components/imou_life/    # Home Assistant integration
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

## 🛠️ Development

### Prerequisites

- Python 3.9+
- Home Assistant 2023.8.0+
- Git

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/maximunited/imou_life.git
   cd imou_life
   ```

2. **Set up development environment**:
   ```bash
   # Windows
   .\tools\scripts\activate_venv.bat
   
   # PowerShell
   .\tools\scripts\activate_venv.ps1
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r config/requirements_dev.txt
   pip install -r config/requirements_test.txt
   ```

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

The script automatically:
- Updates `manifest.json`
- Generates changelog entries
- Commits changes
- Creates and pushes git tags
- Triggers GitHub Actions workflows

### Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=custom_components/imou_life

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
```

### Docker Testing

```bash
# Run tests in Docker
.\tools\scripts\run_docker_tests.ps1

# Or manually
docker-compose -f tools/docker/docker-compose.test.yml up --build
```

## 📚 Documentation

- **[Installation Guide](docs/README.md)** - Complete setup instructions
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing guidelines
- **[Performance Guide](docs/PERFORMANCE_TROUBLESHOOTING.md)** - Optimization tips
- **[HACS Guide](docs/HACS_ENHANCEMENTS.md)** - HACS-specific features
- **[Changelog](docs/CHANGELOG.md)** - Version history and changes

## 🔧 Configuration

### Requirements

- **Home Assistant**: 2023.8.0 or later
- **Python Dependencies**: See `config/requirements.txt`
- **Development Dependencies**: See `config/requirements_dev.txt`
- **Test Dependencies**: See `config/requirements_test.txt`

### Configuration Files

- **`.coveragerc`**: Coverage reporting configuration
- **`setup.cfg`**: Python package configuration
- **`pyproject.toml`**: Project metadata and build settings
- **`.pre-commit-config.yaml`**: Pre-commit hooks configuration

## 🚀 Deployment

### HACS Installation

1. Add this repository to HACS
2. Install the integration
3. Restart Home Assistant
4. Add via Settings > Devices & Services

### Manual Installation

1. Download the latest release
2. Extract to `custom_components/imou_life/`
3. Restart Home Assistant
4. Add via Settings > Devices & Services

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Quality

- **Linting**: Pre-commit hooks ensure code quality
- **Testing**: Comprehensive test suite with coverage reporting
- **Documentation**: Clear docstrings and comprehensive guides
- **Performance**: Optimized for Home Assistant environments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original integration by [@user2684](https://github.com/user2684)
- Enhanced and maintained by [@maximunited](https://github.com/maximunited)
- Community contributors and testers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/maximunited/imou_life/issues)
- **Discussions**: [GitHub Discussions](https://github.com/maximunited/imou_life/discussions)
- **Documentation**: [Project Wiki](https://github.com/maximunited/imou_life/wiki)

---

**Made with ❤️ for the Home Assistant community**
