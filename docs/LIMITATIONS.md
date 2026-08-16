# Known Limitations

Practical constraints when using the Imou Life integration.

## Imou API and account

| Limitation | Impact | Workaround |
| --- | --- | --- |
| **5 devices per developer app** | Imou caps devices linked to one App ID | Use multiple developer apps or prioritize cameras |
| **Rate limits (`OP1013`)** | Bursts of API calls trigger temporary blocks | Increase scan interval; avoid rapid button/PTZ spam |
| **Cloud-only API** | No LAN-only control | Requires internet connectivity to Imou cloud |
| **Unofficial integration** | Not supported by Imou/Dahua | Community support via GitHub issues |

## Push notifications

- Require a **callback URL** reachable from the internet (HTTPS recommended).
- Reverse proxies must forward the callback path correctly; malformed requests are a common setup failure.
- Enable the **Push notifications** switch only after configuring the callback URL in options.

## Device and entity model

- **One Home Assistant device per config entry** — each Imou camera is added separately.
- **Device identifier** is the config entry ID, not the Imou hardware serial.
- Removing a device from the Imou app may trigger a **stale device** repair issue after repeated API errors.

## Battery cameras

- Battery optimization features depend on model and firmware support.
- Aggressive polling drains battery; use longer scan intervals and sleep schedules.
- Some settings are stored in config entry options and may not mirror the Imou app instantly.

## Platform / library constraints

| Area | Limitation |
| --- | --- |
| **async-dependency** | `imouapi` is synchronous; integration wraps it in async coordinators |
| **inject-websession** | `imouapi` does not accept Home Assistant's shared aiohttp session |
| **Python 3.14** | Supported only with Home Assistant dev/nightly builds in CI |

## Home Assistant version

Minimum supported version is **2025.10.0** (PTZ service registration API). See [Version Compatibility](VERSION_COMPATIBILITY.md) for the full matrix.

## What we do not support

- Local RTSP-only cameras without Imou cloud pairing
- ONVIF as a replacement for the Imou OpenAPI
- More than the entities exposed by `imouapi` for your device model

## Related docs

- [Performance Troubleshooting](PERFORMANCE_TROUBLESHOOTING.md)
- [FAQ](FAQ.md)
- [Supported Devices](SUPPORTED_DEVICES.md)
