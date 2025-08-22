"""Tests for the Imou Life Button platform."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.imou_life.button import ImouButton
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouButton:
    """Test the Imou Life Button."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Button"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_button_123"
        coordinator.device.get_status.return_value = True
        coordinator.entities = []
        return coordinator

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "restartDevice"
        sensor.get_description.return_value = "Restart"
        sensor.get_attributes.return_value = {"last_update": "2023-01-01T00:00:00Z"}
        return sensor

    @pytest.fixture
    def button(self, mock_coordinator, mock_sensor_instance):
        """Create a button instance."""
        return ImouButton(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "button.{}"
        )

    def test_button_name(self, button):
        """Test button name property."""
        assert button.name == "Test Button Restart"

    def test_button_unique_id(self, button):
        """Test button unique ID."""
        assert button.unique_id == f"{MOCK_CONFIG_ENTRY.entry_id}_restartDevice"

    def test_button_should_poll(self, button):
        """Test button should_poll property."""
        assert button.should_poll is False

    def test_button_icon(self, button):
        """Test button icon."""
        assert button.icon == "mdi:restart"

    def test_button_device_class(self, button):
        """Test button device class."""
        assert button.device_class == "restart"

    def test_button_available(self, button):
        """Test button available property."""
        assert button.available is True

    @pytest.mark.asyncio
    async def test_button_press(self, button):
        """Test button press functionality."""
        with patch.object(button.sensor_instance, "async_press") as mock_press:
            await button.async_press()
            mock_press.assert_called_once()

    def test_button_device_info(self, button):
        """Test button device info."""
        device_info = button.device_info
        assert device_info["identifiers"] == {("imou_life", MOCK_CONFIG_ENTRY.entry_id)}
        assert device_info["name"] == "Test Button"
        assert device_info["manufacturer"] == "Imou"
