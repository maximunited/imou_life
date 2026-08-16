# Data Updates

How the Imou Life integration keeps entity states current in Home Assistant.

## Polling model

Each device has its own config entry and coordinator (`ImouDataUpdateCoordinator`). The coordinator polls the Imou OpenAPI on a schedule and pushes fresh values to all entities for that device.

| Setting | Default | Where to change |
| --- | --- | --- |
| Scan interval | 15 minutes | Integration **Options** → Polling interval |
| Setup timeout | 30 seconds | Integration **Options** → Setup timeout |
| API timeout | Library default | Integration **Options** → API timeout |

Battery-powered devices can use a separate battery coordinator with power-saving schedules. See [Battery Optimization](BATTERY_OPTIMIZATION.md).

## Tiered polling

To reduce API usage, the coordinator alternates between:

1. **Fast poll** — critical sensors only (online status, motion, battery)
2. **Full poll** — all sensors on the device

Full polls run every third cycle by default. Entity states still update on the configured scan interval; non-critical sensors may lag one cycle during fast polls.

## What triggers an immediate refresh

| Action | Behavior |
| --- | --- |
| **Refresh Data** button | Calls `coordinator.async_request_refresh()` |
| **Refresh Alarm** button | Re-fetches the `motionAlarm` sensor and updates HA state |
| Config entry reload | Full setup + initial coordinator refresh |
| Re-authentication / reconfigure success | Config entry reload |
| Manual **Reload** on integration | Unload + setup for that entry |

Camera snapshots and streams are on-demand and do not wait for the next poll.

## Coordinator failure handling

When a poll fails:

- The coordinator raises `UpdateFailed` (logged once per failure)
- Entities mark themselves unavailable when device status is offline
- Rate limits (`OP1013`) back off with exponential delay and surface in the **API Status** diagnostic sensor
- Repeated "device not found" errors may open a **stale device** repair issue

## Diagnostic sensor

**API Status** (`sensor.*_api_status`, disabled by default) reports:

- `ok` — last poll succeeded
- `rate_limited` — Imou API quota hit
- `error` — other API error on last poll
- `unknown` — no successful poll yet

Attributes include rate-limit timing, scan interval, and stale-device counters.

## Related docs

- [Configuration](CONFIGURATION.md) — option reference
- [Performance Troubleshooting](PERFORMANCE_TROUBLESHOOTING.md) — rate limits and tuning
- [Stale Device Detection](STALE_DEVICE_DETECTION.md) — removed-from-cloud devices
