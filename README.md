
# Imou Life - Home Assistant Integration

[![Home Assistant][ha-badge]][ha-url]
[![hacs_badge][hacs-badge]][hacs-url]
[![Imou Life][imou-badge]][imou-url]
[![Latest Release][release-badge]][release-url]
[![Quality Scale][quality-badge]][quality-url]
[![Buy Me a Coffee][coffee-badge]][coffee-url]

A Home Assistant integration for Imou Life cameras and devices, providing
comprehensive monitoring and control capabilities.

## 🚀 Features

- **Camera Integration**: Live video streaming and snapshot capture
- **Multi-Device Support**: Automatic discovery of new devices added to your Imou account
- **Motion Detection**: Real-time motion alerts and notifications
- **Device Control**: PTZ control, recording management, and more
- **Automation Ready**: Full Home Assistant automation support
- **HACS Compatible**: Easy installation through HACS

## 📋 Requirements

### System Requirements
- **Home Assistant**: 2024.2.0 or later
- **Python**: 3.11, 3.12, 3.13, 3.14
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

Configure options via Settings → Devices & Services → Imou Life → Configure:

- **Scan Interval**: Device data refresh frequency (default: 15 minutes)
- **API Settings**: Base URL, timeout, and server region selection
- **Push Notifications**: Callback URL for real-time motion alerts
- **Battery Optimization**: Sleep schedules and power-saving modes (battery devices only)
- **Discovery**: Enable/disable automatic device discovery (first device only)

## 🔄 Multi-Device Management

The integration **automatically discovers new devices** added to your Imou account - no reconfiguration needed!

**How It Works:**
- Checks for new devices every 60 minutes (configurable 5 min - 24 hours)
- Shows confirmation dialog when a new device is found
- Each device becomes a separate integration entry for independent management
- Shared API credentials - no need to re-enter

**Quick Start:**
1. Add your first device normally during setup
2. When you add more devices to your Imou account, they're automatically discovered
3. Approve the discovery notification to add them to Home Assistant

**Configuration:**
- Go to Settings → Devices & Services → Imou Life
- Click Configure on your **first device entry** (discovery options only show here)
- Toggle discovery on/off or adjust polling interval

See **[Multi-Device Guide](docs/MULTI_DEVICE_GUIDE.md)** for detailed scenarios, best practices, and troubleshooting.

## 📊 Data Updates & Polling

Device data updates every 15 minutes by default using a coordinator-based polling system.

**Adjusting Update Frequency:**
1. Go to Settings → Devices & Services → Imou Life
2. Click Configure on your device
3. Set `Scan Interval` (minimum: 60s, recommended: 300-900s)

> **⚠️ Warning**: Intervals below 5 minutes may trigger API rate limits with multiple devices.

**Alternative: Real-time Updates**
- Use Push Notifications for instant motion detection (requires internet-accessible HA)
- See [Push Notifications Setup](#-push-notifications-setup) below

**Advanced Features:**
- **API Rate Limiting**: Automatic detection and handling with interval adjustment
- **Stale Device Detection**: Auto-detects removed devices - see [Stale Device Detection](docs/STALE_DEVICE_DETECTION.md)
- **Battery Optimization**: Sleep schedules, power-saving modes for battery cameras

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

| Python Version | Home Assistant Version Required | Integration Support Status |
|----------------|--------------------------------|----------------------------|
| **3.11** | 2024.2+ | ✅ **Fully Supported** |
| **3.12** | 2024.2+ | ✅ **Fully Supported** |
| **3.13** | 2024.12+ | ✅ **Fully Supported** |
| **3.14** | 2026.4+ | ✅ **Fully Supported** |

**Note**: Our integration requires Home Assistant 2024.2.0 or later. Python 3.11 and 3.12 work with HA 2024.2+, Python 3.13 requires HA 2024.12+, and Python 3.14 requires HA 2026.4+.

### Tested Environments
- **Home Assistant**: 2024.2.0 → 2026.4.4+ (latest)
- **Python**: 3.11, 3.12, 3.13, 3.14
- **Platforms**: Windows, macOS, Linux, Docker, Home Assistant OS
- **Architectures**: x86_64, ARM64, ARM32

### CI/CD Testing
- **GitHub Actions**: Automated testing on Python 3.11, 3.12, 3.13, 3.14
- **Coverage**: Maintains ≥70% test coverage across all versions
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

<!-- Badge References -->
[ha-badge]: https://img.shields.io/badge/home%20assistant-%2341BDF5.svg?logo=home-assistant&logoColor=white
[ha-url]: https://www.home-assistant.io/
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-url]: https://github.com/custom-components/hacs
[imou-badge]: https://img.shields.io/badge/imou%20life-%23FF8C00.svg?logo=imou&logoColor=white
[imou-url]: https://open.imoulife.com/
[release-badge]: https://img.shields.io/badge/release-1.6.0-blue.svg
[release-url]: https://github.com/maximunited/imou_life/releases/tag/v1.6.0
[quality-badge]: https://img.shields.io/badge/quality%20scale-platinum%20%F0%9F%92%8E-blueviolet.svg
[quality-url]: https://developers.home-assistant.io/docs/core/integration-quality-scale/
[coffee-badge]: https://img.shields.io/badge/buy%20me%20a%20coffee-%23FFDD00.svg?logo=buy-me-a-coffee&logoColor=black
[coffee-url]: https://buymeacoffee.com/maxim_united
