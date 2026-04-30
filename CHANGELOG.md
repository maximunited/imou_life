# Changelog

## [1.3.5] - 2026-05-01

### Added

- **Bronze Tier 100% Complete** 🎉
  - Official Imou branding assets (icon.png 256×256, icon@2x.png 512×512)
  - Downloaded from Home Assistant brands repository
  - All 19 Bronze tier requirements satisfied
  - Quality scale updated to "bronze" in manifest.json

- **API Server Region Selector** (#22)
  - User-friendly dropdown to select optimal API server based on geographic region
  - Predefined servers: Global, Frankfurt (EU), Singapore (Asia), Oregon (US), China
  - Custom URL option for advanced users
  - Performance improvement: Frankfurt server 3× faster for EU users (69ms vs 212ms)
  - 4 new tests for server selection functionality

- **Branding Assets Documentation** (#21)
  - Complete guide: `custom_components/imou_life/BRANDING.md`
  - Official Imou logo resources and implementation steps
  - Technical specifications (PNG format, dimensions, compression)
  - Verification checklist

### Changed

- **has_entity_name Implementation** (#19)
  - All entities now use `_attr_has_entity_name = True`
  - Proper name composition with device name
  - Satisfies Bronze tier requirement

- **entity-event-setup Compliance** (#20)
  - Verified motion detection as state-based (binary_sensor)
  - Last alarm as historical timestamp sensor
  - No Event platform needed (polling-based integration)

### Tests

- **Bronze Tier Compliance Test Suite**
  - `test_branding_assets_exist`: Validates icon format, dimensions, file size
  - PIL validation for PNG format and exact pixel dimensions
  - Data-driven Bronze tier summary (auto-detects icon presence)
  - All 13 Bronze tier tests passing ✅

### Documentation

- Bronze tier status: 19/19 complete (100%) ✅
- Quality scale tracking updated in `quality_scale.yaml`

---

## [Unreleased] - Bronze Tier Runtime Data Migration

### Changed
- **Runtime Data Migration** ⚡ CRITICAL
  - Migrated from legacy `hass.data[DOMAIN]` to modern `entry.runtime_data` pattern
  - Affects all platform files (camera, sensor, binary_sensor, switch, select, button, siren)
  - Battery-specific platforms also migrated (battery_binary_sensor, battery_button, battery_select)
  - Diagnostics updated to use `entry.runtime_data`
  - Shared platform_setup.py updated
  - All 241 unit tests passing ✅
  - Completes 1 of 4 remaining Bronze tier requirements

### Technical
- `__init__.py`: Removed `hass.data[DOMAIN]` usage, now sets `entry.runtime_data = coordinator`
- `async_unload_entry`: Uses `entry.runtime_data` instead of `hass.data[DOMAIN][entry.entry_id]`
- All platform files updated: 8 files modified
- Test fixtures updated: MockConfigEntry now has `runtime_data` attribute
- Test mocks updated: MockHomeAssistant sets `entry.runtime_data` in async_setup

### Quality Scale
- **Bronze**: 16/19 complete (84%) - Up from 15/19 (79%)
- **runtime-data**: ✅ DONE (was TODO)

### Tests
- All unit tests passing: 241 passed, 2 skipped ✅
- Updated test_diagnostics.py to use `entry.runtime_data`
- Updated test_init.py to check `entry.runtime_data`
- Mock fixtures support runtime_data pattern

## [Unreleased] - Bronze Tier Completion

### Added
- **Bronze Tier Compliance Test Suite**: Comprehensive automated testing for quality scale requirements
  - 11 tests validating Bronze tier compliance (10 passing, 1 skipped)
  - Tests cover: config flow, credential validation, unique IDs, service registration, polling intervals, common modules, unloading
  - Summary test documenting compliance status for all 19 Bronze tier rules
  - Test file: `tests/unit/test_bronze_tier_compliance.py`

### Documentation
- **Bronze Tier Completion Guide** (`docs/development/BRONZE_TIER_COMPLETION.md`)
  - Complete summary of 15/19 Bronze tier requirements completed
  - Detailed validation strategy and test coverage
  - Clear documentation of 4 remaining TODO items
  - Next steps for full Bronze tier compliance

- **Quality Scale Roadmap** (`docs/development/QUALITY_SCALE_ROADMAP.md`)
  - Complete path from Bronze to Platinum tier
  - Bronze (15/19), Silver (5/10), Gold (7/23), Platinum (0/3, 2 exempt)
  - Detailed requirements breakdown for each tier
  - Effort estimates and timeline projections (103-147 hours total)
  - Prioritization matrix and migration strategy
  - Version numbering plan (v2.0.0 Bronze, v2.1.0 Silver, v2.5.0 Gold, v3.0.0 Platinum)

- **Service Documentation** (`docs/SERVICES.md`)
  - Complete PTZ service documentation (ptz_location, ptz_move)
  - Battery optimization service documentation (9 services)
  - Parameter specifications with ranges and descriptions
  - 3 automation examples (patrol, battery management, night mode)
  - Satisfies Bronze tier `docs-actions` requirement

- **Uninstall Guide** (`docs/UNINSTALL.md`)
  - UI removal method (recommended)
  - Manual removal method with step-by-step instructions
  - Cleanup procedures and troubleshooting
  - Re-installation instructions
  - Data retention information
  - Satisfies Bronze tier `docs-removal-instructions` requirement

- **Python Dependencies Documentation** (README.md)
  - Added "Python Dependencies" section
  - Documents `imouapi==1.0.15` with PyPI link
  - Explains automatic installation by Home Assistant
  - Satisfies Bronze tier `dependency-transparency` requirement

- **Custom Entity Icons** (`custom_components/imou_life/icons.json`)
  - Custom icons for all entity types
  - State-specific icons for API status sensor (ok, rate_limited, error)

### Changed
- **Repository Organization**: Cleaner structure based on official Imou repository analysis
  - Root directory cleaned (10+ docs moved to subdirectories)
  - Created `docs/development/` for technical documentation
  - Created `docs/testing/` for test documentation
  - Created `assets/images/` for future screenshots

- **Quality Scale Claim**: Corrected from "platinum" to "bronze" in manifest.json
  - Based on official Home Assistant quality scale audit (55 total rules)
  - Accurate representation of current compliance level

### Fixed
- **Quality Scale Tracking** (`custom_components/imou_life/quality_scale.yaml`)
  - Now tracks all 55 official Home Assistant quality scale rules
  - Bronze: 15/19 done, 4 todo
  - Silver: 5/10 done, 5 todo
  - Gold: 7/23 done, 16 todo
  - Platinum: 0/3 done (2 exempt due to library limitations)
  - Includes detailed exemption notes for async-dependency and inject-websession

### Tests
- **All Unit Tests Passing**: 241 passed, 2 skipped ✅
- **Bronze Tier Tests**: 10 passed, 1 skipped ✅
- **Config Flow Tests**: 10/10 passing ✅

### Technical
- Repository reorganization follows Home Assistant best practices
- Test suite validates compliance programmatically
- Documentation provides clear path to higher quality tiers

### TODO (Bronze Tier Completion)
**4 requirements remaining for full Bronze tier compliance:**

1. **has-entity-name** ⚡ CRITICAL
   - Implement `_attr_has_entity_name = True` in base entity
   - Breaking change: entity IDs will change
   - Requires v2.0.0 release with migration guide

2. **runtime-data** ⚡ CRITICAL
   - Migrate from `hass.data[DOMAIN]` to `entry.runtime_data`
   - Affects all platform files
   - Modern Home Assistant pattern (2024.2+)

3. **entity-event-setup** ⚠️ MEDIUM
   - Verify entity event handling
   - Add tests if needed

4. **brands** ⚠️ LOW
   - Create logo and icon assets
   - Add branding files

## [1.3.4] (2026-04-30)
### Added
- **Enhanced Options UI**: Humanized labels and descriptions for better user experience
  - Field labels now capitalized and user-friendly (Motion Sensitivity, Recording Quality, LED Indicators, Auto Sleep, Battery Threshold)
  - Option values humanized: low → "Low", medium → "Medium", high → "High", ultra_high → "Ultra High"
  - Recording quality now shows resolution info: "Low (SD - 480p)", "Standard (HD - 720p)", "High (Full HD - 1080p)", "Ultra High (2K/4K)"
  - Added helpful descriptions below each option explaining purpose and impact
  - All 8 translation files updated with new labels and descriptions

### Changed
- Options flow now uses dictionary-based selectors for better display names
- Motion sensitivity and recording quality options defined in const.py with display names

### Technical
- Added MOTION_SENSITIVITY_OPTIONS dict mapping values to display names
- Added RECORDING_QUALITY_DISPLAY dict with resolution information
- Updated config_flow.py to use vol.In(dict) for selector options
- Fixed Hassfest validation by moving selector labels from translations to code

## [1.3.3] (2026-04-30)
### Fixed
- **Critical: Rate Limit Infinite Loop**: Users can now complete setup even when rate limited
  - Discovery rate limit error now shows clear message instead of auto-redirecting
  - Manual device entry skips validation when rate limited, creates entry anyway
  - Device initializes automatically when rate limit clears
  - Prevents infinite loop where users couldn't complete setup
  - Error message: "Please uncheck 'Enable Device Discovery' and enter device ID manually"

- **URL Field Auto-Population**: URL field now updates correctly based on server selection
  - URL field always visible with auto-populated value for preset servers
  - For custom server: Required field (shows asterisk) with empty default
  - For preset servers: Optional field with auto-populated API endpoint URL
  - Description updated: "Auto-populated based on server selection"

### Changed
- Manual device entry now allows completion even when API rate limited
- Discovery error handling improved with clearer user guidance
- URL field requirement level changes dynamically based on server type

### Technical
- Config flow schema conditionally sets URL field as Required vs Optional
- Manual entry skips device validation when OP1013 error detected
- Added "rate_limit_discovery" error message for discovery failures
- Added 2 new tests for URL field behavior

## [1.3.2] (2026-04-30)
### Fixed
- **Config Flow UI Bug**: URL field no longer shows for preset servers
  - URL field now only appears when "Custom" server is selected
  - Eliminates confusing behavior where URL didn't update when switching servers
  - Cleaner, more intuitive user interface

### Changed
- **Improved Field Labels and Descriptions**:
  - "enable_discover" renamed to "Enable Device Discovery" with helpful description
  - "API Base URL" renamed to "Custom API URL" (only shown for custom servers)
  - Added description: "Automatically discover all devices registered to your Imou account. Disable to manually enter a specific device ID instead."
  - Updated all 8 translation files

### Technical
- Config flow schema now built conditionally based on selected server
- URL field only added to schema when custom server is selected
- Removed unused DEFAULT_API_URL import

## [1.3.1] (2026-04-30)
### Changed
- **Improved API Server Selector UI**: Enhanced config flow login step
  - Renamed "Oregon" to "Virginia (USA)" after geo-location verification
  - API Base URL field now auto-populates based on server selection
  - Clearer field labels: "API Server" and "API Base URL"
  - Dropdown shows proper capitalized names with countries/domains
  - Better descriptions explaining when custom URL is needed
  - Updated all 8 translation files

### Fixed
- **Rate Limit Handling During Discovery**: Config flow now handles rate limits gracefully
  - Detects OP1013 rate limit errors during device discovery
  - Shows helpful error message explaining the situation
  - Automatically redirects to manual device entry instead of infinite loop
  - Prevents repeated API calls when rate limited
  - Users can now complete setup even when rate limited

### Technical
- Verified API server locations via IP geolocation:
  - 8.219.71.80 → Singapore
  - 47.245.141.21 → Frankfurt am Main, Germany
  - 47.90.226.98 → Virginia Beach, Virginia, USA (not Oregon!)
  - openapi-or.easy4ip.com resolves to us-east-1.alb.aliyuncsslbintl.com

## [1.3.0] (2026-04-30)
### Added
- **API Rate Limit Visibility**: New diagnostic sensor showing real-time API health status
  - States: `ok`, `rate_limited`, `error`, `unknown`
  - Tracks rate limit occurrences, duration, and estimated reset time
  - Persistent notification when rate limiting detected during setup
  - Sensor attributes: rate_limit_count, scan_interval, last_error_message, and more
- **Automatic Scan Interval Adjustment**: Intelligently handles rate limiting
  - Automatically doubles scan interval when rate limited (e.g., 15min → 30min)
  - Automatically restores original interval when limit clears
  - Reduces unnecessary API calls during rate limit periods
  - Logs all interval changes for transparency
- **Rate Limit Duration Tracking**: Know exactly when rate limiting will end
  - Tracks when rate limiting started
  - Estimates reset time (Imou API resets hourly)
  - Shows countdown in seconds via `rate_limit_reset_in_seconds` attribute
  - All timestamps in ISO format
- **API Server Region Selector**: User-friendly dropdown to select optimal API server
  - Predefined options: Global, Europe (Frankfurt), Asia Pacific (Singapore), North America (Oregon), China
  - Custom URL option for advanced users
  - Based on ping tests showing Frankfurt server is 3x faster for EU users
  - Validation for custom URLs (shows error if empty when "Custom" selected)

### Changed
- Enhanced coordinator to track rate limit state and adjust behavior automatically
- API Status sensor appears automatically in device panel (diagnostic category)
- Config flow login step now uses dropdown selector instead of text input for API URL
- Improved user experience during rate limiting with automatic recovery

### Fixed
- Rate limit errors no longer crash the integration - handled gracefully with automatic retry
- Empty custom URL validation prevents invalid configurations

### Tests
- Added 18 comprehensive tests for rate limit handling and API status sensor
- Added 4 tests for API server selection in config flow
- Total: 229 tests passing (211 existing + 18 new)

### Documentation
- Added `HOOK_ANALYSIS.md` documenting pre-commit hook decisions
- Updated all 8 translation files with new config flow labels and sensor attributes

## [1.2.2] (2026-04-29)
### Added
- Handle API rate limit errors gracefully


## [1.2.1] (2026-04-29)
### Added
- Fix HACS installation directory structure


## [1.2.0] (2026-04-29)
### Added
- Comprehensive CLAUDE.md with project architecture and development commands
- Karpathy Guidelines as git submodule for code quality standards
- ImouBatteryEntity base class to eliminate code duplication across battery platforms
- Asyncio.Lock for thread-safe state mutations in battery coordinator
- Public API methods for battery optimization (enter_sleep_mode, exit_sleep_mode, etc.)
- Complete battery API integration with proper fallback handling

### Changed
- Refactored battery coordinator to use cached battery data and avoid redundant API calls
- Made battery optimization methods public instead of private
- Updated all battery platform entities to inherit from ImouBatteryEntity base class
- Improved type hints throughout battery code (Dict[str, str] → Dict[str, Any])
- Enhanced current_option fallback logic in battery select entities

### Fixed
- **SECURITY**: Removed hardcoded credentials from camera.py fallback code
- Fixed exception handling in __init__.py to preserve original exception context
- Added error messages to UpdateFailed exceptions in coordinator.py for better debugging
- Added input validation for timeout parsing with try/except to prevent crashes
- Used ValueError instead of generic Exception in switch.py for better error handling
- Removed unittest.mock imports from production code (was incorrectly used)
- Fixed hardcoded mock battery data - now uses real coordinator data

### Tests
- Updated all 206 battery tests to work with new base class architecture
- Added AsyncMock for async_get_battery_status in test fixtures
- Fixed method names in tests to use public API methods
- All tests passing (206 passed, 1 skipped)


## [1.1.2] (2025-08-26)
### Changed
- Version bump to 1.1.2


## [1.1.1] (2025-08-24)
### Changed
- Version bump to 1.1.1


## [1.1.0] (2025-01-27)
### Changed
- Graduated to stable release v1.1.0
- Updated development status from Beta to Production/Stable
- Version bump to 1.1.0

## [1.0.33] (2025-08-23)
### Changed
- Version bump to 1.0.33


## [1.0.32] (2025-08-22)
### Changed
- Version bump to 1.0.32


## [1.0.31] (2025-08-22)
### Changed
- Version bump to 1.0.31


## [1.0.30] (2025-08-22)
### Changed
- Version bump to 1.0.30


## [1.0.29] (2025-08-22)
### Changed
- Version bump to 1.0.29


## [1.0.28] (2025-08-22)
### Changed
- Version bump to 1.0.28


## [1.0.27] (2025-08-22)
### Changed
- Version bump to 1.0.27


## [1.0.26] (2025-08-22)
### Changed
- Version bump to 1.0.26


## [1.0.25] (2025-01-27)
### Added
- Automated version bumping with git-bump script
- One-command version management system
- Auto-increment version functionality

## [1.0.24] (2025-01-27)
### Added
- Enhanced version management scripts
- Improved release automation workflow

## [1.0.23] (2025-01-27)
### Added
- Version management automation scripts
- Git hooks for automatic tagging

## [1.0.22] (2025-01-27)
### Fixed
- Fixed "Invalid handler specified" error when adding integration to Home Assistant
- Removed deprecated CONNECTION_CLASS from config flow
- Added proper domain specification to config flow handler
- Fixed typo in config flow docstring
- Added missing requirements.txt file

## [1.0.21] (2025-01-XX)
### Added
- Unified release workflow system with multiple release modes
- Smart CI draft creation with duplicate prevention
- Flexible manual release options (pre-release/release/draft)

## [1.0.20] (2025-01-XX)
### Added
- HACS-compatible pre-release workflow (automatically publishes pre-releases)
- Enhanced release automation for immediate HACS availability

## [1.0.19] (2025-01-XX)
### Added
- Pre-release workflow configuration for better release management
- Enhanced release automation with proper pre-release tagging

## [1.0.18] (2025-01-XX)
### Added
- Automated CI release workflow for draft releases when tests pass
- Enhanced GitHub Actions workflows for better release management
- Comprehensive workflow documentation in README
- Fixed ZIP file path issues in release workflows

## [1.0.17] (2025-01-XX)
### Added
- Automated CI release workflow for draft releases when tests pass
- Enhanced GitHub Actions workflows for better release management
- Comprehensive workflow documentation in README

## [1.0.16] (2025-06-06)
### Added
- Disclaimer on the status of the integration
### Fixed
- async_forward_entry_setup() deprecation (#124)
- Sets option flow config_entry explicitly deprecation
- Config alias deprecation
- async_add_job() deprecation

## [1.0.15] (2024-01-27)
### Fixed
- HACS failing installation: error 500 (#83 #84)

## [1.0.14] (2023-12-26)
### Added
- French and Indonesian support
- List with all the supported/tested models in the README file
- Instructions on how to contribute in the README file
### Fixed
- Improved support for Cell Go cameras (#55)
- Discovery service now ignores with a warning unrecognized/unsupported devices instead of throwing an error (#47)
### Changed
- Bump imouapi version: 1.0.13 → 1.0.14
- Added a Wiki to Github with articles for end users, developers and maintainers

## [1.0.13] (2023-02-19)
### Added
- Added battery sensor for dormant devices
- Catalan translation
### Changed
- Added new conditions to the Imou Push Notifications automation template in the README file to prevent too many refresh
### Fixed
- Motion detection sensor now showing up for all devices

## [1.0.12] (2022-12-11)
### Fixed
- Dormant device logic

## [1.0.11] (2022-12-11)
### Added
- Support for dormant devices
- `status` sensor
- Options for customizing wait time for camera snapshot download and wait time after waking up dormant device
### Changed
- Device is now marked online if either online or dormant

## [1.0.10] (2022-12-04)
### Added
- Camera entity now supports snapshots and video streaming

## [1.0.9] (2022-11-26)
### Added
- PTZ Support, exposed as `imou_life.ptz_location` and `imou_life.ptz_move` services
- Camera entity, used for invoking the PTZ services

## [1.0.8] (2022-11-21)
### Fixed
- "Failed to setup" error after upgrading to v1.0.7 (#37)

## [1.0.7] (2022-11-20)
### Added
- Spanish and italian translations (#21)
- Reverse proxy sample configuration for custom configuration of push notifications (#29)
- Siren entity (#26)
### Changed
- API URL is now part of the configuration flow (#16)
- Bump imouapi version: 1.0.6 → 1.0.7
### Removed
- `siren` switch, now exposed as a siren entity
- API Base URL option, now part of the configuration flow
### Fixed
- Entities not correctly removed from HA

## [1.0.6] (2022-11-19)
### Added
- `motionAlarm` binary sensor which can be updated also via the `refreshAlarm` button
### Removed
- `lastAlarm` sensor. The same information has been moved into the `alarm_time` attribute inside the `motionAlarm` binary sensor, together with `alarm_type` and  `alarm_code`
### Changed
- Bump imouapi version: 1.0.5 → 1.0.6
- Updated README and link to the roadmap

## [1.0.5] (2022-11-13)
### Added
- Switch for turning the Siren on/off for those devices supporting it
- Buttons for restarting the device and manually refreshing device data in Home Assistant
- Sensor with the callback url set for push notifications
### Changed
- Bump imouapi version: 1.0.5 → 1.0.5
- Reviewed instructions for setting up push notifications
- Updated README with Roadmap
- Deprecated "Callback Webhook ID" option for push notifications, use "Callback URL" instead
- Reviewed switches' labels
### Fixed
- Storage left sensor without SD card now reporting Unknown

## [1.0.4] (2022-11-12)
### Added
- Brazilian Portuguese Translation
- HACS Default repository
### Changed
- Split Github action into test (on PR and push) and release (manual)

## [1.0.3] (2022-10-23)
### Added
- Support white light on motion switch through imouapi
- `linkagewhitelight` now among the switches enabled by default
- Support for SelectEntity and `nightVisionMode` select
- Support storage used through `storageUsed` sensor
- Support for push notifications through `pushNotifications` switch
- Options for configuring push notifications
### Changed
- Bump imouapi version: 1.0.2 → 1.0.4
- Redact device id and entry id from diagnostics

## [1.0.2] (2022-10-19)
### Changed
- Bump imouapi version: 1.0.1 → 1.0.2

## [1.0.1] (2022-10-16)
### Added
- Download diagnostics capability

## [1.0.0] (2022-10-15)
### Changed
- Bump imouapi version: 0.2.2 → 1.0.0
- Entity ID names are now based on the name of the sensor and not on the description

## [0.1.4] (2022-10-08)
### Added
- Test suite
### Changed
- Bump imouapi version: 0.2.1 → 0.2.2

## [0.1.3] (2022-10-04)
### Changed
- Bump imouapi version: 0.2.0 → 0.2.1

## [0.1.2] (2022-10-03)
### Added
- All the switches are now made available. Only a subset are then enabled in HA by default.
- Sensors' icons and default icon
### Changed
- Bump imouapi version: 0.1.5 → 0.2.0 and adapted the code accordingly
- Introduced `ImouEntity` class for all the sensors derived subclasses

## [0.1.1] (2022-09-29)
### Changed
- Bump imouapi version: 0.1.4 → 0.1.5
- Improved README

## [0.1.0] (2022-09-29)
### Added
- First release for beta testing
