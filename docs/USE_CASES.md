# Use Cases

Common ways to deploy Imou Life in Home Assistant.

## Single front-door camera

**Goal:** Motion alerts and live view on a dashboard.

1. Add integration via HACS; complete login + discovery.
2. Enable **Motion alarm** binary sensor (on by default).
3. Add a **Picture glance** or **Live view** card for the camera entity.
4. Create a notification automation — see [Examples](EXAMPLES.md).

**Tips:** Set scan interval to 10–15 minutes unless you need faster motion sync.

## Multi-camera home

**Goal:** Several Imou cameras on one App ID (up to 5).

1. Complete setup for the first camera with discovery enabled.
2. Add additional entries via **Settings → Devices & Services → Imou Life → Add device**.
3. Use areas and labels in HA to group entities.
4. Share one callback URL across entries if using push notifications.

See [Multi-Device Guide](MULTI_DEVICE_GUIDE.md).

## Battery camera (porch / garden)

**Goal:** Maximize battery life while keeping motion useful.

1. Confirm model in [Supported Devices](SUPPORTED_DEVICES.md).
2. Enable **Battery optimization** in integration options.
3. Use 30+ minute scan interval; configure sleep schedule if available.
4. Automate on **motion** only; avoid frequent snapshot scripts.

## Security monitoring with recording

**Goal:** Motion triggers lights and optional snapshot archive.

1. Motion binary sensor → light automation (night-only condition).
2. Optional: `camera.snapshot` to `/config/www/` on motion.
3. Use **Refresh alarm** button sparingly; coordinator poll is usually enough.

## Away mode

**Goal:** Reduce noise when nobody is home.

1. Toggle **Push notifications** off when `zone.home` is empty.
2. Optionally increase scan interval in **Settings → Devices & Services → Imou Life → Configure** (requires integration reload to apply).

## Troubleshooting-first setup

**Goal:** Reliable operation before automations.

1. Confirm **API status** sensor shows `ok` after setup.
2. Check [Performance Troubleshooting](PERFORMANCE_TROUBLESHOOTING.md) if rate-limited.
3. Resolve **stale device** repairs if the camera was removed from the Imou app.

## Related docs

- [Quick Start](QUICK_START.md)
- [Configuration](CONFIGURATION.md)
- [Limitations](LIMITATIONS.md)
