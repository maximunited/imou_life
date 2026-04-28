# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Coding Guidelines

This project uses the **Karpathy Guidelines** to reduce common LLM coding mistakes. The `/karpathy-guidelines` skill is available with these four core principles:

1. **Think Before Coding** - Don't assume. Don't hide confusion. Surface tradeoffs.
2. **Simplicity First** - Minimum code that solves the problem. Nothing speculative.
3. **Surgical Changes** - Touch only what you must. Clean up only your own mess.
4. **Goal-Driven Execution** - Define success criteria. Loop until verified.

See `.claude/skills/karpathy/SKILL.md` for detailed guidelines.

## Project Overview

This is a Home Assistant custom integration for Imou Life cameras and devices. The integration provides comprehensive monitoring and control capabilities through the Imou API, including live video streaming, motion detection, PTZ controls, and device management.

**Key Details:**
- **Domain**: `imou_life`
- **Quality Scale**: Platinum tier
- **Config Flow**: UI-based configuration (VERSION 3)
- **API Library**: `imouapi==1.0.15`
- **Requirements**: Home Assistant 2024.2.0+, Python 3.11-3.13

## Architecture

### Core Components

**Entry Point (`__init__.py`)**
- Sets up the integration using config entries
- Creates `ImouAPIClient` and `ImouDevice` instances
- Initializes `ImouDataUpdateCoordinator` for polling device data
- Registers all platforms (camera, switch, sensor, binary_sensor, select, button, siren)
- Handles device initialization with timeout protection

**Configuration Flow (`config_flow.py`)**
Three-step wizard process:
1. **Login Step**: Validates App ID and App Secret credentials
2. **Discovery Step**: Auto-discovers devices OR allows manual device ID entry
3. **Options Step**: Configures polling interval, API settings, battery optimization, and advanced features

**Data Coordinator (`coordinator.py`)**
- `ImouDataUpdateCoordinator` extends Home Assistant's `DataUpdateCoordinator`
- Polls device data at configurable intervals (default: 15 minutes)
- Handles API exceptions and converts them to `UpdateFailed` events
- Shared by all platform entities for the same device

**Battery-Powered Devices**
- Separate `battery_coordinator.py` for optimized polling of battery devices
- Battery-specific platforms: `battery_binary_sensor.py`, `battery_button.py`, `battery_select.py`
- Advanced battery optimization features: auto-sleep, power saving modes, LED indicators

### Platform Files

Each platform file creates and manages specific entity types:
- `camera.py` - Live streaming, snapshots, PTZ controls
- `switch.py` - Push notifications, device features
- `sensor.py` - Storage usage, callback URL, device status
- `binary_sensor.py` - Online status, motion detection
- `select.py` - Night vision mode, recording quality
- `button.py` - Restart device, refresh data, refresh motion alarm
- `siren.py` - Alarm controls

**Entity Hierarchy:**
- `entity.py` - Base entity class with common properties
- `entity_mixins.py` - Reusable entity behaviors
- `platform_setup.py` - Platform registration utilities

### Key Files

- `const.py` - All constants, configuration keys, default values
- `diagnostics.py` - Device diagnostics for troubleshooting
- `manifest.json` - Integration metadata (version, dependencies, quality scale)
- `translations/*.json` - Multi-language support (ca, en, es-ES, fr, he, id, it-IT, pt-BR)

## Development Commands

### Environment Setup

**Windows:**
```bash
.\tools\scripts\activate_venv.bat        # Command Prompt
.\tools\scripts\activate_venv.ps1        # PowerShell
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r config/requirements_dev.txt
pip install -r config/requirements_test.txt
pre-commit install
```

### Testing

**Run all tests:**
```bash
python -m pytest tests/
```

**Quick test (Windows):**
```bash
run_tests.bat                            # Command Prompt
.\run_tests.ps1                          # PowerShell
python tools/validation/run_simple_tests.py
```

**With coverage:**
```bash
python -m pytest tests/ --cov=custom_components/imou_life --cov-report=html
```

**Test categories:**
```bash
python -m pytest tests/unit/             # Unit tests only
python -m pytest tests/integration/      # End-to-end integration tests
python -m pytest tests/unit/test_battery_*.py  # Battery coordinator tests
```

**Test organization:**
- `tests/unit/` - Isolated unit tests for individual components (206 tests, all passing ✅)
- `tests/integration/` - End-to-end tests covering full workflows (22 tests, 8 passing):
  - Full setup flow (config → entities)
  - Battery optimization integration
  - Entity state updates and interactions
  - Error handling and recovery scenarios
  - Multi-device setups
  - **Status**: 42% pass rate, documented in [tests/integration/KNOWN_ISSUES.md](tests/integration/KNOWN_ISSUES.md)
  - **Note**: Failures are test infrastructure issues, not code bugs
- `tests/fixtures/` - Shared test fixtures and mocks

**Integration test status:**
- ✅ Core functionality validated (8 critical tests passing)
- ⚠️ 11 tests need mock fixes (1-2 hours work, all fixable)
- See `tests/integration/KNOWN_ISSUES.md` for detailed analysis and fix strategies

**Coverage requirements:** Minimum 70% required

### Code Quality

**Run all pre-commit hooks:**
```bash
pre-commit run --all-files
```

