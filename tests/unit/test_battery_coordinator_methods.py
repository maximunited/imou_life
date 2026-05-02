"""Unit tests for battery coordinator method error paths and device method handling."""

from unittest.mock import AsyncMock

import pytest
from imouapi.exceptions import ImouException


class TestBatteryCoordinatorMethodErrorPaths:
    """Test battery coordinator method error handling and device support checks."""

    @pytest.mark.asyncio
    async def test_get_battery_data_fallback_to_device_data(self, coordinator):
        """Test fallback to device data when async_get_battery_status not available."""
        # Remove async_get_battery_status method
        delattr(coordinator.device, "async_get_battery_status")

        # Mock async_get_data instead
        coordinator.device.async_get_data = AsyncMock(
            return_value={
                "battery": {
                    "level": 85,
                    "voltage": 4.1,
                    "consumption": 50,
                    "charging": False,
                }
            }
        )

        battery_data = await coordinator._get_battery_data()

        assert battery_data["level"] == 85
        assert battery_data["voltage"] == 4.1
        assert battery_data["consumption"] == 50
        assert battery_data["charging"] is False

    @pytest.mark.asyncio
    async def test_get_battery_data_error_returns_defaults(self, coordinator):
        """Test battery data returns safe defaults on error."""
        coordinator.device.async_get_battery_status = AsyncMock(
            side_effect=ImouException("Battery data error")
        )

        battery_data = await coordinator._get_battery_data()

        # Should return safe defaults
        assert battery_data["level"] == 100
        assert battery_data["voltage"] is None
        assert battery_data["consumption"] is None
        assert battery_data["charging"] is False

    @pytest.mark.asyncio
    async def test_check_battery_optimization_with_none_battery_level(
        self, coordinator
    ):
        """Test battery optimization check with None battery level."""
        battery_data = {"level": None, "voltage": None, "consumption": None}

        # Should return early without raising
        await coordinator._check_battery_optimization(battery_data)

    @pytest.mark.asyncio
    async def test_deactivate_battery_optimization_already_inactive(self, coordinator):
        """Test deactivating battery optimization when already inactive."""
        coordinator._battery_optimization_active = False

        # Mock device methods
        coordinator.device.async_set_motion_sensitivity = AsyncMock()
        coordinator.device.async_set_recording_quality = AsyncMock()
        coordinator.device.async_set_led_indicators = AsyncMock()
        coordinator.device.async_set_power_mode = AsyncMock()

        await coordinator._deactivate_battery_optimization()

        # Should return early without calling device methods
        coordinator.device.async_set_motion_sensitivity.assert_not_called()
        coordinator.device.async_set_recording_quality.assert_not_called()
        coordinator.device.async_set_led_indicators.assert_not_called()
        coordinator.device.async_set_power_mode.assert_not_called()

    @pytest.mark.asyncio
    async def test_activate_battery_optimization_exception(self, coordinator):
        """Test battery optimization activation handles exceptions."""
        coordinator._battery_optimization_active = False
        coordinator._motion_sensitivity = "high"

        # Mock device method to raise exception
        coordinator.device.async_set_motion_sensitivity = AsyncMock(
            side_effect=ImouException("API error")
        )

        # Should catch exception and log it, not raise
        await coordinator._activate_battery_optimization()

    @pytest.mark.asyncio
    async def test_deactivate_battery_optimization_exception(self, coordinator):
        """Test battery optimization deactivation handles exceptions."""
        coordinator._battery_optimization_active = True

        # Mock device method to raise exception
        coordinator.device.async_set_motion_sensitivity = AsyncMock(
            side_effect=ImouException("API error")
        )

        # Should catch exception and log it, not raise
        await coordinator._deactivate_battery_optimization()


