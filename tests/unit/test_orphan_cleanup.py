"""Test orphan device cleanup functionality."""

from unittest.mock import MagicMock, patch

from homeassistant.helpers.device_registry import DeviceEntry

from custom_components.imou_life import _cleanup_orphan_devices
from custom_components.imou_life.const import DOMAIN
from tests.fixtures.mocks import MockConfigEntry


def _make_device_entry(device_id, identifiers):
    """Create a DeviceEntry with given identifiers."""
    return DeviceEntry(id=device_id, identifiers=identifiers)


def _make_registry(device_entries):
    """Create a mock device registry with a devices collection."""
    registry = MagicMock()
    devices = MagicMock()
    devices.values.return_value = device_entries
    registry.devices = devices
    return registry


def _make_hass(active_entries):
    """Create a mock hass with config entries and device registry."""
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = active_entries
    return hass


class TestCleanupOrphanDevices:
    """Tests for _cleanup_orphan_devices."""

    def test_removes_orphan_device(self):
        """Orphan device (entry_id not in active entries) is removed."""
        orphan = _make_device_entry("dev1", {(DOMAIN, "deleted_entry_id")})
        registry = _make_registry([orphan])

        active_entry = MockConfigEntry(
            domain=DOMAIN, data={}, entry_id="active_entry_id"
        )
        hass = _make_hass([active_entry])

        with patch("custom_components.imou_life.dr.async_get", return_value=registry):
            _cleanup_orphan_devices(hass, active_entry)

        registry.async_remove_device.assert_called_once_with("dev1")

    def test_keeps_active_device(self):
        """Device whose entry_id matches a live config entry is kept."""
        active_device = _make_device_entry("dev1", {(DOMAIN, "active_entry_id")})
        registry = _make_registry([active_device])

        active_entry = MockConfigEntry(
            domain=DOMAIN, data={}, entry_id="active_entry_id"
        )
        hass = _make_hass([active_entry])

        with patch("custom_components.imou_life.dr.async_get", return_value=registry):
            _cleanup_orphan_devices(hass, active_entry)

        registry.async_remove_device.assert_not_called()

    def test_ignores_non_domain_devices(self):
        """Devices from other integrations are never touched."""
        other_device = _make_device_entry("dev1", {("other_domain", "some_id")})
        registry = _make_registry([other_device])

        active_entry = MockConfigEntry(
            domain=DOMAIN, data={}, entry_id="active_entry_id"
        )
        hass = _make_hass([active_entry])

        with patch("custom_components.imou_life.dr.async_get", return_value=registry):
            _cleanup_orphan_devices(hass, active_entry)

        registry.async_remove_device.assert_not_called()

    def test_mixed_devices_only_orphan_removed(self):
        """Only orphan is removed when mixed with active and foreign devices."""
        active_device = _make_device_entry("dev1", {(DOMAIN, "active_entry_id")})
        orphan = _make_device_entry("dev2", {(DOMAIN, "deleted_entry_id")})
        foreign = _make_device_entry("dev3", {("other", "x")})
        registry = _make_registry([active_device, orphan, foreign])

        active_entry = MockConfigEntry(
            domain=DOMAIN, data={}, entry_id="active_entry_id"
        )
        hass = _make_hass([active_entry])

        with patch("custom_components.imou_life.dr.async_get", return_value=registry):
            _cleanup_orphan_devices(hass, active_entry)

        registry.async_remove_device.assert_called_once_with("dev2")

    def test_registry_not_ready_does_not_raise(self):
        """AttributeError from registry is caught gracefully."""
        active_entry = MockConfigEntry(
            domain=DOMAIN, data={}, entry_id="active_entry_id"
        )
        hass = _make_hass([active_entry])

        with patch(
            "custom_components.imou_life.dr.async_get",
            side_effect=AttributeError("not ready"),
        ):
            _cleanup_orphan_devices(hass, active_entry)

    def test_key_error_during_removal_does_not_raise(self):
        """KeyError from async_remove_device is caught gracefully."""
        orphan = _make_device_entry("dev1", {(DOMAIN, "deleted_entry_id")})
        registry = _make_registry([orphan])
        registry.async_remove_device.side_effect = KeyError("dev1")

        active_entry = MockConfigEntry(
            domain=DOMAIN, data={}, entry_id="active_entry_id"
        )
        hass = _make_hass([active_entry])

        with patch("custom_components.imou_life.dr.async_get", return_value=registry):
            _cleanup_orphan_devices(hass, active_entry)
