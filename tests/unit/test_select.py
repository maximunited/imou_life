"""Tests for the Imou Life Select platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.imou_life.select import ImouSelect
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouSelect:
    """Test the Imou Life Select."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Select"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_select_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = MagicMock()
        return coordinator

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "nightVisionMode"
        sensor.get_description.return_value = "Night Vision"
        sensor.get_current_option.return_value = "auto"
        sensor.get_available_options.return_value = ["auto", "on", "off"]
        sensor.get_attributes.return_value = {"last_update": "2023-01-01T00:00:00Z"}
        sensor.async_select_option = AsyncMock()
        return sensor

    @pytest.fixture
    def select(self, mock_coordinator, mock_sensor_instance):
        """Create a select instance."""
        select = ImouSelect(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "select.{}"
        )
        # Set the hass attribute for testing
        select.hass = mock_coordinator.hass
        return select

    def test_select_name(self, select):
        """Test select name property."""
        assert select.name == "Test Select Night Vision"

    def test_select_unique_id(self, select):
        """Test select unique ID."""
        assert select.unique_id == f"{MOCK_CONFIG_ENTRY.entry_id}_nightVisionMode"

    def test_select_should_poll(self, select):
        """Test select should_poll property."""
        assert select.should_poll is False

    def test_select_current_option(self, select):
        """Test select current option."""
        assert select.current_option == "auto"

    def test_select_options(self, select):
        """Test select options."""
        options = select.options
        assert "auto" in options
        assert "on" in options
        assert "off" in options

    def test_select_icon(self, select):
        """Test select icon."""
        assert select.icon == "mdi:weather-night"

    def test_select_available(self, select):
        """Test select available property."""
        assert select.available is True

    @pytest.mark.asyncio
    async def test_select_select_option(self, select):
        """Test select option selection."""
        await select.async_select_option("on")
        select.sensor_instance.async_select_option.assert_called_once_with("on")

    def test_select_device_info(self, select):
        """Test select device info."""
        device_info = select.device_info
        assert device_info["identifiers"] == {("imou_life", MOCK_CONFIG_ENTRY.entry_id)}
        assert device_info["name"] == "Test Select"
        assert device_info["manufacturer"] == "Imou"

    def test_select_extra_state_attributes(self, select):
        """Test select extra state attributes."""
        attrs = select.extra_state_attributes
        assert "last_update" in attrs
        assert attrs["last_update"] == "2023-01-01T00:00:00Z"
