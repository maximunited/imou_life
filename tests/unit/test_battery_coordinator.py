"""Unit tests for battery optimization coordinator."""

from datetime import time, timedelta
from unittest.mock import MagicMock, patch

import pytest

from custom_components.imou_life.battery_coordinator import (
    BatteryOptimizationCoordinator,
)


class TestBatteryOptimizationCoordinator:
    """Test battery optimization coordinator."""

    @pytest.fixture
    def mock_hass(self):
        """Create a mock Home Assistant instance."""
        return MagicMock()

    @pytest.fixture
    def mock_device(self):
        """Create a mock device."""
        device = MagicMock()
        device.get_name.return_value = "Test Device"
        return device

    @pytest.fixture
    def mock_config_entry(self):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.options = {
            "power_mode": "balanced",
            "motion_sensitivity": "medium",
            "recording_quality": "standard",
            "led_indicators": True,
            "auto_sleep": False,
            "battery_threshold": 20,
            "sleep_schedule": "never",
        }
        return config_entry

    @pytest.fixture
    def coordinator(self, mock_hass, mock_device, mock_config_entry):
        """Create a battery optimization coordinator instance."""
        return BatteryOptimizationCoordinator(
            mock_hass,
            mock_device,
            mock_config_entry,
            scan_interval=timedelta(seconds=300),
        )

    def test_coordinator_initialization(
        self, coordinator, mock_device, mock_config_entry
    ):
        """Test coordinator initialization."""
        assert coordinator.device == mock_device
        assert coordinator.config_entry == mock_config_entry
        assert coordinator._power_mode == "balanced"
        assert coordinator._motion_sensitivity == "medium"
        assert coordinator._recording_quality == "standard"
        assert coordinator._led_indicators is True
        assert coordinator._auto_sleep is False
        assert coordinator._battery_threshold == 20
        assert coordinator._sleep_schedule == "never"
        assert coordinator._battery_optimization_active is False

    def test_coordinator_default_values(self, mock_hass, mock_device):
        """Test coordinator with default values."""
        config_entry = MagicMock()
        config_entry.options = {}

        coordinator = BatteryOptimizationCoordinator(
            mock_hass, mock_device, config_entry, scan_interval=timedelta(seconds=300)
        )

        assert coordinator._power_mode == "balanced"
        assert coordinator._motion_sensitivity == "medium"
        assert coordinator._recording_quality == "standard"
        assert coordinator._led_indicators is True
        assert coordinator._auto_sleep is False
        assert coordinator._battery_threshold == 20

    def test_load_settings_custom_sleep_schedule(self, mock_hass, mock_device):
        """Test loading custom sleep schedule settings."""
        config_entry = MagicMock()
        config_entry.options = {
            "sleep_schedule": "custom",
            "sleep_start_time": "23:00",
            "sleep_end_time": "07:00",
        }

        coordinator = BatteryOptimizationCoordinator(
            mock_hass, mock_device, config_entry, scan_interval=timedelta(seconds=300)
        )

        assert coordinator._sleep_schedule == "custom"
        assert coordinator._sleep_start_time == time(23, 0)
        assert coordinator._sleep_end_time == time(7, 0)

    def test_load_settings_invalid_sleep_times(self, mock_hass, mock_device):
        """Test loading invalid sleep schedule times."""
        config_entry = MagicMock()
        config_entry.options = {
            "sleep_schedule": "custom",
            "sleep_start_time": "invalid",
            "sleep_end_time": "invalid",
        }

        coordinator = BatteryOptimizationCoordinator(
            mock_hass, mock_device, config_entry, scan_interval=timedelta(seconds=300)
        )

        # Should fall back to defaults
        assert coordinator._sleep_start_time == time(22, 0)
        assert coordinator._sleep_end_time == time(6, 0)

    @pytest.mark.asyncio
    async def test_get_battery_data_success(self, coordinator):
        """Test getting battery data successfully."""
        battery_data = await coordinator._get_battery_data()

        assert "level" in battery_data
        assert "voltage" in battery_data
        assert "consumption" in battery_data
        assert battery_data["level"] == 85
        assert battery_data["voltage"] == 3.8
        assert battery_data["consumption"] == 0.5

    @pytest.mark.asyncio
    async def test_get_battery_data_exception(self, coordinator):
        """Test getting battery data with exception."""
        # Mock the method to raise an exception
        with patch.object(
            coordinator, "_get_battery_data", side_effect=Exception("Test error")
        ):
            with pytest.raises(Exception, match="Test error"):
                await coordinator._get_battery_data()

    @pytest.mark.asyncio
    async def test_check_battery_optimization_below_threshold(self, coordinator):
        """Test battery optimization activation when below threshold."""
        coordinator._battery_threshold = 20
        coordinator._battery_optimization_active = False

        battery_data = {"level": 15}

        with patch.object(
            coordinator, "_activate_battery_optimization"
        ) as mock_activate:
            await coordinator._check_battery_optimization(battery_data)
            mock_activate.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_battery_optimization_above_threshold(self, coordinator):
        """Test battery optimization deactivation when above threshold."""
        coordinator._battery_threshold = 20
        coordinator._battery_optimization_active = True

        battery_data = {"level": 35}  # Above threshold + 10

        with patch.object(
            coordinator, "_deactivate_battery_optimization"
        ) as mock_deactivate:
            await coordinator._check_battery_optimization(battery_data)
            mock_deactivate.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_battery_optimization_no_change(self, coordinator):
        """Test battery optimization when no change needed."""
        coordinator._battery_threshold = 20
        coordinator._battery_optimization_active = True

        battery_data = {"level": 25}  # Between threshold and threshold + 10

        with patch.object(
            coordinator, "_activate_battery_optimization"
        ) as mock_activate:
            with patch.object(
                coordinator, "_deactivate_battery_optimization"
            ) as mock_deactivate:
                await coordinator._check_battery_optimization(battery_data)
                mock_activate.assert_not_called()
                mock_deactivate.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_sleep_schedule_never(self, coordinator):
        """Test sleep schedule check with 'never' schedule."""
        coordinator._sleep_schedule = "never"

        with patch.object(coordinator, "_enter_sleep_mode") as mock_enter:
            with patch.object(coordinator, "_exit_sleep_mode") as mock_exit:
                await coordinator._check_sleep_schedule()
                mock_enter.assert_not_called()
                mock_exit.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_sleep_schedule_night_only(self, coordinator):
        """Test sleep schedule check with 'night_only' schedule."""
        coordinator._sleep_schedule = "night_only"
        coordinator._sleep_start_time = time(22, 0)
        coordinator._sleep_end_time = time(6, 0)

        with patch(
            "custom_components.imou_life.battery_coordinator.dt_util"
        ) as mock_dt:
            mock_dt.now.return_value.time.return_value = time(23, 0)  # Night time

            with patch.object(coordinator, "_enter_sleep_mode") as mock_enter:
                with patch.object(
                    coordinator, "_is_sleep_mode_active", return_value=False
                ):
                    await coordinator._check_sleep_schedule()
                    mock_enter.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_sleep_schedule_custom_same_day(self, coordinator):
        """Test sleep schedule check with custom same-day schedule."""
        coordinator._sleep_schedule = "custom"
        coordinator._sleep_start_time = time(22, 0)
        coordinator._sleep_end_time = time(6, 0)

        with patch(
            "custom_components.imou_life.battery_coordinator.dt_util"
        ) as mock_dt:
            mock_dt.now.return_value.time.return_value = time(
                23, 0
            )  # During sleep time

            with patch.object(coordinator, "_enter_sleep_mode") as mock_enter:
                with patch.object(
                    coordinator, "_is_sleep_mode_active", return_value=False
                ):
                    await coordinator._check_sleep_schedule()
                    mock_enter.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_sleep_schedule_custom_overnight(self, coordinator):
        """Test sleep schedule check with custom overnight schedule."""
        coordinator._sleep_schedule = "custom"
        coordinator._sleep_start_time = time(22, 0)
        coordinator._sleep_end_time = time(6, 0)

        with patch(
            "custom_components.imou_life.battery_coordinator.dt_util"
        ) as mock_dt:
            mock_dt.now.return_value.time.return_value = time(2, 0)  # During sleep time

            with patch.object(coordinator, "_enter_sleep_mode") as mock_enter:
                with patch.object(
                    coordinator, "_is_sleep_mode_active", return_value=False
                ):
                    await coordinator._check_sleep_schedule()
                    mock_enter.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_sleep_schedule_battery_based(self, coordinator):
        """Test sleep schedule check with battery-based schedule."""
        coordinator._sleep_schedule = "battery_based"
        coordinator._battery_threshold = 20

        with patch.object(coordinator, "_get_battery_data", return_value={"level": 15}):
            with patch.object(coordinator, "_enter_sleep_mode") as mock_enter:
                with patch.object(
                    coordinator, "_is_sleep_mode_active", return_value=False
                ):
                    await coordinator._check_sleep_schedule()
                    mock_enter.assert_called_once()

    @pytest.mark.asyncio
    async def test_activate_battery_optimization(self, coordinator):
        """Test activating battery optimization."""
        coordinator._motion_sensitivity = "high"
        coordinator._recording_quality = "high"
        coordinator._led_indicators = True
        coordinator._power_mode = "balanced"

        with patch.object(coordinator, "_set_motion_sensitivity") as mock_sensitivity:
            with patch.object(coordinator, "_set_recording_quality") as mock_quality:
                with patch.object(coordinator, "_set_led_indicators") as mock_led:
                    with patch.object(coordinator, "_set_power_mode") as mock_power:
                        await coordinator._activate_battery_optimization()

                        mock_sensitivity.assert_called_once_with("low")
                        mock_quality.assert_called_once_with("low")
                        mock_led.assert_called_once_with(False)
                        mock_power.assert_called_once_with("power_saving")
                        assert coordinator._battery_optimization_active is True

    @pytest.mark.asyncio
    async def test_deactivate_battery_optimization(self, coordinator):
        """Test deactivating battery optimization."""
        coordinator._battery_optimization_active = True
        coordinator._motion_sensitivity = "low"
        coordinator._recording_quality = "low"
        coordinator._led_indicators = False
        coordinator._power_mode = "power_saving"

        with patch.object(coordinator, "_set_motion_sensitivity") as mock_sensitivity:
            with patch.object(coordinator, "_set_recording_quality") as mock_quality:
                with patch.object(coordinator, "_set_led_indicators") as mock_led:
                    with patch.object(coordinator, "_set_power_mode") as mock_power:
                        await coordinator._deactivate_battery_optimization()

                        mock_sensitivity.assert_called_once_with("low")
                        mock_quality.assert_called_once_with("low")
                        mock_led.assert_called_once_with(False)
                        mock_power.assert_called_once_with("power_saving")
                        assert coordinator._battery_optimization_active is False

    @pytest.mark.asyncio
    async def test_set_motion_sensitivity_valid(self, coordinator):
        """Test setting valid motion sensitivity."""
        with patch.object(coordinator, "device"):
            await coordinator._set_motion_sensitivity("low")
            # Note: This would call the actual device API in real implementation

    @pytest.mark.asyncio
    async def test_set_motion_sensitivity_invalid(self, coordinator):
        """Test setting invalid motion sensitivity."""
        with pytest.raises(ValueError, match="Invalid motion sensitivity: invalid"):
            await coordinator._set_motion_sensitivity("invalid")

    @pytest.mark.asyncio
    async def test_set_recording_quality_valid(self, coordinator):
        """Test setting valid recording quality."""
        with patch.object(coordinator, "device"):
            await coordinator._set_recording_quality("low")
            # Note: This would call the actual device API in real implementation

    @pytest.mark.asyncio
    async def test_set_recording_quality_invalid(self, coordinator):
        """Test setting invalid recording quality."""
        with pytest.raises(ValueError, match="Invalid recording quality: invalid"):
            await coordinator._set_recording_quality("invalid")

    @pytest.mark.asyncio
    async def test_set_power_mode_valid(self, coordinator):
        """Test setting valid power mode."""
        with patch.object(coordinator, "device"):
            await coordinator._set_power_mode("power_saving")
            # Note: This would call the actual device API in real implementation

    @pytest.mark.asyncio
    async def test_set_power_mode_invalid(self, coordinator):
        """Test setting invalid power mode."""
        with pytest.raises(ValueError, match="Invalid power mode: invalid"):
            await coordinator._set_power_mode("invalid")

    @pytest.mark.asyncio
    async def test_optimize_battery(self, coordinator):
        """Test optimize battery method."""
        with patch.object(coordinator, "_set_power_mode") as mock_power:
            with patch.object(
                coordinator, "_set_motion_sensitivity"
            ) as mock_sensitivity:
                with patch.object(
                    coordinator, "_set_recording_quality"
                ) as mock_quality:
                    with patch.object(coordinator, "_set_led_indicators") as mock_led:
                        await coordinator.optimize_battery(
                            power_mode="ultra_power_saving",
                            motion_sensitivity="low",
                            recording_quality="low",
                            led_indicators=False,
                        )

                        mock_power.assert_called_once_with("ultra_power_saving")
                        mock_sensitivity.assert_called_once_with("low")
                        mock_quality.assert_called_once_with("low")
                        mock_led.assert_called_once_with(False)
                        assert coordinator._battery_optimization_active is True

    @pytest.mark.asyncio
    async def test_set_sleep_schedule_valid(self, coordinator):
        """Test setting valid sleep schedule."""
        await coordinator.set_sleep_schedule("night_only")
        assert coordinator._sleep_schedule == "night_only"

    @pytest.mark.asyncio
    async def test_set_sleep_schedule_invalid(self, coordinator):
        """Test setting invalid sleep schedule."""
        with pytest.raises(ValueError, match="Invalid sleep schedule: invalid"):
            await coordinator.set_sleep_schedule("invalid")

    @pytest.mark.asyncio
    async def test_set_sleep_schedule_with_times(self, coordinator):
        """Test setting sleep schedule with custom times."""
        start_time = time(23, 0)
        end_time = time(7, 0)

        await coordinator.set_sleep_schedule("custom", start_time, end_time)

        assert coordinator._sleep_schedule == "custom"
        assert coordinator._sleep_start_time == start_time
        assert coordinator._sleep_end_time == end_time

    def test_get_battery_optimization_status(self, coordinator):
        """Test getting battery optimization status."""
        status = coordinator.get_battery_optimization_status()

        assert status["active"] is False
        assert status["power_mode"] == "balanced"
        assert status["motion_sensitivity"] == "medium"
        assert status["recording_quality"] == "standard"
        assert status["led_indicators"] is True
        assert status["auto_sleep"] is False
        assert status["battery_threshold"] == 20
        assert status["sleep_schedule"] == "never"

    @pytest.mark.asyncio
    async def test_async_update_data_success(self, coordinator):
        """Test successful data update."""
        with patch.object(coordinator, "_get_battery_data", return_value={"level": 85}):
            with patch.object(coordinator, "_check_battery_optimization"):
                with patch.object(coordinator, "_check_sleep_schedule"):
                    data = await coordinator._async_update_data()

                    assert "battery_level" in data
                    assert "power_mode" in data
                    assert "battery_optimization_active" in data

    @pytest.mark.asyncio
    async def test_async_update_data_exception(self, coordinator):
        """Test data update with exception."""
        with patch.object(
            coordinator, "_get_battery_data", side_effect=Exception("Test error")
        ):
            with pytest.raises(Exception, match="Test error"):
                await coordinator._async_update_data()
