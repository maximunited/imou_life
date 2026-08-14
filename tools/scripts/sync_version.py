"""Sync version from pyproject.toml to manifest.json.

PSR bumps manifest.json via version_variables; this script is used by
build_command (belt-and-suspenders) and CI to verify the files stay aligned.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

PYPROJECT = Path("pyproject.toml")
MANIFEST = Path("custom_components/imou_life/manifest.json")


def read_pyproject_version(pyproject_path: Path | str = PYPROJECT) -> str:
    """Return the project version from pyproject.toml."""
    with open(pyproject_path, "rb") as file:
        version = tomllib.load(file)["project"]["version"]
    if not isinstance(version, str):
        raise TypeError("pyproject.toml project.version must be a string")
    return version


def read_manifest_version(manifest_path: Path | str = MANIFEST) -> str:
    """Return the integration version from manifest.json."""
    with open(manifest_path, encoding="utf-8") as file:
        version = json.load(file)["version"]
    if not isinstance(version, str):
        raise TypeError("manifest.json version must be a string")
    return version


def sync_manifest_version(
    pyproject_path: Path | str = PYPROJECT,
    manifest_path: Path | str = MANIFEST,
) -> str:
    """Copy pyproject version into manifest.json and return that version."""
    version = read_pyproject_version(pyproject_path)
    manifest_path = Path(manifest_path)

    with open(manifest_path, encoding="utf-8") as file:
        manifest: dict[str, object] = json.load(file)

    manifest["version"] = version

    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)
        file.write("\n")

    return version


def main() -> None:
    version = sync_manifest_version()
    print(f"Synced version {version} to {MANIFEST}")


if __name__ == "__main__":
    main()
