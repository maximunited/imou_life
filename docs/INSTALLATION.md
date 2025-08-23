# Imou Life Integration - Complete Installation Guide

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

**PLEASE NOTE**: This is an UNOFFICIAL integration, NOT supported or validated by Imou or linked in any way to Imou.

> **Note**: This is a fork of [user2684/imou_life](https://github.com/user2684/imou_life) with additional improvements and fixes.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting Imou API Credentials](#getting-imou-api-credentials)
3. [Installation Methods](#installation-methods)
4. [Initial Configuration](#initial-configuration)
5. [Device Setup](#device-setup)
6. [Advanced Configuration](#advanced-configuration)
7. [Push Notifications Setup](#push-notifications-setup)
8. [Motion Detection Configuration](#motion-detection-configuration)
9. [PTZ Controls](#ptz-controls)
10. [Troubleshooting](#troubleshooting)
11. [Limitations and Known Issues](#limitations-and-known-issues)

## 🔑 Prerequisites

Before installing the integration, ensure you have:

- **Home Assistant**: Version 2023.8.0 or later
- **Imou Life Account**: Valid account with registered devices
- **Internet Access**: Required for API communication and push notifications
- **Reverse Proxy**: Required for push notifications (NGINX recommended)

## 🔐 Getting Imou API Credentials

The integration requires valid `App ID` and `App Secret` from Imou's developer platform:

### Step 1: Register on Imou Life
1. Download and install the Imou Life app
2. Create an account and register your devices
3. Ensure your devices are working properly in the app

### Step 2: Create Developer Account
1. Visit [https://open.imoulife.com](https://open.imoulife.com)
2. Click "Register" and create a developer account
3. Verify your email address

### Step 3: Get API Credentials
1. Access the [Imou Console](https://open.imoulife.com/consoleNew/myApp/appInfo)
2. Go to "My App" → "App Information"
3. Click "Edit" and fill in the required information:
   - **App Name**: Choose a descriptive name
   - **App Description**: Brief description of your use case
   - **Category**: Select appropriate category
4. **Copy your App ID and App Secret** - you'll need these for the integration

> **Important**: Keep your App Secret secure and don't share it publicly.

## 📥 Installation Methods

### Method 1: HACS Installation (Recommended)

#### Prerequisites
- [HACS](https://hacs.xyz/) must be installed and configured in your Home Assistant instance

#### Installation Steps
1. **Open HACS** in Home Assistant
2. **Go to Integrations** → **Explore & Download Repositories**
3. **Search for "Imou Life"**
4. **Click "Download this repository with HACS"**
5. **Restart Home Assistant**
6. **Add the integration** via Settings → Devices & Services → Add Integration

### Method 2: Manual Installation

#### Prerequisites
- Access to your Home Assistant configuration directory
- Ability to restart Home Assistant

#### Installation Steps
1. **Navigate to your Home Assistant configuration directory** (where `configuration.yaml` is located)
2. **Create the custom_components directory** if it doesn't exist:
   ```bash
   mkdir custom_components
   ```
3. **Create the imou_life directory**:
   ```bash
   mkdir custom_components/imou_life
   ```
4. **Download the integration files**:
   - Go to [GitHub Releases](https://github.com/maximunited/imou_life/releases)
   - Download the latest release ZIP file
   - Extract all files to `custom_components/imou_life/`
5. **Restart Home Assistant**
6. **Add the integration** via Settings → Devices & Services → Add Integration

## ⚙️ Initial Configuration

### Step 1: Add Integration
1. **Go to Settings** → **Devices & Services**
2. **Click the "+" button** to add a new integration
3. **Search for "Imou Life"**
4. **Click on the integration** to start configuration

### Step 2: Enter Credentials
1. **App ID**: Enter your Imou developer App ID
2. **App Secret**: Enter your Imou developer App Secret
3. **Click "Submit"**

### Step 3: Choose Discovery Method
You have two options for adding devices:

#### Option A: Auto-Discover Devices
- **Check "Discover registered devices"**
- The integration will automatically find all devices in your Imou account
- Select the devices you want to add
- Optionally provide custom names

#### Option B: Manual Device Entry
- **Uncheck "Discover registered devices"**
- **Device ID**: Enter the specific Device ID of the device you want to add
- **Device Name**: Optionally provide a custom name

## 📱 Device Setup

### Automatic Device Discovery
When using auto-discovery:
1. **Review the device list** presented by the integration
2. **Select devices** you want to add to Home Assistant
3. **Provide custom names** if desired (optional)
4. **Click "Submit"** to add the selected devices

### Manual Device Entry
When adding devices manually:
1. **Find your Device ID** in the Imou Life app or console
2. **Enter the Device ID** in the configuration
3. **Provide a custom name** if desired
4. **Click "Submit"** to add the device

### What Gets Created
Each device will create several entities in Home Assistant:

#### Core Entities
- **Device**: Main device entity with device information
- **Camera**: Live streaming and snapshot capabilities

#### Control Entities
- **Switches**: Enable/disable features and push notifications
- **Buttons**: Restart device, refresh data, refresh motion alarm
- **Select**: Night vision mode selection

#### Sensor Entities
- **Binary Sensors**: Online status, motion detection
- **Sensors**: Storage usage, callback URL, device status

## 🔧 Advanced Configuration

### Accessing Advanced Settings
After adding a device:
1. **Go to Settings** → **Devices & Services**
2. **Find your Imou Life integration**
3. **Click "Configure"**

### Configurable Options

#### Polling Interval
- **Description**: How often to refresh device data
- **Default**: 15 minutes (900 seconds)
- **Range**: 30 seconds to 24 hours
- **Recommendation**: 15 minutes for most use cases

#### API Base URL
- **Description**: Imou API endpoint
- **Default**: `https://openapi.easy4ip.com/openapi`
- **Note**: Usually doesn't need to be changed

#### API Timeout
- **Description**: API call timeout in seconds
- **Default**: 10 seconds
- **Range**: 5 to 60 seconds
- **Recommendation**: 10-15 seconds

#### Callback URL
- **Description**: URL for push notifications
- **Format**: `https://your-domain.com/api/webhook/unique-string`
- **Required**: Only if using push notifications
- **Note**: Must be accessible from the internet

## 🔔 Push Notifications Setup

### Overview
Push notifications provide real-time updates for motion detection and other events. They require:
- Home Assistant exposed to the internet
- Reverse proxy configuration
- Webhook automation setup

### Step 1: Internet Exposure
1. **Configure Home Assistant** to be accessible from the internet
2. **Set up a reverse proxy** (NGINX recommended)
3. **Ensure proper security** (HTTPS, authentication, etc.)

### Step 2: Configure Callback URL
1. **Go to integration settings** (Configure button)
2. **Set Callback URL** to: `https://your-domain.com/api/webhook/imou_life_callback_123`
3. **Replace parts**:
   - `your-domain.com` with your actual domain
   - `imou_life_callback_123` with a unique, hard-to-guess string

### Step 3: Enable Push Notifications
1. **Go to your device page** in Home Assistant
2. **Find the "Push Notifications" switch**
3. **Enable the switch**
4. **Note**: This applies to ALL devices in your Imou account

### Step 4: Create Webhook Automation
Create this automation in Home Assistant:

```yaml
alias: Imou Push Notifications
description: "Handle Imou push notifications for motion detection"
trigger:
  - platform: webhook
    webhook_id: imou_life_callback_123  # Replace with your unique string
condition:
  - condition: template
    value_template: |
      {% for entity_name in integration_entities("imou_life") %}
        {%- if entity_name is match('.+_refreshalarm$') and is_device_attr(entity_name, "hw_version", trigger.json.did) %}
          true
        {%-endif%}
        {% else %}
          false
      {%- endfor %}
  - condition: template
    value_template: |-
      {%- if trigger.json.msgType in ("videoMotion", "human", "openCamera") %}
        true
      {% else %}
        false
      {%-endif%}
action:
  - service: button.press
    data: {}
    target:
      entity_id: |
        {% for entity_name in integration_entities("imou_life") %}
          {%- if entity_name is match('.+_refreshalarm$') and is_device_attr(entity_name, "hw_version", trigger.json.did) %}
            {{entity_name}}
          {%-endif%}
        {%- endfor %}
    enabled: true
mode: queued
max: 10
```

**Important Notes**:
- Replace `imou_life_callback_123` with your actual webhook ID
- The API limits push notification changes to 10 times per day
- Changes may take up to 5 minutes to apply

## 🚨 Motion Detection Configuration

### Motion Sensor Overview
The integration creates a "Motion Alarm" binary sensor that detects motion events. You have three update options:

### Option 1: Default Polling (No Internet Required)
- **Update Frequency**: Every 15 minutes (or your configured polling interval)
- **Pros**: No internet exposure required, simple setup
- **Cons**: Delayed updates, may miss short events
- **Best For**: Basic monitoring, no real-time requirements

### Option 2: Manual Refresh
- **Update Frequency**: On-demand via button or automation
- **Setup**: Create automation to press the "Refresh Alarm" button
- **Example Automation**:
```yaml
alias: Imou - Refresh Alarm
description: "Refresh motion alarm sensor every 30 seconds"
trigger:
  - platform: time_pattern
    seconds: "30"
action:
  - service: button.press
    data: {}
    target:
      entity_id: button.your_device_refreshalarm  # Replace with your entity
mode: single
```

**Note**: Imou API is limited to 20,000 calls per day.

### Option 3: Push Notifications (Real-time)
- **Update Frequency**: Real-time when motion is detected
- **Pros**: Immediate updates, no polling required
- **Cons**: Requires internet exposure and reverse proxy
- **Best For**: Security applications, real-time monitoring

## 🎥 PTZ Controls

### Overview
If your device supports PTZ (Pan-Tilt-Zoom), the integration provides two services for camera control.

### Available Services

#### `imou_life.ptz_location`
Moves the camera to specific coordinates.

**Parameters**:
- **horizontal**: Pan position (-1.0 to 1.0)
- **vertical**: Tilt position (-1.0 to 1.0)
- **zoom**: Zoom level (0.0 to 1.0)

**Example**:
```yaml
service: imou_life.ptz_location
data:
  horizontal: 0.5
  vertical: -0.3
  zoom: 0.8
target:
  entity_id: camera.your_device
```

#### `imou_life.ptz_move`
Moves the camera in specific directions.

**Parameters**:
- **operation**: Movement direction
  - Basic: "UP", "DOWN", "LEFT", "RIGHT"
  - Diagonal: "UPPER_LEFT", "BOTTOM_LEFT", "UPPER_RIGHT", "BOTTOM_RIGHT"
  - Zoom: "ZOOM_IN", "ZOOM_OUT"
  - Control: "STOP"
- **duration**: Movement duration in milliseconds

**Example**:
```yaml
service: imou_life.ptz_move
data:
  operation: "UP"
  duration: 2000
target:
  entity_id: camera.your_device
```

### Testing PTZ Controls
1. **Go to Developer Tools** → **Services**
2. **Select the PTZ service** you want to test
3. **Choose your camera entity** as the target
4. **Fill in the parameters**
5. **Click "Call Service"**

### Creating PTZ Presets
Since the Imou API doesn't support presets, you can create them using Home Assistant scripts:

```yaml
# Example: Home position preset
alias: "PTZ - Home Position"
sequence:
  - service: imou_life.ptz_location
    data:
      horizontal: 0
      vertical: 0
      zoom: 0.5
    target:
      entity_id: camera.your_device
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### API Authentication Errors
**Symptoms**: "Invalid credentials" or "Authentication failed"
**Solutions**:
1. Verify your App ID and App Secret are correct
2. Check that your Imou developer account is active
3. Ensure the credentials haven't expired

#### Device Not Found
**Symptoms**: "Device not found" or "Device ID invalid"
**Solutions**:
1. Verify the device is registered in your Imou Life account
2. Check that the device is online in the Imou app
3. Ensure the device ID is entered correctly

#### Push Notifications Not Working
**Symptoms**: No real-time updates, webhook errors
**Solutions**:
1. Verify Home Assistant is exposed to the internet
2. Check reverse proxy configuration
3. Ensure the callback URL is correct and accessible
4. Verify the webhook automation is active

#### Motion Detection Delays
**Symptoms**: Motion sensor updates slowly or not at all
**Solutions**:
1. Check your polling interval setting
2. Verify the device supports motion detection
3. Consider using push notifications for real-time updates

### Debug Logging

Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: info
  logs:
    custom_components.imou_life: debug
    imouapi: debug
```

### Device Diagnostics

1. **Go to your device page** in Home Assistant
2. **Click "Download Diagnostics"**
3. **Review the information** for errors or configuration issues
4. **Include diagnostics** when reporting issues

### Getting Help

1. **Check the logs** for error messages
2. **Review this documentation** for configuration details
3. **Search existing issues** on GitHub
4. **Create a new issue** with:
   - Detailed error description
   - Device model and firmware
   - Home Assistant version
   - Debug logs and diagnostics
   - Steps to reproduce the issue

## ⚠️ Limitations and Known Issues

### API Limitations
- **Device Limit**: Imou limits developer accounts to 5 devices
- **API Calls**: Limited to 20,000 calls per day
- **Push Notifications**: Limited to 10 configuration changes per day

### Technical Limitations
- **Event Streaming**: Imou API doesn't provide real-time event streams
- **Polling Required**: Integration must poll devices for status updates
- **Request Formatting**: Imou API sends malformed HTTP requests (requires reverse proxy)

### Known Issues
- **Configuration Sync**: Changes in Imou Life app may take several minutes to appear in Home Assistant
- **Device Sharing**: Some devices may not work properly when shared between accounts
- **Firmware Compatibility**: Newer device firmware may not be fully compatible

### Workarounds

#### Multiple Device Accounts
If you need to control more than 5 devices:
1. **Create additional Imou accounts** with different email addresses
2. **Get new App ID and App Secret** for each account
3. **Add devices** through different integration instances
4. **Alternative**: Share devices between accounts and add through the primary account

#### Real-time Updates
For real-time motion detection:
1. **Use push notifications** instead of polling
2. **Set up proper reverse proxy** (NGINX recommended)
3. **Configure webhook automation** for immediate response

## 📚 Additional Resources

- **[Development Guide](DEVELOPMENT.md)**: Contributing and development setup
- **[Performance Guide](PERFORMANCE_TROUBLESHOOTING.md)**: Optimization tips
- **[HACS Guide](HACS_ENHANCEMENTS.md)**: HACS-specific features
- **[Changelog](CHANGELOG.md)**: Version history and changes
- **[Project Wiki](https://github.com/maximunited/imou_life/wiki)**: Additional documentation and examples

## 🤝 Support and Contributing

- **Issues**: [GitHub Issues](https://github.com/maximunited/imou_life/issues)
- **Discussions**: [GitHub Discussions](https://github.com/maximunited/imou_life/discussions)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines

---

**Note**: This integration is based on reverse-engineered Imou APIs and may not work with all device models or firmware versions. For official support, consider using the [official Imou Home Assistant integration](https://github.com/Imou-OpenPlatform/Imou-Home-Assistant).