class TestBatteryCoordinatorDeviceMethodSupport:
    """Test battery coordinator handles devices without certain methods."""

    @pytest.mark.asyncio
    async def test_set_motion_sensitivity_device_not_supported(self, coordinator):
        """Test motion sensitivity when device doesn't support method."""
        # Remove the async_set_motion_sensitivity method
        if hasattr(coordinator.device, "async_set_motion_sensitivity"):
            delattr(coordinator.device, "async_set_motion_sensitivity")

        # Should log warning but not raise
        await coordinator._set_motion_sensitivity("low")

    @pytest.mark.asyncio
    async def test_set_motion_sensitivity_device_exception(self, coordinator):
        """Test motion sensitivity when device method raises exception."""
        coordinator.device.async_set_motion_sensitivity = AsyncMock(
            side_effect=ImouException("API error")
        )

        with pytest.raises(ImouException):
            await coordinator._set_motion_sensitivity("medium")

    @pytest.mark.asyncio
    async def test_set_recording_quality_device_not_supported(self, coordinator):
        """Test recording quality when device doesn't support method."""
        # Remove the async_set_recording_quality method
        if hasattr(coordinator.device, "async_set_recording_quality"):
            delattr(coordinator.device, "async_set_recording_quality")

        # Should log warning but not raise
        await coordinator._set_recording_quality("low")

    @pytest.mark.asyncio
    async def test_set_recording_quality_device_exception(self, coordinator):
        """Test recording quality when device method raises exception."""
        coordinator.device.async_set_recording_quality = AsyncMock(
            side_effect=ImouException("API error")
        )

        with pytest.raises(ImouException):
            await coordinator._set_recording_quality("standard")

    @pytest.mark.asyncio
    async def test_set_led_indicators_device_not_supported(self, coordinator):
        """Test LED indicators when device doesn't support method."""
        # Remove the async_set_led_indicators method
        if hasattr(coordinator.device, "async_set_led_indicators"):
            delattr(coordinator.device, "async_set_led_indicators")

        # Should log warning but not raise
        await coordinator._set_led_indicators(False)

    @pytest.mark.asyncio
    async def test_set_led_indicators_device_exception(self, coordinator):
        """Test LED indicators when device method raises exception."""
        coordinator.device.async_set_led_indicators = AsyncMock(
            side_effect=ImouException("API error")
        )

        with pytest.raises(ImouException):
            await coordinator._set_led_indicators(True)

    @pytest.mark.asyncio
    async def test_set_power_mode_device_not_supported(self, coordinator):
        """Test power mode when device doesn't support method."""
        # Remove the async_set_power_mode method
        if hasattr(coordinator.device, "async_set_power_mode"):
            delattr(coordinator.device, "async_set_power_mode")

        # Should log warning but not raise
        await coordinator._set_power_mode("balanced")

    @pytest.mark.asyncio
    async def test_set_power_mode_device_exception(self, coordinator):
        """Test power mode when device method raises exception."""
        coordinator.device.async_set_power_mode = AsyncMock(
            side_effect=ImouException("API error")
        )

        with pytest.raises(ImouException):
            await coordinator._set_power_mode("performance")


class TestBatteryCoordinatorSleepModeDeviceSupport:
    """Test battery coordinator sleep mode with device support checks."""

    @pytest.mark.asyncio
    async def test_enter_sleep_mode_already_active(self, coordinator):
        """Test entering sleep mode when already active."""
        coordinator._sleep_mode_active = True
        coordinator.device.async_enter_sleep_mode = AsyncMock()

        await coordinator.enter_sleep_mode()

        # Should return early without calling device
        coordinator.device.async_enter_sleep_mode.assert_not_called()

    @pytest.mark.asyncio
    async def test_enter_sleep_mode_device_not_supported(self, coordinator):
        """Test entering sleep mode when device doesn't support method."""
        coordinator._sleep_mode_active = False

        # Remove the async_enter_sleep_mode method
        if hasattr(coordinator.device, "async_enter_sleep_mode"):
            delattr(coordinator.device, "async_enter_sleep_mode")

        # Should log warning but not raise or set active
        await coordinator.enter_sleep_mode()
        assert coordinator._sleep_mode_active is False

    @pytest.mark.asyncio
    async def test_enter_sleep_mode_device_exception(self, coordinator):
        """Test entering sleep mode when device method raises exception."""
        coordinator._sleep_mode_active = False
        coordinator.device.async_enter_sleep_mode = AsyncMock(
            side_effect=ImouException("Sleep mode API error")
        )

        with pytest.raises(ImouException):
            await coordinator.enter_sleep_mode()

    @pytest.mark.asyncio
    async def test_exit_sleep_mode_already_inactive(self, coordinator):
        """Test exiting sleep mode when already inactive."""
        coordinator._sleep_mode_active = False
        coordinator.device.async_exit_sleep_mode = AsyncMock()

        await coordinator.exit_sleep_mode()

        # Should return early without calling device
        coordinator.device.async_exit_sleep_mode.assert_not_called()

    @pytest.mark.asyncio
    async def test_exit_sleep_mode_device_not_supported(self, coordinator):
        """Test exiting sleep mode when device doesn't support method."""
        coordinator._sleep_mode_active = True

        # Remove the async_exit_sleep_mode method
        if hasattr(coordinator.device, "async_exit_sleep_mode"):
            delattr(coordinator.device, "async_exit_sleep_mode")

        # Should log warning but not raise or change state
        await coordinator.exit_sleep_mode()
        assert coordinator._sleep_mode_active is True

    @pytest.mark.asyncio
    async def test_exit_sleep_mode_device_exception(self, coordinator):
        """Test exiting sleep mode when device method raises exception."""
        coordinator._sleep_mode_active = True
        coordinator.device.async_exit_sleep_mode = AsyncMock(
            side_effect=ImouException("Wake API error")
        )

        with pytest.raises(ImouException):
            await coordinator.exit_sleep_mode()
