# Automation Examples

Ready-to-use Home Assistant automations for Imou Life devices.

Replace `binary_sensor.front_door_motion_alarm` and entity IDs with yours from **Developer Tools → States**.

## Motion-activated notification

```yaml
automation:
  - alias: "Imou motion notification"
    triggers:
      - trigger: state
        entity_id: binary_sensor.front_door_motion_alarm
        to: "on"
    actions:
      - action: notify.mobile_app_your_phone
        data:
          title: "Motion detected"
          message: "Front door camera saw movement."
```

## Turn on outdoor light when motion detected (night only)

```yaml
automation:
  - alias: "Imou motion light at night"
    triggers:
      - trigger: state
        entity_id: binary_sensor.garden_motion_alarm
        to: "on"
    conditions:
      - condition: sun
        after: sunset
        before: sunrise
    actions:
      - action: light.turn_on
        target:
          entity_id: light.garden_flood
```

## Low battery alert

```yaml
automation:
  - alias: "Imou battery low"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.garden_battery
        below: 20
    actions:
      - action: notify.persistent_notification
        data:
          message: "Garden camera battery is below 20%."
```

## Snapshot on motion (for logging)

```yaml
automation:
  - alias: "Imou motion snapshot"
    triggers:
      - trigger: state
        entity_id: binary_sensor.driveway_motion_alarm
        to: "on"
    actions:
      - action: camera.snapshot
        target:
          entity_id: camera.driveway_live
        data:
          filename: "/config/www/snapshots/driveway_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
```

## PTZ preset via script

```yaml
script:
  imou_look_at_door:
    sequence:
      - action: imou_life.ptz_location
        target:
          entity_id: camera.porch_live
        data:
          horizontal: 0.5
          vertical: 0.0
          zoom: 0.0
```

## Disable push notifications when away (optional)

```yaml
automation:
  - alias: "Imou push off when nobody home"
    triggers:
      - trigger: state
        entity_id: zone.home
        to: "0"
    actions:
      - action: switch.turn_off
        target:
          entity_id: switch.camera_push_notifications
```

> Push notifications require a publicly reachable callback URL in integration options. See [Limitations](LIMITATIONS.md).

## Related docs

- [Services](SERVICES.md) — PTZ service reference
- [Entities](ENTITIES.md) — available entity types
- [Use Cases](USE_CASES.md) — common setup patterns
