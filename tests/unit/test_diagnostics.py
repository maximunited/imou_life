"""Tests for the Imou Life Diagnostics."""

from unittest.mock import MagicMock

import pytest

from custom_components.imou_life.diagnostics import async_get_config_entry_diagnostics
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestDiagnostics:
    """Test the diagnostics module."""

    @pytest.fixture
    def mock_hass(self):
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        return hass

    @pytest.fixture
    def mock_config_entry(self):
        """Create a mock config entry."""
        return MOCK_CONFIG_ENTRY

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = {
            "device_info": {
                "device_id": "test_device_123",
                "device_name": "Test Device",
                "device_type": "camera",
            },
            "last_update": "2023-01-01T00:00:00Z",
        }
        return coordinator

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test config entry diagnostics."""
        # Mock the coordinator retrieval from hass.data
        mock_hass.data = {"imou_life": {mock_config_entry.entry_id: mock_coordinator}}
        mock_coordinator.device.get_diagnostics.return_value = {
            "device_id": "test_device_123",
            "device_name": "Test Device",
            "device_type": "camera",
        }

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        assert isinstance(result, dict)
        assert "entry" in result
        assert "device_info" in result
        # The entry_id gets redacted, so we can't assert on it
        assert "entry_id" in result["entry"]
        assert result["device_info"]["device_id"] == "test_device_123"

    @pytest.mark.asyncio
    async def test_diagnostics_no_coordinator(self, mock_hass, mock_config_entry):
        """Test diagnostics when no coordinator exists."""
        # Mock empty hass.data
        mock_hass.data = {"imou_life": {}}

        # This should raise a KeyError since the coordinator doesn't exist
        with pytest.raises(KeyError):
            await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

    @pytest.mark.asyncio
    async def test_diagnostics_structure(
        self, mock_hass, mock_config_entry, mock_coordinator
    ):
        """Test diagnostics data structure."""
        # Mock the coordinator retrieval from hass.data
        mock_hass.data = {"imou_life": {mock_config_entry.entry_id: mock_coordinator}}
        mock_coordinator.device.get_diagnostics.return_value = {
            "device_id": "test_device_123",
            "device_name": "Test Device",
            "device_type": "camera",
        }

        result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)

        # Check required keys exist
        required_keys = ["entry", "device_info"]
        for key in required_keys:
            assert key in result
