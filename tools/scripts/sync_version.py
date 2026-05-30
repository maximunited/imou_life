"""Sync version from pyproject.toml to manifest.json.

Called by python-semantic-release via build_command after version bump.
"""

import json
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

PYPROJECT = "pyproject.toml"
MANIFEST = "custom_components/imou_life/manifest.json"


def main() -> None:
    with open(PYPROJECT, "rb") as f:
        version: str = tomllib.load(f)["project"]["version"]

    with open(MANIFEST) as f:
        manifest: dict[str, object] = json.load(f)

    manifest["version"] = version

    with open(MANIFEST, "w") as f:
        json.dump(manifest, f, indent=4)
        f.write("\n")

    print(f"Synced version {version} to {MANIFEST}")


if __name__ == "__main__":
    main()
