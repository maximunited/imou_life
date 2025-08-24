# Battery Optimization Features

The IMOU Life integration now includes comprehensive battery optimization features to help extend the battery life of your IMOU devices.

## Overview

Battery optimization automatically adjusts device settings based on battery level and user preferences to maximize battery life while maintaining essential functionality.

## Features

### 1. Power Modes

- **Performance Mode**: Maximum functionality, higher power consumption
- **Balanced Mode**: Balanced performance and power consumption
- **Power Saving Mode**: Reduced functionality, lower power consumption
- **Ultra Power Saving Mode**: Minimal functionality, lowest power consumption

### 2. Motion Sensitivity Control

- **Low**: Minimal motion detection, saves battery
- **Medium**: Balanced detection and battery life
- **High**: Maximum motion detection, higher power consumption
- **Ultra High**: Extreme sensitivity for critical areas

### 3. Recording Quality Settings

- **Low**: Lower resolution, longer battery life
- **Standard**: Balanced quality and battery life
- **High**: Higher resolution, moderate battery consumption
- **Ultra High**: Maximum quality, highest power consumption

### 4. Sleep Schedule Management

- **Never**: Device stays active 24/7
- **Night Only**: Automatic sleep during night hours (10 PM - 6 AM)
- **Custom**: User-defined sleep schedule
- **Battery Based**: Sleep mode activates when battery is low

### 5. LED Indicator Control

- Enable/disable LED indicators to save power
- Automatic LED management based on battery level

### 6. Auto-Sleep Features

- Automatic sleep mode activation based on battery threshold
- Configurable battery threshold (5% - 50%)
- Smart wake-up when motion is detected

## Configuration

### Basic Settings

Configure battery optimization in the integration options:

1. Go to **Devices & Services** → **Integrations**
2. Find your IMOU Life integration and click **Configure**
3. Adjust the following settings:

```
Battery Optimization: Enabled
Power Saving Mode: Enabled
Motion Sensitivity: Medium
Recording Quality: Standard
LED Indicators: Enabled
Auto Sleep: Disabled
Battery Threshold: 20%
Sleep Schedule: Night Only
```

### Advanced Configuration

#### Custom Sleep Schedule

For custom sleep schedules, you can set specific start and end times:

```yaml
# Example: Sleep from 11 PM to 7 AM
sleep_schedule: "custom"
sleep_start_time: "23:00"
sleep_end_time: "07:00"
```

#### Battery Threshold Configuration

Set the battery level at which optimization activates:

- **5%**: Very aggressive optimization
- **20%**: Recommended default
- **50%**: Conservative optimization

## Entities

### Sensors

- **Battery Level**: Current battery percentage
- **Battery Voltage**: Battery voltage reading
- **Power Consumption**: Current power usage in watts
- **Sleep Mode Status**: Current sleep mode state
- **Power Saving Status**: Power saving mode status

### Binary Sensors

- **Low Battery**: True when battery is below threshold
- **Charging**: True when device is charging
- **Power Saving Active**: True when power saving is enabled
- **Sleep Mode Active**: True when device is in sleep mode

### Select Entities

- **Power Mode**: Choose power mode (Performance/Balanced/Power Saving/Ultra Power Saving)
- **Motion Sensitivity**: Set motion detection sensitivity
- **Recording Quality**: Choose recording quality level
- **Sleep Schedule**: Configure sleep schedule type

### Buttons

- **Enter Sleep Mode**: Manually activate sleep mode
- **Exit Sleep Mode**: Wake up device from sleep mode
- **Optimize Battery**: Apply optimal battery settings
- **Reset Power Settings**: Reset all settings to defaults

### Switches

- **Power Saving Mode**: Enable/disable power saving
- **Auto Sleep**: Enable automatic sleep mode
- **LED Indicators**: Control LED indicator lights
- **Motion Sensitivity**: Enable/disable motion sensitivity control

## Services

### optimize_battery

Optimize device battery settings for maximum battery life.

```yaml
service: imou_life.optimize_battery
target:
  entity_id: select.garage_camera_power_mode
data:
  power_mode: "power_saving"
  motion_sensitivity: "low"
  recording_quality: "low"
  led_indicators: false
```

### set_power_mode

Set the power mode for the device.

```yaml
service: imou_life.set_power_mode
target:
  entity_id: select.garage_camera_power_mode
data:
  power_mode: "balanced"
```

### set_sleep_schedule

