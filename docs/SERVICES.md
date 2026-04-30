# Imou Life Services

The Imou Life integration provides several services for controlling your Imou devices. These services allow you to control PTZ cameras, manage battery optimization, and configure device settings.

## PTZ (Pan-Tilt-Zoom) Services

### imou_life.ptz_location

Move a PTZ camera to a specific location.

**Target:** Camera entities

**Parameters:**

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `horizontal` | number | -1 to 1 | 0 | Horizontal position (-1 = left, 0 = center, 1 = right) |
| `vertical` | number | -1 to 1 | 0 | Vertical position (-1 = down, 0 = center, 1 = up) |
| `zoom` | number | 0 to 1 | 0 | Zoom level (0 = no zoom, 1 = maximum zoom) |

**Example:**
```yaml
service: imou_life.ptz_location
target:
  entity_id: camera.living_room_camera
data:
  horizontal: 0.5    # Pan right
  vertical: 0.3      # Tilt up
  zoom: 0.2          # Slight zoom in
```

### imou_life.ptz_move

Move a PTZ camera in a specific direction for a duration.

**Target:** Camera entities

**Parameters:**

| Parameter | Type | Options | Default | Description |
|-----------|------|---------|---------|-------------|
| `operation` | select | UP, DOWN, LEFT, RIGHT, UPPER_LEFT, BOTTOM_LEFT, UPPER_RIGHT, BOTTOM_RIGHT, ZOOM_IN, ZOOM_OUT, STOP | - | Direction to move |
| `duration` | number | 100-10000 ms | 1000 | Duration of movement in milliseconds |

**Example:**
```yaml
service: imou_life.ptz_move
target:
  entity_id: camera.living_room_camera
data:
  operation: "UP"
  duration: 2000     # Move up for 2 seconds
```

## Battery Optimization Services

These services help optimize battery life for battery-powered Imou devices.

### imou_life.optimize_battery

Comprehensive battery optimization with multiple settings.

**Target:** Imou device entities

**Parameters:**

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `power_mode` | select | performance, balanced, power_saving, ultra_power_saving | Power consumption mode |
| `motion_sensitivity` | select | low, medium, high, ultra_high | Motion detection sensitivity |
| `recording_quality` | select | low, standard, high, ultra_high | Video recording quality |
| `led_indicators` | boolean | true/false | Enable/disable LED indicators |

**Example:**
```yaml
service: imou_life.optimize_battery
target:
  entity_id: camera.front_door
data:
  power_mode: "power_saving"
  motion_sensitivity: "medium"
  recording_quality: "standard"
  led_indicators: false
```

### imou_life.set_power_mode

Set the device power mode.

**Target:** Imou device entities

**Parameters:**

| Parameter | Type | Options | Required | Description |
|-----------|------|---------|----------|-------------|
| `power_mode` | select | performance, balanced, power_saving, ultra_power_saving | Yes | Power consumption mode |

**Power Modes:**
- `performance`: Maximum features, highest power consumption
- `balanced`: Good balance of features and power
- `power_saving`: Reduced features, lower power consumption
- `ultra_power_saving`: Minimal features, maximum battery life

**Example:**
```yaml
service: imou_life.set_power_mode
target:
  entity_id: camera.front_door
data:
  power_mode: "power_saving"
```

### imou_life.set_sleep_schedule

Configure when the device should enter sleep mode to conserve battery.

**Target:** Imou device entities

**Parameters:**

| Parameter | Type | Options | Required | Description |
|-----------|------|---------|----------|-------------|
| `sleep_schedule` | select | never, night_only, custom, battery_based | Yes | Sleep schedule type |
| `start_time` | time | HH:MM | If custom | When to start sleep mode |
| `end_time` | time | HH:MM | If custom | When to end sleep mode |

**Schedule Types:**
- `never`: Device never sleeps
- `night_only`: Sleep during typical night hours
- `custom`: Sleep during specified hours
- `battery_based`: Automatic sleep based on battery level

**Example:**
```yaml
service: imou_life.set_sleep_schedule
target:
  entity_id: camera.front_door
data:
  sleep_schedule: "custom"
  start_time: "23:00:00"
  end_time: "06:00:00"
```

### imou_life.set_motion_sensitivity

Set the motion detection sensitivity level.

**Target:** Imou device entities

**Parameters:**

| Parameter | Type | Options | Required | Description |
|-----------|------|---------|----------|-------------|
| `sensitivity` | select | low, medium, high, ultra_high | Yes | Sensitivity level |

**Sensitivity Levels:**
- `low`: Detects only significant motion, fewer false alarms
- `medium`: Balanced sensitivity
- `high`: Detects smaller movements, more sensitive
- `ultra_high`: Maximum sensitivity, may increase false alarms

