"""Tests for release and compatibility version drift guards."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
MANIFEST = REPO_ROOT / "custom_components/imou_life/manifest.json"
HACS_JSON = REPO_ROOT / "hacs.json"
HA_COMPAT_WORKFLOW = REPO_ROOT / ".github/workflows/ha-compatibility.yml"
VERSION_COMPAT_DOC = REPO_ROOT / "docs/VERSION_COMPATIBILITY.md"
PSR_MANIFEST_VARIABLE = "custom_components/imou_life/manifest.json:version"


def _load_sync_version() -> ModuleType:
    script_path = REPO_ROOT / "tools" / "scripts" / "sync_version.py"
    spec = importlib.util.spec_from_file_location("sync_version", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load sync_version from {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module", name="sync_version")
def fixture_sync_version() -> ModuleType:
    return _load_sync_version()


class TestReleaseVersionDrift:
    """Guard against pyproject.toml and manifest.json drifting apart."""

    def test_manifest_matches_pyproject(self, sync_version: ModuleType) -> None:
        assert sync_version.read_manifest_version(
            MANIFEST
        ) == sync_version.read_pyproject_version(PYPROJECT)

    def test_sync_version_is_idempotent(self, sync_version: ModuleType) -> None:
        before = MANIFEST.read_text(encoding="utf-8")
        sync_version.sync_manifest_version(PYPROJECT, MANIFEST)
        after = MANIFEST.read_text(encoding="utf-8")
        assert before == after

    def test_sync_version_updates_drifted_manifest(
        self, sync_version: ModuleType, tmp_path: Path
    ) -> None:
        pyproject = tmp_path / "pyproject.toml"
        manifest = tmp_path / "manifest.json"
        pyproject.write_text('[project]\nversion = "9.9.9"\n', encoding="utf-8")
        manifest.write_text(json.dumps({"version": "1.0.0"}), encoding="utf-8")

        version = sync_version.sync_manifest_version(pyproject, manifest)

        assert version == "9.9.9"
        assert json.loads(manifest.read_text(encoding="utf-8"))["version"] == "9.9.9"

    def test_psr_tracks_both_version_files(self) -> None:
        content = PYPROJECT.read_text(encoding="utf-8")
        assert 'version_toml = ["pyproject.toml:project.version"]' in content
        assert "version_variables" in content
        assert PSR_MANIFEST_VARIABLE in content


class TestHaFloorDrift:
    """Guard against hacs.json, CI matrix, and docs disagreeing on HA floor."""

    def test_hacs_homeassistant_in_ci_matrix(self) -> None:
        hacs = json.loads(HACS_JSON.read_text(encoding="utf-8"))
        workflow = HA_COMPAT_WORKFLOW.read_text(encoding="utf-8")
        floor = hacs["homeassistant"]
        assert f'ha-version: "{floor}"' in workflow

    def test_hacs_homeassistant_documented(self) -> None:
        hacs = json.loads(HACS_JSON.read_text(encoding="utf-8"))
        doc = VERSION_COMPAT_DOC.read_text(encoding="utf-8")
        assert hacs["homeassistant"] in doc

    def test_minimum_ci_matrix_matches_hacs_floor(self) -> None:
        hacs = json.loads(HACS_JSON.read_text(encoding="utf-8"))
        workflow = HA_COMPAT_WORKFLOW.read_text(encoding="utf-8")
        match = re.search(
            r'- ha-version:\s*"([^"]+)"\s*\n\s*python-version:.*\n\s*label:\s*"Minimum"',
            workflow,
        )
        assert match is not None, "Could not find labeled Minimum HA matrix cell"
        assert match.group(1) == hacs["homeassistant"]
