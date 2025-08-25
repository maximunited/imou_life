"""Unit tests for battery coordinator data update methods."""

from unittest.mock import patch

import pytest


class TestBatteryCoordinatorData:
    """Test battery coordinator data update methods."""

    @pytest.mark.asyncio
    async def test_async_update_data_success(self, coordinator):
        """Test successful data update."""
        with patch.object(coordinator, "_get_battery_data", return_value={"level": 85}):
            with patch.object(coordinator, "_check_battery_optimization"):
                with patch.object(coordinator, "_check_sleep_schedule"):
                    data = await coordinator._async_update_data()

                    expected_fields = [
                        "battery_level",
                        "power_mode",
                        "battery_optimization_active",
                    ]
                    for field in expected_fields:
                        assert field in data

    @pytest.mark.asyncio
    async def test_async_update_data_exception(self, coordinator):
        """Test data update with exception."""
        with patch.object(
            coordinator, "_get_battery_data", side_effect=Exception("Test error")
        ):
            with pytest.raises(Exception, match="Test error"):
                await coordinator._async_update_data()
