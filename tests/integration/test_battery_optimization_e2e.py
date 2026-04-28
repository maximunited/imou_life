"""End-to-end tests for battery optimization features."""

from datetime import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.imou_life.battery_coordinator import (
    BatteryOptimizationCoordinator,
)
from custom_components.imou_life.const import DOMAIN
from tests.fixtures.mocks import MockConfigEntry


@pytest.mark.asyncio
async def test_battery_coordinator_integration(hass, mock_imou_device):
    """Test battery coordinator integrates with main coordinator."""
    # Create config entry with battery optimization options
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "app_id": "test",
            "app_secret": "secret",
            "device_id": "test_device_123",
            "device_name": "Battery Camera",
        },
        options={
            "power_mode": "power_saving",
            "motion_sensitivity": "low",
            "recording_quality": "standard",
            "led_indicators": False,
            "auto_sleep": True,
            "battery_threshold": 20,
            "sleep_schedule": "night_only",
        },
        entry_id="battery_test",
        version=3,
    )

    # Create battery coordinator
    battery_coordinator = BatteryOptimizationCoordinator(
        hass, mock_imou_device, config_entry, scan_interval=60
    )

    # Initial data fetch
    await battery_coordinator.async_refresh()
    assert battery_coordinator.data is not None
    assert "battery_level" in battery_coordinator.data

    # Verify battery optimization settings loaded
    assert battery_coordinator._power_mode == "power_saving"
    assert battery_coordinator._motion_sensitivity == "low"
    assert battery_coordinator._sleep_schedule == "night_only"


@pytest.mark.asyncio
async def test_battery_sleep_schedule_workflow(hass, mock_imou_device):
    """Test complete battery sleep schedule workflow."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        options={
            "sleep_schedule": "custom",
            "sleep_start_time": "22:00",
            "sleep_end_time": "06:00",
        },
        entry_id="sleep_test",
        version=3,
    )

    coordinator = BatteryOptimizationCoordinator(
        hass, mock_imou_device, config_entry, scan_interval=60
    )

    # Configure custom sleep schedule
    await coordinator.set_sleep_schedule("custom", time(22, 0), time(6, 0))

    assert coordinator._sleep_schedule == "custom"
    assert coordinator._sleep_start_time == time(22, 0)
    assert coordinator._sleep_end_time == time(6, 0)

    # Simulate night time (should enter sleep mode)
    with patch(
        "custom_components.imou_life.battery_coordinator.dt_util"
    ) as mock_dt:
        mock_dt.now.return_value.time.return_value = time(23, 0)

        await coordinator._check_sleep_schedule()

        # Should enter sleep mode during night hours
        assert coordinator.is_sleep_mode_active() is True

    # Simulate morning (should exit sleep mode)
    with patch(
        "custom_components.imou_life.battery_coordinator.dt_util"
    ) as mock_dt:
        mock_dt.now.return_value.time.return_value = time(7, 0)

        await coordinator._check_sleep_schedule()

        # Should exit sleep mode during day hours
        assert coordinator.is_sleep_mode_active() is False


@pytest.mark.asyncio
async def test_battery_based_sleep_activation(hass, mock_imou_device):
    """Test battery-based sleep mode activation."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        options={
            "sleep_schedule": "battery_based",
            "battery_threshold": 25,
        },
        entry_id="battery_sleep_test",
        version=3,
    )

    coordinator = BatteryOptimizationCoordinator(
        hass, mock_imou_device, config_entry, scan_interval=60
    )

    # Set initial battery level above threshold
    coordinator.data = {"battery_level": 50}

    await coordinator._check_sleep_schedule()
    assert coordinator.is_sleep_mode_active() is False

    # Battery drops below threshold
    coordinator.data = {"battery_level": 20}

    await coordinator._check_sleep_schedule()
    assert coordinator.is_sleep_mode_active() is True

    # Battery recovers (with hysteresis)
    coordinator.data = {"battery_level": 30}

    await coordinator._check_sleep_schedule()
    # Should still be in sleep mode due to hysteresis (threshold + 10)
    assert coordinator.is_sleep_mode_active() is True

    # Battery fully recovered
    coordinator.data = {"battery_level": 50}

    await coordinator._check_sleep_schedule()
    # Should exit sleep mode
    assert coordinator.is_sleep_mode_active() is False


