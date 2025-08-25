"""Unit tests for battery coordinator sleep schedule logic."""

from datetime import time
from unittest.mock import patch

import pytest


class TestBatteryCoordinatorSleep:
    """Test battery coordinator sleep schedule logic."""

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
            mock_dt.now.return_value.time.return_value = time(23, 0)

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
            mock_dt.now.return_value.time.return_value = time(23, 0)

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
            mock_dt.now.return_value.time.return_value = time(2, 0)

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
        await coordinator.set_sleep_schedule("custom", time(23, 0), time(7, 0))
        assert coordinator._sleep_schedule == "custom"
        assert coordinator._sleep_start_time == time(23, 0)
        assert coordinator._sleep_end_time == time(7, 0)
