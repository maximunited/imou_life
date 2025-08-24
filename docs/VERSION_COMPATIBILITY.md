# Version Compatibility Guide

This document provides comprehensive information about Python and Home Assistant version compatibility for the Imou Life integration.

## 🐍 Python Version Support

### Supported Python Versions

| Python Version | Release Date | Support Status | Notes |
|----------------|---------------|----------------|-------|
| **3.11** | October 2022 | ✅ **Fully Supported** | Stable, recommended for production |
| **3.12** | October 2023 | ✅ **Fully Supported** | Latest stable, recommended for new deployments |
| **3.13** | October 2024 | ✅ **Fully Supported** | Latest development, fully tested |

### Python Version Requirements

- **Minimum**: Python 3.11
- **Recommended**: Python 3.12 or 3.13
- **Maximum**: Python 3.13 (latest available)

## 🏠 Home Assistant Version Support

### Supported Home Assistant Versions

| Home Assistant Version | Release Date | Python Support | Integration Status |
|------------------------|--------------|----------------|-------------------|
| **2024.2.0** | February 2024 | 3.11, 3.12 | ✅ **Minimum Required** |
| **2024.12.0** | December 2024 | 3.11, 3.12, 3.13 | ✅ **Python 3.13 Support Added** |
| **2025.1.0** | January 2025 | 3.11, 3.12, 3.13 | ✅ **Latest Stable** |
| **2025.8.3+** | August 2025 | 3.11, 3.12, 3.13 | ✅ **Latest Development** |

### Home Assistant Requirements

- **Minimum**: 2024.2.0
- **Recommended**: Latest stable release
- **Python 3.13**: Requires 2024.12.0 or later

## 🔄 Compatibility Matrix

### Full Compatibility Matrix

| Python | HA 2024.2+ | HA 2024.12+ | HA 2025.1+ | HA 2025.8+ |
|--------|-------------|--------------|-------------|-------------|
| **3.11** | ✅ **Full** | ✅ **Full** | ✅ **Full** | ✅ **Full** |
| **3.12** | ✅ **Full** | ✅ **Full** | ✅ **Full** | ✅ **Full** |
| **3.13** | ❌ **No** | ✅ **Full** | ✅ **Full** | ✅ **Full** |

### Why This Version Range?

1. **Home Assistant 2024.2.0**: First version with comprehensive Python 3.11-3.12 support
2. **Home Assistant 2024.12.0**: First version with Python 3.13 support
3. **Future Versions**: All future Home Assistant versions will be compatible

## 🧪 Testing & Validation

### CI/CD Testing

Our GitHub Actions workflow tests all supported combinations:

- **Python 3.11** + Home Assistant 2024.2.0+
- **Python 3.12** + Home Assistant 2024.2.0+
- **Python 3.13** + Home Assistant 2024.12.0+

### Test Coverage

- **Unit Tests**: ✅ All Python versions
- **Integration Tests**: ✅ All Python versions
- **Home Assistant Integration**: ✅ All supported versions
- **Code Quality**: ✅ Linting, formatting, security checks

## 🚀 Installation Recommendations

### For Production Use

**Recommended Configuration:**
- **Python**: 3.12 (stable, well-tested)
- **Home Assistant**: Latest stable release
- **Platform**: Any supported platform

### For Development

**Development Environment:**
- **Python**: 3.13 (latest features)
- **Home Assistant**: Latest development release
- **Platform**: Linux/macOS recommended for full testing

### For Legacy Systems

**Minimum Viable Configuration:**
- **Python**: 3.11
- **Home Assistant**: 2024.2.0
- **Platform**: Any supported platform

## ⚠️ Important Notes

### Version Constraints

1. **Python 3.10 and below**: Not supported (Home Assistant compatibility)
2. **Home Assistant below 2024.2.0**: Not supported (API compatibility)
3. **Python 3.13 with HA < 2024.12.0**: Not supported (HA doesn't support Python 3.13)

### Migration Paths

- **From Python 3.10**: Upgrade to Python 3.11+ and HA 2024.2.0+
- **From HA < 2024.2.0**: Upgrade to HA 2024.2.0+ (Python 3.11+)
- **To Python 3.13**: Ensure HA 2024.12.0+ is installed

## 🔧 Troubleshooting

### Common Compatibility Issues

#### Python Version Issues
```bash
# Check Python version
python --version

# Should show 3.11, 3.12, or 3.13
```

#### Home Assistant Version Issues
```yaml
# In Home Assistant, check version
# Configuration → Info → Home Assistant Core
# Should show 2024.2.0 or later
```

#### Integration Installation Issues
```bash
# If using manual installation, ensure Python version compatibility
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
```

### Getting Help

If you encounter compatibility issues:

1. **Check your versions**: Python and Home Assistant
2. **Verify requirements**: Ensure minimum versions are met
3. **Check logs**: Look for version-related error messages
4. **Open an issue**: Include version information in your report

## 📚 Additional Resources

- **[Home Assistant Python Support](https://developers.home-assistant.io/docs/core/architecture/python-version-support/)**
- **[Python Version Support Matrix](https://www.python.org/downloads/)**
- **[Home Assistant Release Notes](https://www.home-assistant.io/blog/categories/release-notes/)**

---

**Last Updated**: August 2025
**Integration Version**: 1.1.1
**Maintainer**: [@maximunited](https://github.com/maximunited)
