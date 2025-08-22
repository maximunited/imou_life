"""Tests for the Imou Life Coordinator."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from custom_components.imou_life.coordinator import ImouLifeDataUpdateCoordinator
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouLifeDataUpdateCoordinator:
    """Test the Imou Life Data Update Coordinator."""

    @pytest.fixture
    def mock_hass(self):
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        hass.async_add_executor_job = AsyncMock()
        return hass

    @pytest.fixture
    def mock_api(self):
        """Create a mock API client."""
        api = MagicMock()
        api.get_devices = AsyncMock()
        api.get_device_status = AsyncMock()
        return api

    @pytest.fixture
    def coordinator(self, mock_hass, mock_api):
        """Create a coordinator instance."""
        return ImouLifeDataUpdateCoordinator(mock_hass, MOCK_CONFIG_ENTRY, mock_api)

    def test_coordinator_initialization(self, coordinator):
        """Test coordinator initialization."""
        assert coordinator.config_entry == MOCK_CONFIG_ENTRY
        assert coordinator.api is not None
        assert coordinator.data == {}

    @pytest.mark.asyncio
    async def test_coordinator_async_get_data_success(self, coordinator, mock_api):
        """Test successful data retrieval."""
        mock_devices = [
            {"device_id": "dev1", "name": "Camera 1", "type": "camera"},
            {"device_id": "dev2", "name": "Sensor 1", "type": "sensor"}
        ]
        mock_api.get_devices.return_value = mock_devices
        
        result = await coordinator._async_get_data()
        
        assert result == mock_devices
        mock_api.get_devices.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_async_get_data_failure(self, coordinator, mock_api):
        """Test data retrieval failure."""
        mock_api.get_devices.side_effect = Exception("API Error")
        
        result = await coordinator._async_get_data()
        
        assert result == {}
        mock_api.get_devices.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_async_update_data_success(self, coordinator, mock_api):
        """Test successful data update."""
        mock_devices = [
            {"device_id": "dev1", "name": "Camera 1", "type": "camera"}
        ]
        mock_api.get_devices.return_value = mock_devices
        
        await coordinator._async_update_data()
        
        assert coordinator.data == mock_devices

    @pytest.mark.asyncio
    async def test_coordinator_async_update_data_failure(self, coordinator, mock_api):
        """Test data update failure."""
        mock_api.get_devices.side_effect = Exception("API Error")
        
        await coordinator._async_update_data()
        
        assert coordinator.data == {}

    def test_coordinator_last_update_success(self, coordinator):
        """Test last update success property."""
        assert coordinator.last_update_success is True

    def test_coordinator_data(self, coordinator):
        """Test coordinator data property."""
        assert coordinator.data == {}

    @pytest.mark.asyncio
    async def test_coordinator_refresh(self, coordinator):
        """Test coordinator refresh method."""
        with patch.object(coordinator, '_async_update_data') as mock_update:
            await coordinator.async_refresh()
            mock_update.assert_called_once()

    def test_coordinator_config_entry_id(self, coordinator):
        """Test coordinator config entry ID."""
        assert coordinator.config_entry_id == MOCK_CONFIG_ENTRY.entry_id

    def test_coordinator_name(self, coordinator):
        """Test coordinator name."""
        assert coordinator.name == "Imou Life"

    @pytest.mark.asyncio
    async def test_coordinator_startup(self, coordinator):
        """Test coordinator startup."""
        with patch.object(coordinator, '_async_update_data') as mock_update:
            await coordinator.async_start()
            mock_update.assert_called_once()
