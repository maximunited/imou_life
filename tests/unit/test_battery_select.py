"""Unit tests for battery optimization select entities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.imou_life.battery_select import ImouBatterySelect
from custom_components.imou_life.const import (
    MOTION_SENSITIVITY_LEVELS,
    POWER_MODES,
    RECORDING_QUALITY_OPTIONS,
    SLEEP_SCHEDULE_OPTIONS,
)


class TestImouBatterySelect:
    """Test battery optimization select entities."""

    @pytest.fixture
    def mock_hass(self):
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        hass.config_entries = MagicMock()
        return hass

    @pytest.fixture
    def mock_coordinator(self, mock_hass):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Device"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_device_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = mock_hass
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
            "sleep_schedule": "never",
        }
        return config_entry

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "powerMode"
        sensor.get_description.return_value = "Power Mode"
        sensor.get_state.return_value = "balanced"
        sensor.get_attributes.return_value = {}
        sensor.async_update = AsyncMock()
        sensor.set_enabled = MagicMock()

        # Make sure async_update is properly mocked as an async method
        sensor.async_update.return_value = None
        return sensor

    @pytest.fixture
    def power_mode_select(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Create a power mode select entity."""
        return ImouBatterySelect(
            mock_coordinator,
            mock_config_entry,
            "powerMode",
            "Power Mode",
            POWER_MODES,
            "mdi:battery-settings",
            "power_mode",
        )

    @pytest.fixture
    def motion_sensitivity_select(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Create a motion sensitivity select entity."""
        return ImouBatterySelect(
            mock_coordinator,
            mock_config_entry,
            "motionSensitivityLevel",
            "Motion Sensitivity",
            MOTION_SENSITIVITY_LEVELS,
            "mdi:tune-vertical",
            "motion_sensitivity",
        )

    @pytest.fixture
    def recording_quality_select(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Create a recording quality select entity."""
        return ImouBatterySelect(
            mock_coordinator,
            mock_config_entry,
            "recordingQuality",
            "Recording Quality",
            RECORDING_QUALITY_OPTIONS,
            "mdi:video-quality",
            "recording_quality",
        )

    @pytest.fixture
    def sleep_schedule_select(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Create a sleep schedule select entity."""
        return ImouBatterySelect(
            mock_coordinator,
            mock_config_entry,
            "sleepSchedule",
            "Sleep Schedule",
            SLEEP_SCHEDULE_OPTIONS,
            "mdi:clock-outline",
            "sleep_schedule",
        )

    def test_select_initialization(self, power_mode_select):
        """Test select entity initialization."""
        assert power_mode_select.select_type == "powerMode"
        assert power_mode_select._description == "Power Mode"
        assert power_mode_select._options == POWER_MODES
        assert power_mode_select._icon == "mdi:battery-settings"
        assert power_mode_select._attribute_name == "power_mode"

    def test_select_name(self, power_mode_select):
        """Test select entity name."""
        assert power_mode_select.name == "Test Device Power Mode"

    def test_select_unique_id(self, power_mode_select, mock_config_entry):
        """Test select entity unique ID."""
        expected_id = f"{mock_config_entry.entry_id}_powerMode"
        assert power_mode_select.unique_id == expected_id

    def test_select_icon(self, power_mode_select):
        """Test select entity icon."""
        assert power_mode_select.icon == "mdi:battery-settings"

    def test_select_options(self, power_mode_select):
        """Test select entity options."""
        assert power_mode_select.options == POWER_MODES

    def test_select_current_option_from_coordinator(
        self, power_mode_select, mock_coordinator
    ):
        """Test getting current option from coordinator."""
        mock_coordinator.get_battery_optimization_status.return_value = {
            "power_mode": "power_saving"
        }

        assert power_mode_select.current_option == "power_saving"

    def test_select_current_option_from_config(
        self, power_mode_select, mock_config_entry
    ):
        """Test getting current option from config when coordinator doesn't have method."""
        # Remove the method from coordinator
        coordinator = power_mode_select.coordinator
        delattr(coordinator, "get_battery_optimization_status")

        assert power_mode_select.current_option == "balanced"

    def test_select_current_option_fallback(self, power_mode_select):
        """Test getting current option when neither coordinator nor config has it."""
        # Remove the method from coordinator
        coordinator = power_mode_select.coordinator
        delattr(coordinator, "get_battery_optimization_status")
        # Clear config options
        power_mode_select.config_entry.options = {}

        assert power_mode_select.current_option is None

    @pytest.mark.asyncio
    async def test_select_option_power_mode(self, power_mode_select, mock_coordinator):
        """Test selecting power mode option."""
        mock_coordinator.set_power_mode = AsyncMock()

        await power_mode_select.async_select_option("power_saving")

        mock_coordinator.set_power_mode.assert_called_once_with("power_saving")

    @pytest.mark.asyncio
    async def test_select_option_motion_sensitivity(
        self, motion_sensitivity_select, mock_coordinator
    ):
        """Test selecting motion sensitivity option."""
        mock_coordinator.set_motion_sensitivity = AsyncMock()

        await motion_sensitivity_select.async_select_option("low")

        mock_coordinator.set_motion_sensitivity.assert_called_once_with("low")

    @pytest.mark.asyncio
    async def test_select_option_recording_quality(
        self, recording_quality_select, mock_coordinator
    ):
        """Test selecting recording quality option."""
        mock_coordinator.set_recording_quality = AsyncMock()

        await recording_quality_select.async_select_option("low")

        mock_coordinator.set_recording_quality.assert_called_once_with("low")

    @pytest.mark.asyncio
    async def test_select_option_sleep_schedule(
        self, sleep_schedule_select, mock_coordinator
    ):
        """Test selecting sleep schedule option."""
        mock_coordinator.set_sleep_schedule = AsyncMock()

        await sleep_schedule_select.async_select_option("night_only")

        mock_coordinator.set_sleep_schedule.assert_called_once_with("night_only")

    @pytest.mark.asyncio
    async def test_select_option_invalid(self, power_mode_select):
        """Test selecting invalid option."""
        # The method logs an error but doesn't raise an exception
        await power_mode_select.async_select_option("invalid_option")
        # Should not raise exception, just log error

    @pytest.mark.asyncio
    async def test_select_option_updates_config(
        self, power_mode_select, mock_config_entry
    ):
        """Test that selecting option updates config entry."""
        mock_coordinator = power_mode_select.coordinator
        mock_coordinator.set_power_mode = AsyncMock()

        # Mock the config entry update
        with patch.object(
            power_mode_select.coordinator.hass.config_entries,
            "async_update_entry",
        ) as mock_update:
            await power_mode_select.async_select_option("power_saving")

            # Check that config entry was updated
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_select_option_coordinator_method_not_found(self, power_mode_select):
        """Test selecting option when coordinator method is not found."""
        # Remove the set_power_mode method from coordinator
        delattr(power_mode_select.coordinator, "set_power_mode")

        # Should still work and update config
        with patch.object(
            power_mode_select.coordinator.hass.config_entries,
            "async_update_entry",
        ) as mock_update:
            await power_mode_select.async_select_option("power_saving")

            # Check that config entry was updated
            mock_update.assert_called_once()

    def test_select_available(self, power_mode_select):
        """Test select entity availability."""
        assert power_mode_select.available is True

    def test_select_available_device_offline(self, power_mode_select, mock_coordinator):
        """Test select entity availability when device is offline."""
        mock_coordinator.device.get_status.return_value = False

        assert power_mode_select.available is False

    @pytest.mark.asyncio
    async def test_select_added_to_hass(self, power_mode_select):
        """Test select entity added to hass."""
        # Patch the sensor instance's async_update method
        with patch.object(
            power_mode_select.sensor_instance, "async_update", new_callable=AsyncMock
        ):
            await power_mode_select.async_added_to_hass()
            # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_select_will_remove_from_hass(self, power_mode_select):
        """Test select entity will be removed from hass."""
        await power_mode_select.async_will_remove_from_hass()
        # Should not raise any exceptions

    def test_motion_sensitivity_select_properties(self, motion_sensitivity_select):
        """Test motion sensitivity select entity properties."""
        assert motion_sensitivity_select.name == "Test Device Motion Sensitivity"
        assert motion_sensitivity_select.icon == "mdi:tune-vertical"
        assert motion_sensitivity_select.options == MOTION_SENSITIVITY_LEVELS
        assert motion_sensitivity_select._attribute_name == "motion_sensitivity"

    def test_recording_quality_select_properties(self, recording_quality_select):
        """Test recording quality select entity properties."""
        assert recording_quality_select.name == "Test Device Recording Quality"
        assert recording_quality_select.icon == "mdi:video-quality"
        assert recording_quality_select.options == RECORDING_QUALITY_OPTIONS
        assert recording_quality_select._attribute_name == "recording_quality"

    def test_sleep_schedule_select_properties(self, sleep_schedule_select):
        """Test sleep schedule select entity properties."""
        assert sleep_schedule_select.name == "Test Device Sleep Schedule"
        assert sleep_schedule_select.icon == "mdi:clock-outline"
        assert sleep_schedule_select.options == SLEEP_SCHEDULE_OPTIONS
        assert sleep_schedule_select._attribute_name == "sleep_schedule"

    @pytest.mark.asyncio
    async def test_select_option_exception_handling(self, power_mode_select):
        """Test exception handling when selecting option."""
        # Mock coordinator method to raise exception
        power_mode_select.coordinator.set_power_mode = AsyncMock(
            side_effect=Exception("Test error")
        )

        # Should handle exception gracefully
        await power_mode_select.async_select_option("power_saving")
        # Should not raise exception, just log error

    def test_select_device_info(self, power_mode_select):
        """Test select entity device info."""
        device_info = power_mode_select.device_info

        assert device_info["identifiers"] == {
            ("imou_life", power_mode_select.config_entry.entry_id)
        }
        assert device_info["name"] == "Test Device"
        assert device_info["model"] == "Test Model"
        assert device_info["manufacturer"] == "Imou"
        assert device_info["sw_version"] == "1.0.0"
        assert device_info["hw_version"] == "test_device_123"
