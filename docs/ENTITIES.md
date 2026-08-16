# Entities and Functions

Reference for entities created by the Imou Life integration.

## Platforms

| Platform | Purpose |
| --- | --- |
| `camera` | Live stream and snapshots |
| `binary_sensor` | Motion and online status |
| `sensor` | Battery, storage, timestamps, diagnostics |
| `switch` | Push notifications and device toggles |
| `select` | Night vision and quality modes |
| `button` | Restart, refresh data, refresh alarm |
| `siren` | Alarm / siren control (where supported) |

Battery-powered models may also create entities from `battery_*` platforms when optimization is enabled.

## Device classes

Entities use Home Assistant device classes where applicable:

| Entity | Sensor name (API) | Device class |
| --- | --- | --- |
| Binary sensor | `motionAlarm` | `motion` |
| Sensor | `battery`, `batteryLevel` | `battery` |
| Sensor | `lastAlarm` | `timestamp` |
| Sensor | `batteryVoltage` | `voltage` |
| Sensor | `powerConsumption` | `power` |
| Button | `restartDevice` | `restart` |

Other sensors use translation keys and icons from `icons.json` without a device class.

## Common entities

### Camera

- Live stream (`stream` supported)
- Snapshot on demand
- PTZ via `imou_life.ptz_location` and `imou_life.ptz_move` services

### Binary sensors

- **Motion alarm** — `motion` class; primary automation trigger
- **Online** — connectivity (when exposed by API)

### Sensors

- **Battery** / **Battery level** — percentage
- **Storage used** — SD card usage (%)
- **Last alarm** — timestamp of last motion event
- **API status** — diagnostic; disabled by default

### Switches

Enabled by default (subset of API switches):

- Motion detection, audio detection, push notifications, and other model-specific toggles

**Push notifications** requires callback URL in options.

### Selects

- Night vision mode and similar multi-option settings (model-dependent)

### Buttons

| Button | Default enabled | Action |
| --- | --- | --- |
| Refresh data | No | Coordinator refresh |
| Refresh alarm | No | Updates motion sensor |
| Restart device | No | Remote reboot |

### Siren

- Turn on / off / toggle where the device exposes a siren channel

## Services

See [SERVICES.md](SERVICES.md) for PTZ parameters and examples.

## Translations

Entity names and states are translated in:

`ca`, `en`, `es-ES`, `fr`, `he`, `id`, `it-IT`, `pt-BR`

Exception messages for user actions are in `en.json` (other locales fall back as keys are added).

## Related docs

- [Data Updates](DATA_UPDATE.md)
- [Examples](EXAMPLES.md)
- [Supported Devices](SUPPORTED_DEVICES.md)
