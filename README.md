
# Imou Life - Home Assistant Integration

[![Home Assistant](https://img.shields.io/badge/home%20assistant-%2341BDF5.svg?logo=home-assistant&logoColor=white)](https://www.home-assistant.io/)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Imou Life](https://img.shields.io/badge/imou%20life-%23FF8C00.svg?logo=imou&logoColor=white)](https://open.imoulife.com/)
[![Latest Release](https://img.shields.io/badge/release-1.2.0-blue.svg)](https://github.com/maximunited/imou_life/releases/tag/v1.2.0)
[![Pre-release](https://img.shields.io/badge/pre--release-1.2.0-orange.svg)](https://github.com/maximunited/imou_life/releases/tag/v1.2.0)
[![Quality Scale](https://img.shields.io/badge/quality%20scale-platinum-brightgreen.svg)](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
[![Buy Me a Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-%23FFDD00.svg?logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/maxim_united)

A Home Assistant integration for Imou Life cameras and devices, providing comprehensive monitoring and control capabilities.

## 🚀 Features

- **Camera Integration**: Live video streaming and snapshot capture
- **Motion Detection**: Real-time motion alerts and notifications
- **Device Control**: PTZ control, recording management, and more
- **Automation Ready**: Full Home Assistant automation support
- **HACS Compatible**: Easy installation through HACS

## 📋 Requirements

### System Requirements
- **Home Assistant**: 2024.2.0 or later
- **Python**: 3.11, 3.12, 3.13, 3.14 (experimental)
- **Operating System**: Any platform supported by Home Assistant

### Python Dependencies
- **imouapi**: 1.0.15 (automatically installed with the integration)
  - Official Python library for Imou API communication
  - Handles device discovery, authentication, and control
  - See [imouapi on PyPI](https://pypi.org/project/imouapi/)

> **Note**: The imouapi library is automatically installed by Home Assistant when you add the integration. No manual installation required.

### Account Requirements
- **Imou Account**: Valid Imou Life account with registered devices
- **Developer Account**: App ID and App Secret from [Imou Open Platform](https://open.imoulife.com)

## 🔑 Getting Your Imou API Credentials

Before installing the integration, you need to obtain your Imou API credentials:

1. **Register on Imou Life** if you haven't already
2. **Create a Developer Account** at [https://open.imoulife.com](https://open.imoulife.com)
3. **Access the Imou Console** at [https://open.imoulife.com/consoleNew/myApp/appInfo](https://open.imoulife.com/consoleNew/myApp/appInfo)
4. **Go to "My App" → "App Information"** and click Edit
5. **Fill in the required information** and copy your **App ID** and **App Secret**

> **Note**: These credentials are required for the integration to communicate with your Imou devices.

## 📥 Installation

### Option 1: HACS Installation (Recommended)

1. **Install HACS** if you haven't already ([HACS Installation Guide](https://hacs.xyz/docs/installation/installation/))
2. **Add this repository** to HACS:
   - Go to HACS → Integrations → Explore & Download Repositories
   - Search for "Imou Life"
   - Click "Download this repository with HACS"
3. **Restart Home Assistant**
4. **Add the integration** via Settings → Devices & Services → Add Integration

### Option 2: Manual Installation

1. **Download the latest release** from [GitHub Releases](https://github.com/maximunited/imou_life/releases)
2. **Extract the files** to your `custom_components/imou_life/` directory
3. **Restart Home Assistant**
4. **Add the integration** via Settings → Devices & Services → Add Integration

## ⚙️ Configuration

### Initial Setup

1. **Search for "Imou Life"** in the Add Integration screen
2. **Enter your credentials**:
   - **App ID**: Your Imou developer App ID
   - **App Secret**: Your Imou developer App Secret
3. **Choose discovery method**:
   - **Auto-discover devices**: Automatically finds all devices in your Imou account
   - **Manual device entry**: Enter a specific Device ID

### Device Configuration

Once added, each device will create several entities:

- **Switches**: Enable/disable push notifications and device features
- **Sensors**: Storage usage, callback URL, device status
- **Binary Sensors**: Online status, motion detection
- **Select**: Night vision mode selection
- **Buttons**: Restart device, refresh data, refresh motion alarm
- **Camera**: Live streaming and snapshots

### Advanced Configuration

After adding a device, you can configure advanced options:

- **Polling Interval**: How often to refresh device data (default: 15 minutes)
- **API Base URL**: Imou API endpoint (default: https://openapi.easy4ip.com/openapi)
- **API Timeout**: API call timeout in seconds (default: 10 seconds)
- **Callback URL**: For push notifications (requires internet exposure)

## 📊 Data Updates & Polling

The integration uses a **coordinator-based polling system** to keep device data up-to-date while respecting API rate limits.

### How Data Updates Work

1. **Data Update Coordinator**: Each device has a coordinator that manages data fetching and distribution to all entities
2. **Polling Interval**: Configurable update frequency (default: 900 seconds / 15 minutes)
3. **Parallel Updates Control**: Platform updates are serialized (`PARALLEL_UPDATES = 1`) to prevent API rate limiting
4. **Automatic Recovery**: Failed updates are logged and retried on the next interval

### Update Intervals

| Setting | Default Value | Configurable | Purpose |
|---------|---------------|--------------|---------|
| **Scan Interval** | 15 minutes (900s) | ✅ Yes (Options) | Balance freshness vs API calls |

**Note**: All devices (standard and battery-powered) use the same configurable scan interval. Battery-powered cameras have additional optimization features (sleep schedules, power-saving modes) but share the same polling frequency.

### Battery Device Optimization

Battery-powered cameras support additional features:
- **Smart scheduling**: Configurable sleep schedules (daily, weekly, custom, battery-based)
- **Power-saving modes**: Automatic optimization when battery is low
- **LED control**: Manage LED indicators to conserve power
- **Motion sensitivity**: Adjustable detection levels to reduce wake events

### API Rate Limiting

The Imou API has rate limits to protect their service:
- **Rate Limit Detection**: Automatic detection of `OP1013` rate limit errors
- **Error Handling**: Failed requests don't crash the integration
- **User Notification**: Persistent notification shown if rate-limited during setup
- **Retry Strategy**: Next update attempt waits for the current effective interval (temporarily increased while rate-limited)
- **Monitoring**: Check the API Status diagnostic sensor (disabled by default) for rate limit status

### Stale Device Detection

The integration automatically detects when a device no longer exists on your Imou account:
- **Automatic Detection**: Monitors for "device not found" API errors
- **Smart Threshold**: Requires 3 consecutive failures to avoid false positives
- **User Control**: Presents a repair issue in Settings → System → Repairs
- **Flexible Options**: Choose to Remove, Retry, or Ignore the warning
- **No Silent Deletion**: Device is only removed after explicit user confirmation

See [Stale Device Detection](docs/STALE_DEVICE_DETECTION.md) for detailed information.

### Customizing Update Frequency

To change polling intervals:

1. **Go to Settings** → Devices & Services → Imou Life
2. **Click Configure** on your device
3. **Adjust Options**:
   - `Scan Interval`: Seconds between updates (minimum: 60, recommended: 300-900)
   - Applies to all device data including battery status
4. **Save and Reload**

> **⚠️ Rate Limit Warning**: Setting intervals too low (< 5 minutes for multiple devices) may trigger API rate limits. The Imou developer account is limited to reasonable API call frequencies.

### Real-time Updates (Alternative)

For instant motion detection updates instead of polling:
- Use **Push Notifications** (see section below)
- Requires internet-accessible Home Assistant instance
- Bypasses polling for motion events only
- Other sensor data still uses polling

## 🔔 Push Notifications Setup

For real-time motion detection updates:

1. **Expose Home Assistant** to the internet (required)
2. **Set up a reverse proxy** (NGINX recommended)
3. **Configure callback URL** in the integration settings
4. **Enable push notifications** on one device (applies to all devices)
5. **Create the automation** for handling webhook events

> **Important**: Push notifications require Home Assistant to be exposed to the internet and behind a reverse proxy due to API limitations.

## 🎥 PTZ Controls

If your device supports PTZ (Pan-Tilt-Zoom), the integration provides:

- **`imou_life.ptz_location`**: Move to specific coordinates
- **`imou_life.ptz_move`**: Move in specific directions with duration

These services can be called from automations or manually via Developer Tools.

## 🚨 Motion Detection

The integration creates a "Motion Alarm" binary sensor that can be used in automations. You have three update options:

1. **Default**: Updates every 15 minutes (no internet required)
2. **Manual refresh**: Use the "Refresh Alarm" button or automation
3. **Push notifications**: Real-time updates (requires internet exposure)

## 🔧 Troubleshooting

### Common Issues

- **API Errors**: Verify your App ID and App Secret are correct
- **Device Not Found**: Ensure the device is registered in your Imou account
- **Push Notifications**: Check that Home Assistant is exposed to the internet and behind a reverse proxy

### Debug Logging

Enable debug logging for troubleshooting:

```yaml
logger:
  default: info
  logs:
    custom_components.imou_life: debug
    imouapi: debug
```

### Device Diagnostics

Download diagnostics from the device page in Home Assistant for detailed information.

## 📚 Documentation

- **[Complete Installation Guide](docs/INSTALLATION.md)** - Detailed setup and configuration
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and development setup
- **[Performance Guide](docs/PERFORMANCE_TROUBLESHOOTING.md)** - Optimization tips
- **[HACS Guide](docs/HACS_ENHANCEMENTS.md)** - HACS-specific features
- **[Changelog](docs/CHANGELOG.md)** - Version history and changes

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/maximunited/imou_life/issues)
- **Discussions**: [GitHub Discussions](https://github.com/maximunited/imou_life/discussions)
- **Wiki**: [Project Wiki](https://github.com/maximunited/imou_life/wiki)

## 🔄 Compatibility & Testing

### Python & Home Assistant Version Support

| Python Version | Home Assistant Support | Integration Status |
|----------------|------------------------|-------------------|
| **3.11** | 2023.3+ | ✅ **Fully Supported** (2024.2.0+) |
| **3.12** | 2024.2+ | ✅ **Fully Supported** (2024.2.0+) |
| **3.13** | 2024.12+ | ✅ **Fully Supported** (2024.2.0+) |
| **3.14** | 2025.6+ (estimated) | ✅ **Tested** (experimental) |

**Note**: Our integration requires Home Assistant 2024.2.0+ which automatically provides Python 3.11-3.13 compatibility. Python 3.14 support is tested in CI but may require Home Assistant 2025.6+ or later.

### Tested Environments
- **Home Assistant**: 2024.2.0 → 2025.8.3+ (latest)
- **Python**: 3.11, 3.12, 3.13, 3.14 (experimental)
- **Platforms**: Windows, macOS, Linux, Docker, Home Assistant OS
- **Architectures**: x86_64, ARM64, ARM32

### CI/CD Testing
- **GitHub Actions**: Automated testing on Python 3.11, 3.12, 3.13, 3.14
- **Coverage**: Maintains >60% test coverage across all versions
- **Quality**: Scrutinizer CI integration for code quality monitoring

## ⚠️ Important Notes

- **Unofficial Integration**: This is not supported by Imou
- **API Limitations**: Imou limits developer accounts to 5 devices
- **Internet Required**: Push notifications require Home Assistant to be internet-accessible
- **Reverse Proxy**: Required for push notifications due to API request formatting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original integration by [@user2684](https://github.com/user2684)
- Enhanced and maintained by [@maximunited](https://github.com/maximunited)
- Community contributors and testers

---

**Made with ❤️ for the Home Assistant community**