@pytest.mark.asyncio
async def test_power_mode_changes_propagate(hass, mock_imou_device):
    """Test that power mode changes propagate to device."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        options={"power_mode": "balanced"},
        entry_id="power_test",
        version=3,
    )

    coordinator = BatteryOptimizationCoordinator(
        hass, mock_imou_device, config_entry, scan_interval=60
    )

    # Mock the set_power_mode method
    coordinator.device.set_power_mode = AsyncMock()

    # Change power mode
    await coordinator.set_power_mode("power_saving")

    # Verify it was set on the device
    coordinator.device.set_power_mode.assert_called_once_with("power_saving")
    assert coordinator._power_mode == "power_saving"


@pytest.mark.asyncio
async def test_led_indicators_toggle(hass, mock_imou_device):
    """Test LED indicators can be toggled."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        options={"led_indicators": True},
        entry_id="led_test",
        version=3,
    )

    coordinator = BatteryOptimizationCoordinator(
        hass, mock_imou_device, config_entry, scan_interval=60
    )

    # Mock LED control method
    coordinator.device.set_led_status = AsyncMock()

    # Initial state
    assert coordinator._led_indicators is True

    # Toggle off
    await coordinator.set_led_indicators(False)
    coordinator.device.set_led_status.assert_called_with(False)
    assert coordinator._led_indicators is False

    # Toggle on
    await coordinator.set_led_indicators(True)
    coordinator.device.set_led_status.assert_called_with(True)
    assert coordinator._led_indicators is True


@pytest.mark.asyncio
async def test_battery_optimization_status_retrieval(hass, mock_imou_device):
    """Test retrieving battery optimization status."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        options={
            "power_mode": "power_saving",
            "motion_sensitivity": "high",
            "recording_quality": "hd",
            "led_indicators": False,
        },
        entry_id="status_test",
        version=3,
    )

    coordinator = BatteryOptimizationCoordinator(
        hass, mock_imou_device, config_entry, scan_interval=60
    )

    # Get optimization status
    status = coordinator.get_battery_optimization_status()

    assert status["power_mode"] == "power_saving"
    assert status["motion_sensitivity"] == "high"
    assert status["recording_quality"] == "hd"
    assert status["led_indicators"] is False


@pytest.mark.asyncio
async def test_battery_data_caching(hass, mock_imou_device):
    """Test that battery data is cached and not fetched redundantly."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        options={},
        entry_id="cache_test",
        version=3,
    )

    coordinator = BatteryOptimizationCoordinator(
        hass, mock_imou_device, config_entry, scan_interval=60
    )

    # First call - should fetch from API
    data1 = await coordinator._get_battery_data()
    assert mock_imou_device.async_get_battery_status.call_count == 1

    # Data should be cached now
    assert coordinator.data is not None

    # Second call - should use cached data
    data2 = await coordinator._get_battery_data()
    # Call count should still be 1 (used cache)
    assert mock_imou_device.async_get_battery_status.call_count == 1

    # Both should return same data
    assert data1 == data2


@pytest.mark.asyncio
async def test_concurrent_sleep_mode_operations(hass, mock_imou_device):
    """Test that concurrent sleep mode operations are thread-safe."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        options={},
        entry_id="concurrent_test",
        version=3,
    )

    coordinator = BatteryOptimizationCoordinator(
        hass, mock_imou_device, config_entry, scan_interval=60
    )

    # Simulate concurrent operations using lock
    import asyncio

    results = []

    async def enter_sleep():
        await coordinator.enter_sleep_mode()
        results.append("enter")

    async def exit_sleep():
        await coordinator.exit_sleep_mode()
        results.append("exit")

    # Run concurrent operations
    await asyncio.gather(enter_sleep(), exit_sleep(), enter_sleep())

    # All operations should complete without deadlock
    assert len(results) == 3
    assert "enter" in results
    assert "exit" in results
