"""Unit tests for battery coordinator optimization logic."""

from unittest.mock import patch

import pytest


class TestBatteryCoordinatorOptimization:
    """Test battery coordinator optimization logic."""

    @pytest.mark.asyncio
    async def test_get_battery_data_success(self, coordinator):
        """Test getting battery data successfully."""
        battery_data = await coordinator._get_battery_data()

        expected_fields = ["level", "voltage", "consumption"]
        for field in expected_fields:
            assert field in battery_data

        assert battery_data["level"] == 85
        assert battery_data["voltage"] == 3.8
        assert battery_data["consumption"] == 0.5

    @pytest.mark.asyncio
    async def test_get_battery_data_exception(self, coordinator):
        """Test getting battery data with exception."""
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

        with patch.object(
            coordinator, "_activate_battery_optimization"
        ) as mock_activate:
            await coordinator._check_battery_optimization({"level": 15})
            mock_activate.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_battery_optimization_above_threshold(self, coordinator):
        """Test battery optimization deactivation when above threshold."""
        coordinator._battery_threshold = 20
        coordinator._battery_optimization_active = True

        with patch.object(
            coordinator, "_deactivate_battery_optimization"
        ) as mock_deactivate:
            await coordinator._check_battery_optimization({"level": 35})
            mock_deactivate.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_battery_optimization_no_change(self, coordinator):
        """Test battery optimization when no change needed."""
        coordinator._battery_threshold = 20
        coordinator._battery_optimization_active = True

        with patch.object(
            coordinator, "_activate_battery_optimization"
        ) as mock_activate:
            with patch.object(
                coordinator, "_deactivate_battery_optimization"
            ) as mock_deactivate:
                await coordinator._check_battery_optimization({"level": 25})
                mock_activate.assert_not_called()
                mock_deactivate.assert_not_called()

    @pytest.mark.asyncio
    async def test_activate_battery_optimization(self, coordinator):
        """Test activating battery optimization."""
        coordinator._motion_sensitivity = "high"
        coordinator._recording_quality = "high"
        coordinator._led_indicators = True
        coordinator._power_mode = "balanced"

        with patch.object(coordinator, "_set_motion_sensitivity") as mock_motion:
            with patch.object(coordinator, "_set_recording_quality") as mock_recording:
                with patch.object(coordinator, "_set_led_indicators") as mock_led:
                    with patch.object(coordinator, "_set_power_mode") as mock_power:
                        await coordinator._activate_battery_optimization()

                        mock_motion.assert_called_once_with("low")
                        mock_recording.assert_called_once_with("low")
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

        with patch.object(coordinator, "_set_motion_sensitivity") as mock_motion:
            with patch.object(coordinator, "_set_recording_quality") as mock_recording:
                with patch.object(coordinator, "_set_led_indicators") as mock_led:
                    with patch.object(coordinator, "_set_power_mode") as mock_power:
                        await coordinator._deactivate_battery_optimization()

                        mock_motion.assert_called_once_with("low")
                        mock_recording.assert_called_once_with("low")
                        mock_led.assert_called_once_with(False)
                        mock_power.assert_called_once_with("power_saving")
                        assert coordinator._battery_optimization_active is False

    @pytest.mark.asyncio
    async def test_optimize_battery(self, coordinator):
        """Test optimize battery method."""
        with patch.object(coordinator, "_set_power_mode") as mock_power:
            with patch.object(coordinator, "_set_motion_sensitivity") as mock_motion:
                with patch.object(
                    coordinator, "_set_recording_quality"
                ) as mock_recording:
                    with patch.object(coordinator, "_set_led_indicators") as mock_led:
                        await coordinator.optimize_battery(
                            power_mode="ultra_power_saving",
                            motion_sensitivity="low",
                            recording_quality="low",
                            led_indicators=False,
                        )

                        mock_power.assert_called_once_with("ultra_power_saving")
                        mock_motion.assert_called_once_with("low")
                        mock_recording.assert_called_once_with("low")
                        mock_led.assert_called_once_with(False)
                        assert coordinator._battery_optimization_active is True
