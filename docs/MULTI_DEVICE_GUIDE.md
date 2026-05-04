# Multi-Device Management Guide

Complete guide to managing multiple Imou devices with automatic discovery.

## Table of Contents

- [How Automatic Discovery Works](#how-automatic-discovery-works)
- [Configuration](#configuration)
- [Usage Scenarios](#usage-scenarios)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## How Automatic Discovery Works

The integration automatically discovers new devices added to your Imou account:

1. **Background Polling**: Checks for new devices every 60 minutes (configurable 5 min - 24 hours)
2. **Confirmation Dialog**: When a new device is found, Home Assistant shows a confirmation dialog
3. **User Control**: You choose to add or dismiss the discovered device
4. **Shared Credentials**: New devices use the same API credentials as your first device
5. **Separate Entries**: Each device becomes its own integration entry for independent management

**Key Features:**
- ✅ Enabled by default - works out of the box
- ✅ User confirmation required - no surprise auto-adds
- ✅ Rate limit friendly - designed to respect Imou API limits
- ✅ Fully configurable - adjust polling interval or disable entirely

## Configuration

### Accessing Discovery Settings

1. Go to **Settings** → **Devices & Services** → **Imou Life**
2. Click **Configure** on your **first device entry**
3. Discovery options (only visible on first entry):
   - **Enable automatic device discovery**: Toggle on/off (default: enabled)
   - **Discovery polling interval**: 300-86400 seconds (default: 3600 / 60 minutes)

> **Note**: Discovery settings only appear on the first device you configured. All discovered devices automatically share the same API credentials.

### Adjusting the Polling Interval

- **Default (3600s / 60 min)**: Best balance for most users
- **Conservative (86400s / 24 hours)**: Minimal API calls if you rarely add devices
- **Active (900s / 15 min)**: When actively adding multiple devices

**Recommendation**: Keep the default 60-minute interval to avoid API rate limits.

## Usage Scenarios

### Scenario 1: Adding Your Second Camera

**Before:**
```
✓ Living Room Camera (configured manually)
```

**After 60 minutes:**
```
✓ Living Room Camera
🔔 New device discovered: "Backyard Camera" - [Add Device] [Dismiss]
```

**Click "Add Device":**
```
✓ Living Room Camera
✓ Backyard Camera (automatically configured)
```

---

### Scenario 2: Family Member Adds Camera

Your family member installs a new Imou camera and adds it to your shared account.

**Before:**
```
✓ Front Door Camera
✓ Garage Camera
```

**Within 60 minutes:**
```
✓ Front Door Camera
✓ Garage Camera
🔔 Notification: "New Imou device discovered: Driveway Camera"
```

**After accepting:**
```
✓ Front Door Camera
✓ Garage Camera
✓ Driveway Camera (automatically added with all entities)
```

**No re-configuration needed** - API credentials are automatically shared!

---

### Scenario 3: Managing Multiple Locations

Perfect for managing cameras at home, office, and vacation properties.

**Setup Steps:**
1. Add all devices to your Imou account
2. Configure the integration once with your API credentials
3. Select your first device during initial setup
4. All other devices are automatically discovered within 60 minutes

**Result:**
```
✓ Home - Living Room
✓ Home - Kitchen
✓ Home - Front Door
✓ Office - Reception
✓ Office - Conference Room
✓ Vacation Home - Entrance
```

**Management Benefits:**
- Remove devices individually from Settings → Devices & Services
- Configure each device independently (different polling intervals, etc.)
- Use devices in separate automations
- Each device has its own entity list

## Best Practices

### When to Disable Discovery

- **Single Device Setup**: You only have one camera and won't be adding more
- **Manual Control**: You prefer to manually add all devices
- **Testing/Development**: Avoid automatic discovery during integration testing

**To disable**: Go to first device's configuration options and toggle off "Enable automatic device discovery"

### When to Adjust the Interval

| Interval | When to Use |
|----------|-------------|
| **15 minutes (900s)** | Actively adding multiple devices, need fast discovery |
| **60 minutes (3600s)** | Default - best balance for most users |
| **24 hours (86400s)** | Rarely add devices, want minimal API calls |

**Warning**: Intervals below 15 minutes may trigger API rate limits with multiple devices.

### Managing Discovered Devices

Each discovered device:
- Appears as a separate integration entry in Devices & Services
- Can be removed independently (won't affect other devices)
- Has its own configuration options (scan interval, API settings, etc.)
- Creates its own set of entities (camera, switches, sensors, etc.)

**Discovery coordinator runs only on the first device entry** - removing the first device automatically transfers discovery to the next entry.

## Troubleshooting

### Discovery Not Working

**Check these settings:**
1. Is discovery enabled? (First device → Configure → Enable automatic device discovery)
2. Is the device registered on your Imou account? (Check Imou Life mobile app)
3. Has 60 minutes passed since the device was added?
4. Check Home Assistant logs for discovery errors: `Settings → System → Logs`

### Device Already Configured

If you see "already configured" when trying to add a device:
- The device already exists as an integration entry
- Check Settings → Devices & Services → Imou Life for existing entries
- Each device can only be added once (prevents duplicates)

### Rate Limit Errors During Discovery

If discovery triggers rate limits:
- Increase the discovery interval (Settings → Devices & Services → Imou Life → Configure first device)
- Default 60-minute interval is designed to avoid rate limits
- Check the API Status diagnostic sensor for rate limit details

### First Device Removal

When you remove the first device:
- Discovery automatically transfers to the next device entry
- No manual reconfiguration needed
- Discovery settings are preserved
- Removing the last device stops discovery completely

## Advanced: Discovery Architecture

**Technical Details:**
- Uses `ImouDiscoveryCoordinator` for background polling
- Implements unique_id enforcement to prevent duplicate entries
- Gracefully handles API rate limits (logs debug, non-critical failure)
- Event-based cleanup system for entry lifecycle management
- Dynamic config entry creation pattern (1:1 entry-to-device mapping)

**API Efficiency:**
- Single discovery poll covers all devices in your account
- Conservative 60-minute default respects Imou API rate limits
- Discovery runs only from first entry (no duplicate API calls)
- Automatic retry on transient failures

---

**Need Help?**
- [GitHub Issues](https://github.com/maximunited/imou_life/issues) - Report bugs or request features
- [GitHub Discussions](https://github.com/maximunited/imou_life/discussions) - Ask questions
- [Project Wiki](https://github.com/maximunited/imou_life/wiki) - Additional documentation
