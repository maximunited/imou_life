"""Unit tests for battery coordinator device settings and validation."""

import asyncio
from unittest.mock import patch

import pytest


class TestBatteryCoordinatorSettings:
    """Test battery coordinator device settings and validation."""

    @pytest.mark.asyncio
    async def test_set_motion_sensitivity_valid(self, coordinator):
        """Test setting valid motion sensitivity."""
        with patch.object(coordinator, "device"):
            await coordinator._set_motion_sensitivity("low")

    def test_set_motion_sensitivity_invalid(self, coordinator):
        """Test setting invalid motion sensitivity."""
        with pytest.raises(ValueError, match="Invalid motion sensitivity: invalid"):
            asyncio.run(coordinator._set_motion_sensitivity("invalid"))

    @pytest.mark.asyncio
    async def test_set_recording_quality_valid(self, coordinator):
        """Test setting valid recording quality."""
        with patch.object(coordinator, "device"):
            await coordinator._set_recording_quality("low")

    def test_set_recording_quality_invalid(self, coordinator):
        """Test setting invalid recording quality."""
        with pytest.raises(ValueError, match="Invalid recording quality: invalid"):
            asyncio.run(coordinator._set_recording_quality("invalid"))

    @pytest.mark.asyncio
    async def test_set_power_mode_valid(self, coordinator):
        """Test setting valid power mode."""
        with patch.object(coordinator, "device"):
            await coordinator._set_power_mode("power_saving")

    def test_set_power_mode_invalid(self, coordinator):
        """Test setting invalid power mode."""
        with pytest.raises(ValueError, match="Invalid power mode: invalid"):
            asyncio.run(coordinator._set_power_mode("invalid"))

    @pytest.mark.asyncio
    async def test_set_led_indicators(self, coordinator):
        """Test setting LED indicators."""
        with patch.object(coordinator, "device"):
            await coordinator._set_led_indicators(False)
            await coordinator._set_led_indicators(True)

    def test_get_battery_optimization_status(self, coordinator):
        """Test getting battery optimization status."""
        status = coordinator.get_battery_optimization_status()

        expected_status = {
            "active": False,
            "power_mode": "balanced",
            "motion_sensitivity": "medium",
            "recording_quality": "standard",
            "led_indicators": True,
            "auto_sleep": False,
            "battery_threshold": 20,
            "sleep_schedule": "never",
        }

        for key, expected_value in expected_status.items():
            assert status[key] == expected_value
