# Supported Devices

The integration works with Imou cameras and doorbells registered to your Imou account via the [Imou Open Platform](https://open.imoulife.com).

## Compatibility model

Support is **API-driven**, not a fixed hardware list:

1. Device is visible in the Imou Life mobile app
2. Device is registered to your developer App ID
3. `imouapi` exposes sensors/controls for that model

If setup completes and entities appear, the device is supported at the integration level. Missing features usually mean the Imou API does not expose that capability for the model.

## Tested families

Community reports and development focus on these lines (not exhaustive):

| Family | Examples | Notes |
| --- | --- | --- |
| Bullet / turret (mains) | Ranger, Cruiser series | Full entity set typical |
| Battery cell | IPC-A26*, IPC-B46*, IPC-A28* | Battery optimization + sleep |
| Battery AA | IPC-A22* | Replaceable cells; shorter life |
| Doorbell | Various Imou doorbells | Siren + motion common |

Model strings appear in **Device info** (manufacturer Imou, model field) and diagnostics.

## Battery model reference

Battery metadata for [Battery Notes](https://github.com/andrew-codechimp/HA-Battery-Notes) is mapped in code for:

- IPC-A26HP, IPC-A26Z
- IPC-B46L, IPC-B46LP, IPC-B46LN
- IPC-A28HWP
- IPC-A22E, IPC-A22EP

Other models still show a battery **percentage** sensor when the API provides it.

## Multi-device accounts

- Discovery during setup lists devices on your App ID.
- Ongoing discovery can suggest new devices (first config entry only).
- Imou's **5-device developer limit** still applies.

## Unsupported or partial

- Devices removed from Imou cloud but still in HA → stale device repair flow
- OEM rebrands may work if they use the same Imou OpenAPI backend
- NVR-only channels without individual device IDs are not supported

## Reporting compatibility

When opening an issue, include:

- Model from HA device page
- Firmware version (device diagnostics)
- Which entities are missing vs the Imou app

## Related docs

- [Entities](ENTITIES.md) — what each platform provides
- [Limitations](LIMITATIONS.md)
- [Installation](INSTALLATION.md)
