# Changelog

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
