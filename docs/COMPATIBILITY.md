# Home Assistant Compatibility

This integration is tested against multiple Home Assistant versions to ensure broad compatibility.

## Tested Versions

The integration is automatically tested against:

| Home Assistant Version | Python Version | Status | Notes |
|------------------------|----------------|--------|-------|
| 2025.5.0 | 3.12 | ✅ Supported | Minimum required version |
| 2025.9.0 | 3.12 | ✅ Supported | Mid-2025 stable |
| 2026.1.0 | 3.13 | ✅ Supported | Recent stable |
| 2026.4.0 | 3.13 | ✅ Supported | Latest stable |
| dev (nightly) | 3.14 | ⚠️ Testing | Development version |

## Minimum Requirements

- **Home Assistant**: 2025.5.0 or newer
- **Python**: 3.11 - 3.14
- **imouapi**: 1.0.15

## Version Support Policy

### Supported Versions
We actively support and test against:
- **Current release**: Latest stable Home Assistant version
- **Previous major releases**: Last 12 months of releases
- **Minimum version**: 2025.5.0 (released May 2025)

### End of Life
Support for older versions may be dropped when:
- Home Assistant itself drops support for that version
- Critical dependencies require newer HA versions
- Security vulnerabilities cannot be addressed in older versions

## Compatibility Testing

### Automated Tests
Every pull request and weekly scheduled runs test against:
- Minimum supported version (2025.5.0)
- Mid-2025 stable version (2025.9.0)
- Recent stable (2026.1.0)
- Current stable version (2026.4.0)
- Development version (to catch upcoming breaking changes)

### Manual Testing
Before each release, we manually test:
- Config flow setup
- Device discovery
- Entity creation and updates
- Options flow configuration
- Platform-specific features

## Known Compatibility Issues

### Home Assistant 2025.4.x and earlier
❌ **Not supported** - Requires HA 2025.5.0 or newer

**Reason**: Integration targets current Home Assistant APIs and features

**Workaround**: Upgrade Home Assistant to 2025.5.0 or newer

---

### Python 3.11 and earlier
❌ **Not supported** - Requires Python 3.12 or newer

**Reason**:
- Uses Python 3.12+ features
- Home Assistant 2025.5+ requires Python 3.12+

**Workaround**: Upgrade to Home Assistant running on Python 3.12+

---

## Breaking Changes

### Version 1.6.0
- **Minimum HA version**: Increased to 2024.3.3
- **Minimum Python version**: 3.11

### Version 1.5.0
- Dynamic device discovery requires HA 2024.2.0+

### Version 1.4.0
- Battery optimization features require HA 2024.2.0+

## Reporting Compatibility Issues

If you experience issues with a specific Home Assistant version:

1. **Check compatibility table above**
2. **Verify minimum requirements are met**
3. **Report the issue** with:
   - Home Assistant version (`Configuration → System → About`)
   - Python version
   - Integration version
   - Error logs from `Configuration → Logs`

[Report Issue](https://github.com/maximunited/imou_life/issues/new?template=bug_report.md)

## Future Compatibility

### Home Assistant 2025.x
We monitor Home Assistant development and will update the integration as needed for:
- New entity features
- API changes
- Deprecation warnings
- Platform improvements

### Python 3.15+
We will add support for new Python versions as they are adopted by Home Assistant core.