**Individual checks:**
```bash
black --check --diff .                   # Code formatting (line length: 88)
flake8 .                                 # Linting
isort --check-only --diff .              # Import sorting
mypy custom_components/imou_life/        # Type checking
```

**Auto-fix formatting:**
```bash
black .
isort .
```

### Validation

**HACS validation:**
```bash
# Runs automatically in CI, or use the HACS GitHub Action
```

**Hassfest validation:**
```bash
# Runs automatically in CI, or use the Home Assistant hassfest action
```

**Manifest validation:**
```bash
python -c "import json; json.load(open('custom_components/imou_life/manifest.json')); print('Manifest validation passed')"
```

### Version Management & Releases

**Prerequisites:**
```bash
# IMPORTANT: Install pre-commit before running git bump
pip install pre-commit
pre-commit install
```

**Automatic version bumping:**
```bash
git bump                                 # Auto-increment patch version
git bump 1.2.0                           # Specific version
git bump 1.2.0 "Battery optimization"    # With custom message
```

The `git bump` script (PowerShell alias in `.git/config`):
- Updates `manifest.json` version
- Generates changelog entry in `docs/CHANGELOG.md`
- Commits changes with appropriate message
- Creates and pushes git tag (triggers release workflow)
- Requires pre-commit to be installed (will fail if missing)

**IMPORTANT**: The `git bump` script creates a basic changelog entry. For production releases:
1. Manually edit `docs/CHANGELOG.md` to add detailed sections (Added/Changed/Fixed/Security/Tests)
2. Follow [Keep a Changelog](https://keepachangelog.com/) format
3. Then run `git bump` to create the release

**Release Process:**
See `docs/RELEASE_PROCESS.md` for complete documentation including:
- Automated release workflow
- Manual release when automation fails
- Troubleshooting common issues
- Changelog format requirements

## CI/CD Workflows

**test.yml** - Quick PR checks:
- Pre-commit hooks (black, flake8, isort, codespell)
- Unit tests on Python 3.11, 3.12, 3.13
- HACS validation
- Hassfest validation

**validate.yml** - Comprehensive validation (main branches):
- Full test suite with coverage
- Coverage upload to Coveralls
- Code formatting and linting
- Manifest and translation validation

**releases.yml** - Automated release creation:
- Triggered by version tags (e.g., `v1.2.0`)
- Reads changelog using `mindsers/changelog-reader-action`
- Creates integration zip file (`imou_life.zip`)
- Creates GitHub pre-release with zip attachment
- Requires Keep a Changelog format in `docs/CHANGELOG.md`

## Coding Standards

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add motion detection sensitivity control
fix: resolve API timeout issues
docs: update installation guide
refactor: extract sleep schedule helpers
test: add coverage for battery optimization
```

### Code Style

- **Line length**: 88 characters (Black default)
- **Python version**: 3.11+ compatibility required
- **Type hints**: Use throughout (mypy compliance)
- **Async/await**: All I/O operations must be async
- **Logging**: Use `_LOGGER` from `logging.getLogger(__package__)`
- **Error handling**: Catch `ImouException` from imouapi library

### Configuration Flow Rules

- Config flow VERSION is currently 3
- Never modify config flow without incrementing VERSION if you change data structure
- All user-facing strings must have translation keys in `translations/*.json`
- Use `data_description` for helper text below form fields (Home Assistant 2024.2+)

### Entity Naming

- Follow Home Assistant entity naming conventions
- Use proper device classes for binary sensors and sensors
- Set appropriate entity categories (config, diagnostic)
- Provide translations for all entity names and states

### Battery Optimization

When working on battery-powered device features:
- Use the separate `battery_coordinator.py` for polling
- Respect sleep schedules (daily, weekly, custom)
- Consider power-saving modes and LED indicator settings
- Check battery threshold settings before triggering actions

## Important Notes

### API Limitations

- Imou limits developer accounts to 5 devices
- API base URL: `https://openapi.easy4ip.com/openapi`
- Default timeout: 10 seconds
- Push notifications require internet-accessible Home Assistant instance

### Home Assistant Integration Quality Scale

Currently at **Platinum tier**. When making changes:
- Maintain >70% test coverage
- Keep all type annotations
- Ensure fully async implementation
- Monitor performance (network/CPU usage)
- Update documentation for new features

### Testing Requirements

- All new features must include unit tests
- Integration tests for complex flows
- Mock the imouapi library in tests using fixtures in `tests/fixtures/`
- Use `pytest-homeassistant-custom-component` for Home Assistant test utilities

### Pre-commit.ci

This project uses pre-commit.ci for automatic code quality checks:
- Automatically fixes code style issues on PRs
- Keeps hooks updated monthly
- All PRs must pass pre-commit checks before merge

## Documentation Structure

- `README.md` - User-facing installation and usage guide
- `docs/DEVELOPMENT.md` - Detailed development guide
- `docs/INSTALLATION.md` - Complete installation instructions
- `docs/CONFIGURATION.md` - Configuration options
- `docs/TESTING.md` - Testing documentation
- `docs/PERFORMANCE_TROUBLESHOOTING.md` - Performance optimization
- `docs/QUALITY_SCALE.md` - Integration quality assessment
- `docs/CHANGELOG.md` - Version history