Configure when the device should enter sleep mode.

```yaml
service: imou_life.set_sleep_schedule
target:
  entity_id: select.garage_camera_sleep_schedule
data:
  sleep_schedule: "custom"
  start_time: "22:00"
  end_time: "06:00"
```

### set_motion_sensitivity

Set the motion detection sensitivity level.

```yaml
service: imou_life.set_motion_sensitivity
target:
  entity_id: select.garage_camera_motion_sensitivity
data:
  sensitivity: "medium"
```

### set_recording_quality

Set the recording quality (affects battery life).

```yaml
service: imou_life.set_recording_quality
target:
  entity_id: select.garage_camera_recording_quality
data:
  quality: "standard"
```

### enter_sleep_mode

Manually put the device into sleep mode.

```yaml
service: imou_life.enter_sleep_mode
target:
  entity_id: button.garage_camera_enter_sleep_mode
```

### exit_sleep_mode

Wake up the device from sleep mode.

```yaml
service: imou_life.exit_sleep_mode
target:
  entity_id: button.garage_camera_exit_sleep_mode
```

### reset_power_settings

Reset all power and battery optimization settings to defaults.

```yaml
service: imou_life.reset_power_settings
target:
  entity_id: button.garage_camera_reset_power_settings
```

## Automation Examples

### Automatic Battery Optimization

```yaml
automation:
  - alias: "Optimize Battery When Low"
    trigger:
      platform: numeric_state
      entity_id: sensor.garage_camera_battery_level
      below: 20
    action:
      - service: imou_life.optimize_battery
        target:
          entity_id: select.garage_camera_power_mode
        data:
          power_mode: "power_saving"
          motion_sensitivity: "low"
          recording_quality: "low"
          led_indicators: false
```

### Night Mode Sleep Schedule

```yaml
automation:
  - alias: "Night Mode Sleep Schedule"
    trigger:
      platform: time
      at: "22:00"
    action:
      - service: imou_life.enter_sleep_mode
        target:
          entity_id: button.garage_camera_enter_sleep_mode

  - alias: "Wake Up in Morning"
    trigger:
      platform: time
      at: "06:00"
    action:
      - service: imou_life.exit_sleep_mode
        target:
          entity_id: button.garage_camera_exit_sleep_mode
```

### Motion-Based Wake Up

```yaml
automation:
  - alias: "Wake Up on Motion Detection"
    trigger:
      platform: state
      entity_id: binary_sensor.garage_camera_motion_alarm
      to: "on"
    condition:
      - condition: state
        entity_id: binary_sensor.garage_camera_sleep_mode_active
        state: "on"
    action:
      - service: imou_life.exit_sleep_mode
        target:
          entity_id: button.garage_camera_exit_sleep_mode
```

## Best Practices

### 1. Battery Level Monitoring

- Monitor battery level regularly
- Set appropriate battery thresholds
- Use battery-based sleep schedules for critical devices

### 2. Motion Detection Optimization

- Use lower sensitivity during quiet hours
- Adjust sensitivity based on area importance
- Consider time-based sensitivity changes

### 3. Recording Quality Management

- Use lower quality for general monitoring
- Reserve high quality for critical events
- Implement quality-based recording schedules

### 4. Sleep Schedule Planning

- Plan sleep schedules around usage patterns
- Use custom schedules for irregular patterns
- Consider battery-based schedules for mobile devices

### 5. Power Mode Selection

- Use performance mode sparingly
- Default to balanced mode for most scenarios
- Enable power saving for extended battery life

## Troubleshooting

### Common Issues

1. **Device Not Entering Sleep Mode**
   - Check sleep schedule configuration
   - Verify battery threshold settings
   - Ensure auto-sleep is enabled

2. **Battery Optimization Not Working**
   - Verify battery optimization is enabled
   - Check coordinator status
   - Review log messages for errors

3. **Settings Not Persisting**
   - Check configuration entry options
   - Verify entity state updates
   - Review coordinator data flow

### Debug Information

Enable debug logging to troubleshoot issues:

```yaml
logger:
  custom_components.imou_life: debug
```

### Support

For issues with battery optimization features:

1. Check the integration logs
2. Verify device compatibility
3. Review configuration settings
4. Check Home Assistant community forums

## Future Enhancements

Planned improvements for battery optimization:

- Machine learning-based optimization
- Weather-based power management
- Integration with solar power systems
- Advanced sleep pattern recognition
- Cloud-based optimization recommendations
