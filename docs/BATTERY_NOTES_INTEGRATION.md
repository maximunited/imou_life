# Battery Notes Integration

The Imou Life integration is enhanced to work seamlessly with the [Battery Notes](https://github.com/andrew-codechimp/HA-Battery-Notes) custom integration for tracking battery-powered cameras.

## What is Battery Notes?

Battery Notes helps you track:
- When batteries were last replaced/charged
- Battery type and quantity
- Low battery alerts
- Battery life statistics

## Compatibility

### Automatic Detection

For **supported camera models**, the Imou Life integration automatically exposes battery metadata that Battery Notes can detect:

**Supported Models:**
- **Cell Series** (Rechargeable):
  - IPC-A26HP (Li-ion 5200mAh)
  - IPC-A26Z (Li-ion 5200mAh)

- **Cell 2 Series** (Rechargeable):
  - IPC-B46L (Li-ion 5200mAh, FRB20 battery)
  - IPC-B46LP (Li-ion 5200mAh, FRB20 battery)
  - IPC-B46LN (Li-ion 5200mAh, FRB20 battery)

- **Cell Pro Series** (Rechargeable):
  - IPC-A28HWP (Li-ion 10400mAh)

- **Cell Go Series** (Replaceable AA batteries):
  - IPC-A22E (4× AA, ~180 days typical life)
  - IPC-A22EP (4× AA, ~180 days typical life)

### Battery Sensor Attributes

The battery sensor (`sensor.<device>_battery`) exposes these attributes for Battery Notes:

```yaml
battery_type: "Rechargeable Li-ion 5200mAh"  # or "4× AA" for replaceable
battery_quantity: 1                          # Number of batteries
is_rechargeable: true                        # true for rechargeable, false for replaceable
typical_battery_life_days: 180               # Only for replaceable batteries
```

## Setup with Battery Notes

### Option 1: Automatic (Recommended)

If your camera model is supported, Battery Notes should automatically detect the battery type.

1. Install [Battery Notes](https://github.com/andrew-codechimp/HA-Battery-Notes) via HACS
2. Restart Home Assistant
3. Battery Notes should automatically create a battery tracker for your Imou camera

### Option 2: Manual Configuration

For cameras not yet in our database, or to override automatic detection:

1. Go to **Settings** → **Devices & Services** → **Battery Notes**
2. Click **Add Device**
3. Fill in:
   - **Device**: Select your Imou camera
   - **Battery Type**: Enter battery type (see specifications below)
   - **Battery Quantity**: Number of batteries
   - **Last Replaced**: When you last charged/replaced the battery

## Camera Battery Specifications

### Rechargeable Models

| Model | Battery Type | Capacity | Typical Charge Life |
|-------|--------------|----------|---------------------|
| IPC-A26HP | Li-ion | 5200mAh | 1-3 months* |
| IPC-A26Z | Li-ion | 5200mAh | 1-3 months* |
| IPC-B46L / IPC-B46LP / IPC-B46LN (Cell 2) | Li-ion (FRB20) | 5200mAh | 3-6 months* |
| IPC-A28HWP | Li-ion | 10400mAh | 3-6 months* |

*Depends on usage: motion events, live viewing frequency, WiFi signal strength, temperature

### Replaceable Battery Models

| Model | Battery Type | Quantity | Typical Life |
|-------|--------------|----------|--------------|
| IPC-A22E | AA | 4 | ~180 days |
| IPC-A22EP | AA | 4 | ~180 days |

**Note**: Typical life assumes:
- 10-15 motion events per day
- Minimal live viewing
- Good WiFi signal
- Moderate temperature (10-25°C)

## Tracking Battery Replacement/Charging

### For Rechargeable Cameras

Use the Battery Notes service to log when you charge your camera:

```yaml
service: battery_notes.set_battery_replaced
target:
  entity_id: sensor.<your_camera>_battery
data:
  datetime_replaced: "{{ now() }}"
```

Or use the Battery Notes UI to mark the battery as "charged".

### For Replaceable Battery Cameras

Log when you replace batteries:

```yaml
service: battery_notes.set_battery_replaced
target:
  entity_id: sensor.<your_camera>_battery
data:
  datetime_replaced: "{{ now() }}"
```

## Automation Examples

### Low Battery Alert

```yaml
automation:
  - alias: "Imou Camera Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.garage_cam_battery
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "Low Battery Alert"
          message: "Garage Cam battery is at {{ states('sensor.garage_cam_battery') }}%. Time to charge!"
```

### Remind to Charge After X Days

```yaml
automation:
  - alias: "Remind to Charge Camera"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: template
        value_template: >
          {{ (now() - states.sensor.garage_cam_battery.attributes.battery_last_replaced | as_datetime).days > 30 }}
    action:
      - service: notify.mobile_app
        data:
          title: "Camera Maintenance"
          message: "Garage Cam hasn't been charged in {{ (now() - states.sensor.garage_cam_battery.attributes.battery_last_replaced | as_datetime).days }} days"
```

## Adding Your Camera Model

If your Imou camera model isn't listed, you can help improve the integration:

1. **Find your model** in the device details (Settings → Devices → Your Camera)
2. **Look up specifications** on [Imou's official site](https://www.imoulife.com/)
3. **Submit a GitHub issue** with:
   - Model number (e.g., IPC-A26HP)
   - Battery type (Li-ion capacity OR AA/AAA count)
   - Whether rechargeable or replaceable

We'll add it to the `battery_types.py` database in the next release!

## Troubleshooting

### Battery Notes Doesn't Detect My Camera

**Check if model is supported:**
```yaml
# Developer Tools → Template
{{ state_attr('sensor.<your_camera>_battery', 'battery_type') }}
```

If this returns `None`, your camera model isn't in our database yet.

**Workaround**: Manually add to Battery Notes (see Option 2 above).

### Battery Type Shows Wrong Information

Please report this on [GitHub Issues](https://github.com/maximunited/imou_life/issues) with:
- Your camera model
- What the integration shows
- What it should be (from Imou specifications)

## Related Documentation

- [Battery Optimization Features](BATTERY_OPTIMIZATION.md)
- [Imou Battery Camera Specifications](https://www.imoulife.com/support)
- [Battery Notes Documentation](https://codechimp.org/HA-Battery-Notes/)
