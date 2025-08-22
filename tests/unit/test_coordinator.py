"""Tests for the Imou Life Coordinator."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.imou_life.coordinator import ImouDataUpdateCoordinator


class TestImouDataUpdateCoordinator:
    """Test the Imou Life Data Update Coordinator."""

    @pytest.fixture
    def mock_device(self):
        """Create a mock device."""
        device = MagicMock()
        device.async_get_data = AsyncMock(return_value={"test": "data"})
        return device

    @pytest.fixture
    def coordinator(self, mock_device):
        """Create a coordinator instance."""
        return ImouDataUpdateCoordinator(
            hass=MagicMock(),
            device=mock_device,
            scan_interval=30,
        )

    def test_coordinator_initialization(self, coordinator):
        """Test coordinator initialization."""
        assert coordinator.device is not None
        assert coordinator.scan_inteval == 30
        assert coordinator.platforms == []
        assert coordinator.entities == []

    @pytest.mark.asyncio
    async def test_coordinator_async_update_data_success(self, coordinator):
        """Test successful data update."""
        result = await coordinator._async_update_data()
        assert result == {"test": "data"}
        coordinator.device.async_get_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_coordinator_async_update_data_failure(self, coordinator):
        """Test data update failure."""
        from imouapi.exceptions import ImouException

        coordinator.device.async_get_data.side_effect = ImouException("Test error")

        with pytest.raises(Exception):  # UpdateFailed exception
            await coordinator._async_update_data()

        coordinator.device.async_get_data.assert_called_once()

    def test_coordinator_platforms(self, coordinator):
        """Test coordinator platforms property."""
        assert coordinator.platforms == []
        coordinator.platforms.append("test_platform")
        assert "test_platform" in coordinator.platforms

    def test_coordinator_entities(self, coordinator):
        """Test coordinator entities property."""
        assert coordinator.entities == []
        test_entity = MagicMock()
        coordinator.entities.append(test_entity)
        assert test_entity in coordinator.entities

    def test_coordinator_name(self, coordinator):
        """Test coordinator name."""
        assert coordinator.name == "imou_life"

    def test_coordinator_update_interval(self, coordinator):
        """Test coordinator update interval."""
        from datetime import timedelta

        assert coordinator.update_interval == timedelta(seconds=30)
