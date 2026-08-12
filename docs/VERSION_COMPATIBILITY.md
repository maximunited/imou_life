# Version Compatibility Guide

Python and Home Assistant version support for the Imou Life integration.

## Python Version Support

| Python Version | Support Status | Notes |
| -------------- | -------------- | ----- |
| 3.11 | Supported | Minimum for local tooling / older HA cores |
| 3.12 | Supported | Used by CI minimum HA pin |
| 3.13 | Supported | Recommended with current HA stable |
| 3.14 | Supported in CI | Covered by unit CI and HA `dev` matrix job |

### Requirements

- **Minimum**: Python 3.11
- **Recommended**: Python 3.13 with current Home Assistant stable
- **CI coverage**: 3.11–3.14

## Home Assistant Version Support

| Home Assistant | Role | Python in CI | Status |
| -------------- | ---- | ------------ | ------ |
| 2024.12.5 | Minimum (HACS / matrix floor) | 3.12 | Supported |
| 2025.12.5 | Late previous-year pin | 3.13 | Supported |
| 2026.8.1 | Latest stable | 3.13 | Supported |
| `dev` | Development / nightly | 3.14 | Allowed to fail in CI |

### Requirements

- **Minimum**: Home Assistant 2024.12.5 (same as `hacs.json` and the compatibility workflow)
- **Recommended**: Latest stable (currently 2026.8.x)
- **Python 3.13**: Requires Home Assistant 2024.12.0 or later
- **Python 3.14**: Prefer current stable or `dev`; covered by the allow-failure matrix job

## Compatibility Matrix

| Python | HA 2024.12+ | HA 2025.12+ | HA 2026.8+ | HA `dev` |
| ------ | ----------- | ----------- | ---------- | -------- |
| 3.11 | Supported | Supported | Supported | Best-effort |
| 3.12 | Supported (CI min pin) | Supported | Supported | Best-effort |
| 3.13 | Supported | Supported (CI late-2025 pin) | Supported (CI latest stable) | Best-effort |
| 3.14 | Best-effort | Best-effort | Best-effort | CI allow-failure |

### Why this floor?

1. **2024.12.x**: First Home Assistant line with Python 3.13 support; a practical minimum without jumping straight to 2025/2026.
2. **2025.12.x**: Keeps a late previous-year pin in CI so regressions are not only caught on bleeding-edge or ancient cores.
3. **2026.8.x**: Current stable line validated in CI.
4. **`dev` + Python 3.14**: Early warning for upcoming HA / Python breakage; failures do not block merges.

## Testing

The `.github/workflows/ha-compatibility.yml` matrix runs:

| Label | HA version | Python |
| ----- | ---------- | ------ |
| Minimum | 2024.12.5 | 3.12 |
| Late 2025 | 2025.12.5 | 3.13 |
| Latest Stable | 2026.8.1 | 3.13 |
| Development | `dev` | 3.14 (allow-failure) |

Separate unit CI also exercises Python 3.11–3.14.

## Installation recommendations

### Production

- **Python**: 3.13
- **Home Assistant**: Latest stable (2026.8.x or newer)

### Development

- **Python**: 3.13 or 3.14
- **Home Assistant**: Latest stable, plus occasional `dev` checks

### Minimum viable

- **Python**: 3.12 (3.11 still accepted by project tooling)
- **Home Assistant**: 2024.12.5 or later

## Notes

1. Python 3.10 and below are not supported.
2. Home Assistant below 2024.12.5 is outside the declared support floor (HACS and CI).
3. Python 3.13 with Home Assistant older than 2024.12.0 is not supported by Home Assistant itself.

## Troubleshooting

```bash
python --version
# Expect 3.11, 3.12, 3.13, or 3.14
```

In Home Assistant: **Settings → About** (or Configuration → Info) and confirm Core is 2024.12.5 or later.

When opening an issue, include Python version, Home Assistant Core version, and integration version.

## Additional resources

- [Home Assistant Python support](https://developers.home-assistant.io/docs/core/architecture/python-version-support/)
- [Python downloads](https://www.python.org/downloads/)
- [Home Assistant release notes](https://www.home-assistant.io/blog/categories/release-notes/)

---

**Last Updated**: August 2026
**Integration Version**: 1.8.5 (`pyproject.toml`; keep in sync with releases)
**Maintainer**: [@maximunited](https://github.com/maximunited)