**Example:**
```yaml
service: imou_life.set_motion_sensitivity
target:
  entity_id: camera.front_door
data:
  sensitivity: "medium"
```

### imou_life.set_recording_quality

Set the video recording quality (affects battery life and storage).

**Target:** Imou device entities

**Parameters:**

| Parameter | Type | Options | Required | Description |
|-----------|------|---------|----------|-------------|
| `quality` | select | low, standard, high, ultra_high | Yes | Recording quality |

**Quality Levels:**
- `low`: SD - 480p (lowest battery usage, lowest quality)
- `standard`: HD - 720p (balanced)
- `high`: Full HD - 1080p (higher battery usage, better quality)
- `ultra_high`: 2K/4K (highest battery usage, best quality)

**Example:**
```yaml
service: imou_life.set_recording_quality
target:
  entity_id: camera.front_door
data:
  quality: "standard"
```

### imou_life.enter_sleep_mode

Manually put the device into sleep mode immediately.

**Target:** Imou device entities

**No parameters required**

**Example:**
```yaml
service: imou_life.enter_sleep_mode
target:
  entity_id: camera.front_door
```

### imou_life.exit_sleep_mode

Wake up the device from sleep mode.

**Target:** Imou device entities

**No parameters required**

**Example:**
```yaml
service: imou_life.exit_sleep_mode
target:
  entity_id: camera.front_door
```

### imou_life.reset_power_settings

Reset all power and battery optimization settings to defaults.

**Target:** Imou device entities

**No parameters required**

**Example:**
```yaml
service: imou_life.reset_power_settings
target:
  entity_id: camera.front_door
```

## Automation Examples

### Example 1: PTZ Patrol

Create a simple patrol pattern for a PTZ camera:

```yaml
automation:
  - alias: "Camera Patrol"
    trigger:
      - platform: time_pattern
        minutes: "/5"  # Every 5 minutes
    action:
      - service: imou_life.ptz_location
        target:
          entity_id: camera.living_room
        data:
          horizontal: -0.5
          vertical: 0
      - delay:
          seconds: 3
      - service: imou_life.ptz_location
        target:
          entity_id: camera.living_room
        data:
          horizontal: 0.5
          vertical: 0
      - delay:
          seconds: 3
      - service: imou_life.ptz_location
        target:
          entity_id: camera.living_room
        data:
          horizontal: 0
          vertical: 0
```

### Example 2: Battery-Based Power Management

Automatically adjust settings based on battery level:

```yaml
automation:
  - alias: "Battery Low - Power Save"
    trigger:
      - platform: numeric_state
        entity_id: sensor.front_door_battery
        below: 20
    action:
      - service: imou_life.optimize_battery
        target:
          entity_id: camera.front_door
        data:
          power_mode: "ultra_power_saving"
          motion_sensitivity: "low"
          recording_quality: "low"
          led_indicators: false

  - alias: "Battery Charged - Normal Mode"
    trigger:
      - platform: numeric_state
        entity_id: sensor.front_door_battery
        above: 80
    action:
      - service: imou_life.optimize_battery
        target:
          entity_id: camera.front_door
        data:
          power_mode: "balanced"
          motion_sensitivity: "medium"
          recording_quality: "standard"
          led_indicators: true
```

### Example 3: Night Mode with Sleep Schedule

Optimize for battery at night:

```yaml
automation:
  - alias: "Night Mode"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: imou_life.set_sleep_schedule
        target:
          entity_id: camera.front_door
        data:
          sleep_schedule: "custom"
          start_time: "22:00:00"
          end_time: "06:00:00"
      - service: imou_life.set_power_mode
        target:
          entity_id: camera.front_door
        data:
          power_mode: "power_saving"
```

## Device Compatibility

- **PTZ Services**: Only available on cameras that support PTZ functionality
- **Battery Services**: Only available on battery-powered devices
- **Power Management**: Available on all devices, but most effective on battery-powered cameras

## Troubleshooting

### Service call fails

1. Check that the device supports the requested feature
2. Verify the device is online
3. Check Home Assistant logs for specific error messages
4. Ensure you're targeting the correct entity type (camera vs other entities)

### PTZ commands not working

1. Verify your camera supports PTZ (pan/tilt/zoom)
2. Check that the camera is not in sleep mode
3. Try smaller movements first to test functionality
4. Consult your camera's manual for PTZ capabilities

### Battery optimization not applying

1. Check that the device is battery-powered
2. Verify the device is not rate-limited by the Imou API
3. Check the API status sensor for any issues
4. Some settings may require the device to restart

## See Also

- [Configuration Guide](CONFIGURATION.md) - Options flow settings
- [Battery Optimization Guide](../docs/development/BATTERY_IMPROVEMENTS_SUMMARY.md) - Advanced battery features
- [Troubleshooting](PERFORMANCE_TROUBLESHOOTING.md) - Common issues and solutions
