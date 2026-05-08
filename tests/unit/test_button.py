"""Tests for the Imou Life Button platform."""

from unittest.mock import AsyncMock, MagicMock

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
        # Use AsyncMock for async methods
        sensor.async_press = AsyncMock()
        return sensor

    @pytest.fixture
    def button(self, mock_coordinator, mock_sensor_instance):
        """Create a button instance."""
        return ImouButton(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "button.{}"
        )

    def test_button_name(self, button):
        """Test button name property."""
        # With has_entity_name=True, name is just the sensor description
        assert button.name == "Restart"

    def test_button_unique_id(self, button):
        """Test button unique ID."""
        assert button.unique_id == f"{MOCK_CONFIG_ENTRY.entry_id}_restartDevice"

    def test_button_should_poll(self, button):
        """Test button should_poll property."""
        assert button.should_poll is False

    def test_button_icon(self, button):
        """Test button has translation key for dynamic icons."""
        assert button._attr_translation_key == "restart_device"

    def test_button_device_class(self, button):
        """Test button device class."""
        assert button.device_class == "restart"

    def test_button_available(self, button):
        """Test button available property."""
        assert button.available is True

    @pytest.mark.asyncio
    async def test_button_press(self, button):
        """Test button press functionality."""
        await button.async_press()
        button.sensor_instance.async_press.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_button_press_refresh_data(
        self, mock_coordinator, mock_sensor_instance
    ):
        """Test pressing refreshData button triggers coordinator refresh."""
        # Create refreshData button
        mock_sensor_instance.get_name.return_value = "refreshData"
        mock_sensor_instance.get_description.return_value = "Refresh Data"
        mock_coordinator.async_request_refresh = AsyncMock()

        button = ImouButton(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "button.{}"
        )

        await button.async_press()

        # Verify async_press was awaited
        mock_sensor_instance.async_press.assert_awaited_once()
        # Verify coordinator refresh was requested (covers line 48)
        mock_coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_button_press_refresh_alarm(
        self, mock_coordinator, mock_sensor_instance
    ):
        """Test pressing refreshAlarm button updates motion sensor."""
        # Create refreshAlarm button
        mock_sensor_instance.get_name.return_value = "refreshAlarm"
        mock_sensor_instance.get_description.return_value = "Refresh Alarm"

        # Mock the motionAlarm sensor
        motion_sensor = MagicMock()
        motion_sensor.async_update = AsyncMock()
        mock_coordinator.device.get_sensor_by_name.return_value = motion_sensor

        # Mock entity with motionAlarm sensor
        mock_entity = MagicMock()
        mock_entity.sensor_instance.get_name.return_value = "motionAlarm"
        mock_entity.async_update_ha_state = AsyncMock()
        mock_coordinator.entities = [mock_entity]

        button = ImouButton(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "button.{}"
        )

        await button.async_press()

        # Verify async_press was awaited
        mock_sensor_instance.async_press.assert_awaited_once()
        # Verify motion sensor was updated (covers lines 52-54)
        mock_coordinator.device.get_sensor_by_name.assert_called_once_with(
            "motionAlarm"
        )
        motion_sensor.async_update.assert_awaited_once()
        # Verify HA state was updated (covers lines 56-58)
        mock_entity.async_update_ha_state.assert_awaited_once()

    def test_entity_registry_enabled_default_disabled_buttons(self):
        """Test that manual/advanced buttons are disabled by default."""
        mock_coordinator = MagicMock()

        # Test disabled buttons
        for button_name in ["refreshData", "refreshAlarm", "restartDevice"]:
            mock_sensor = MagicMock()
            mock_sensor.get_name.return_value = button_name
            mock_sensor.get_description.return_value = button_name

            button = ImouButton(
                mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor, "button.{}"
            )

            # These buttons should be disabled by default (covers lines 34-35)
            assert button.entity_registry_enabled_default is False

    def test_entity_registry_enabled_default_enabled_buttons(self):
        """Test that other buttons are enabled by default."""
        mock_coordinator = MagicMock()
        mock_sensor = MagicMock()
        mock_sensor.get_name.return_value = "someOtherButton"
        mock_sensor.get_description.return_value = "Some Other Button"

        button = ImouButton(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor, "button.{}"
        )

        # Other buttons should be enabled by default
        assert button.entity_registry_enabled_default is True

    def test_button_device_info(self, button):
        """Test button device info."""
        device_info = button.device_info
        assert device_info["identifiers"] == {("imou_life", MOCK_CONFIG_ENTRY.entry_id)}
        assert device_info["name"] == "Test Button"
        assert device_info["manufacturer"] == "Imou"
