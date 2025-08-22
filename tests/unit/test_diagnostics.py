"""Tests for the Imou Life Diagnostics."""
import pytest
from unittest.mock import MagicMock
from unittest.mock import patch

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
                "device_type": "camera"
            },
            "last_update": "2023-01-01T00:00:00Z"
        }
        return coordinator

    @pytest.mark.asyncio
    async def test_async_get_config_entry_diagnostics(self, mock_hass, mock_config_entry, mock_coordinator):
        """Test config entry diagnostics."""
        # Mock the coordinator retrieval
        with patch('custom_components.imou_life.diagnostics.get_coordinator', return_value=mock_coordinator):
            result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
            
            assert isinstance(result, dict)
            assert "config_entry" in result
            assert "coordinator_data" in result
            assert result["config_entry"]["entry_id"] == mock_config_entry.entry_id
            assert result["coordinator_data"]["device_info"]["device_id"] == "test_device_123"

    @pytest.mark.asyncio
    async def test_diagnostics_no_coordinator(self, mock_hass, mock_config_entry):
        """Test diagnostics when no coordinator exists."""
        with patch('custom_components.imou_life.diagnostics.get_coordinator', return_value=None):
            result = await async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
            
            assert isinstance(result, dict)
            assert "config_entry" in result
            assert "coordinator_data" in result
            assert result["coordinator_data"] == {}

    def test_diagnostics_structure(self, mock_hass, mock_config_entry, mock_coordinator):
        """Test diagnostics data structure."""
        with patch('custom_components.imou_life.diagnostics.get_coordinator', return_value=mock_coordinator):
            result = async_get_config_entry_diagnostics(mock_hass, mock_config_entry)
            
            # Check required keys exist
            required_keys = ["config_entry", "coordinator_data"]
            for key in required_keys:
                assert key in result
