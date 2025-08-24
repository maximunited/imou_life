"""Unit tests for battery optimization button entities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.imou_life.battery_button import ImouBatteryButton


class TestImouBatteryButton:
    """Test battery optimization button entities."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Device"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_device_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = MagicMock()
        return coordinator

    @pytest.fixture
    def mock_config_entry(self):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry_123"
        config_entry.options = {
            "power_mode": "balanced",
            "motion_sensitivity": "medium",
            "recording_quality": "standard",
            "led_indicators": True,
            "auto_sleep": False,
            "battery_threshold": 20,
        }
        return config_entry

    @pytest.fixture
    def enter_sleep_button(self, mock_coordinator, mock_config_entry):
        """Create an enter sleep mode button entity."""
        return ImouBatteryButton(
            mock_coordinator,
            mock_config_entry,
            "enterSleepMode",
            "Enter Sleep Mode",
            "mdi:power-sleep",
            "enter_sleep_mode",
        )

    @pytest.fixture
    def exit_sleep_button(self, mock_coordinator, mock_config_entry):
        """Create an exit sleep mode button entity."""
        return ImouBatteryButton(
            mock_coordinator,
            mock_config_entry,
            "exitSleepMode",
            "Exit Sleep Mode",
            "mdi:power-sleep",
            "exit_sleep_mode",
        )

    @pytest.fixture
    def optimize_battery_button(self, mock_coordinator, mock_config_entry):
        """Create an optimize battery button entity."""
        return ImouBatteryButton(
            mock_coordinator,
            mock_config_entry,
            "optimizeBattery",
            "Optimize Battery",
            "mdi:battery-settings",
            "optimize_battery",
        )

    @pytest.fixture
    def reset_power_button(self, mock_coordinator, mock_config_entry):
        """Create a reset power settings button entity."""
        return ImouBatteryButton(
            mock_coordinator,
            mock_config_entry,
            "resetPowerSettings",
            "Reset Power Settings",
            "mdi:refresh-circle",
            "reset_power_settings",
        )

    def test_button_initialization(self, enter_sleep_button):
        """Test button entity initialization."""
        assert enter_sleep_button.button_type == "enterSleepMode"
        assert enter_sleep_button._description == "Enter Sleep Mode"
        assert enter_sleep_button._icon == "mdi:power-sleep"
        assert enter_sleep_button._action_name == "enter_sleep_mode"

    def test_button_name(self, enter_sleep_button):
        """Test button entity name."""
        assert enter_sleep_button.name == "Test Device Enter Sleep Mode"

    def test_button_unique_id(self, enter_sleep_button, mock_config_entry):
        """Test button entity unique ID."""
        expected_id = f"{mock_config_entry.entry_id}_enterSleepMode"
        assert enter_sleep_button.unique_id == expected_id

    def test_button_icon(self, enter_sleep_button):
        """Test button entity icon."""
        assert enter_sleep_button.icon == "mdi:power-sleep"

    @pytest.mark.asyncio
    async def test_button_press_enter_sleep_mode(
        self, enter_sleep_button, mock_coordinator
    ):
        """Test enter sleep mode button press."""
        mock_coordinator.enter_sleep_mode = AsyncMock()

        await enter_sleep_button.async_press()

        mock_coordinator.enter_sleep_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_button_press_exit_sleep_mode(
        self, exit_sleep_button, mock_coordinator
    ):
        """Test exit sleep mode button press."""
        mock_coordinator.exit_sleep_mode = AsyncMock()

        await exit_sleep_button.async_press()

        mock_coordinator.exit_sleep_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_button_press_optimize_battery(
        self, optimize_battery_button, mock_coordinator
    ):
        """Test optimize battery button press."""
        mock_coordinator.optimize_battery = AsyncMock()

        await optimize_battery_button.async_press()

        mock_coordinator.optimize_battery.assert_called_once()

    @pytest.mark.asyncio
    async def test_button_press_reset_power_settings(
        self, reset_power_button, mock_config_entry
    ):
        """Test reset power settings button press."""
        with patch.object(
            reset_power_button.coordinator.hass.config_entries, "async_update_entry"
        ) as mock_update:
            await reset_power_button.async_press()

            # Check that config entry was updated with default values
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_button_press_enter_sleep_mode_coordinator_method_not_found(
        self, enter_sleep_button
    ):
        """Test enter sleep mode button when coordinator method is not found."""
        # Remove the enter_sleep_mode method from coordinator
        delattr(enter_sleep_button.coordinator, "enter_sleep_mode")

        # Should handle gracefully and log warning
        await enter_sleep_button.async_press()
        # Should not raise exception

    @pytest.mark.asyncio
    async def test_button_press_exit_sleep_mode_coordinator_method_not_found(
        self, exit_sleep_button
    ):
        """Test exit sleep mode button when coordinator method is not found."""
        # Remove the exit_sleep_mode method from coordinator
        delattr(exit_sleep_button.coordinator, "exit_sleep_mode")

        # Should handle gracefully and log warning
        await exit_sleep_button.async_press()
        # Should not raise exception

    @pytest.mark.asyncio
    async def test_button_press_optimize_battery_coordinator_method_not_found(
        self, optimize_battery_button
    ):
        """Test optimize battery button when coordinator method is not found."""
        # Remove the optimize_battery method from coordinator
        delattr(optimize_battery_button.coordinator, "optimize_battery")

        # Should handle gracefully and log warning
        await optimize_battery_button.async_press()
        # Should not raise exception

    @pytest.mark.asyncio
    async def test_button_press_reset_power_settings_with_coordinator_method(
        self, reset_power_button, mock_coordinator
    ):
        """Test reset power settings button with coordinator reset method."""
        mock_coordinator.reset_power_settings = AsyncMock()

        with patch.object(
            reset_power_button.coordinator.hass.config_entries, "async_update_entry"
        ):
            await reset_power_button.async_press()

            mock_coordinator.reset_power_settings.assert_called_once()

    @pytest.mark.asyncio
    async def test_button_press_exception_handling(
        self, enter_sleep_button, mock_coordinator
    ):
        """Test button press exception handling."""
        mock_coordinator.enter_sleep_mode = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Should handle exception gracefully
        await enter_sleep_button.async_press()
        # Should not raise exception, just log error

    def test_button_available(self, enter_sleep_button):
        """Test button entity availability."""
        assert enter_sleep_button.available is True

    def test_button_available_device_offline(
        self, enter_sleep_button, mock_coordinator
    ):
        """Test button entity availability when device is offline."""
        mock_coordinator.device.get_status.return_value = False

        assert enter_sleep_button.available is False

    @pytest.mark.asyncio
    async def test_button_added_to_hass(self, enter_sleep_button):
        """Test button entity added to hass."""
        await enter_sleep_button.async_added_to_hass()
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_button_will_remove_from_hass(self, enter_sleep_button):
        """Test button entity will be removed from hass."""
        await enter_sleep_button.async_will_remove_from_hass()
        # Should not raise any exceptions

    def test_button_device_info(self, enter_sleep_button):
        """Test button entity device info."""
        device_info = enter_sleep_button.device_info

        assert device_info["identifiers"] == {
            ("imou_life", enter_sleep_button.config_entry.entry_id)
        }
        assert device_info["name"] == "Test Device"
        assert device_info["model"] == "Test Model"
        assert device_info["manufacturer"] == "Imou"
        assert device_info["sw_version"] == "1.0.0"
        assert device_info["hw_version"] == "test_device_123"

    def test_all_button_types(self, mock_coordinator, mock_config_entry):
        """Test all button types have correct properties."""
        button_configs = [
            (
                "enterSleepMode",
                "Enter Sleep Mode",
                "mdi:power-sleep",
                "enter_sleep_mode",
            ),
            ("exitSleepMode", "Exit Sleep Mode", "mdi:power-sleep", "exit_sleep_mode"),
            (
                "optimizeBattery",
                "Optimize Battery",
                "mdi:battery-settings",
                "optimize_battery",
            ),
            (
                "resetPowerSettings",
                "Reset Power Settings",
                "mdi:refresh-circle",
                "reset_power_settings",
            ),
        ]

        for button_type, description, icon, action_name in button_configs:
            button = ImouBatteryButton(
                mock_coordinator,
                mock_config_entry,
                button_type,
                description,
                icon,
                action_name,
            )

            assert button.button_type == button_type
            assert button._description == description
            assert button._icon == icon
            assert button._action_name == action_name
            assert button.name == f"Test Device {description}"

    @pytest.mark.asyncio
    async def test_button_press_logging(self, enter_sleep_button, mock_coordinator):
        """Test that button press logs appropriate messages."""
        mock_coordinator.enter_sleep_mode = AsyncMock()

        with patch("custom_components.imou_life.battery_button._LOGGER") as mock_logger:
            await enter_sleep_button.async_press()

            # Check that info message was logged
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "Executed" in log_message
            assert "%s action for device %s" in log_message

    @pytest.mark.asyncio
    async def test_button_press_error_logging(
        self, enter_sleep_button, mock_coordinator
    ):
        """Test that button press errors are logged."""
        mock_coordinator.enter_sleep_mode = AsyncMock(
            side_effect=Exception("Test error")
        )

        with patch("custom_components.imou_life.battery_button._LOGGER") as mock_logger:
            await enter_sleep_button.async_press()

            # Check that error message was logged
            mock_logger.error.assert_called_once()
            log_message = mock_logger.error.call_args[0][0]
            assert "Error executing" in log_message
            assert "%s action:" in log_message
