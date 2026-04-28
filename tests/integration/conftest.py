"""Shared fixtures for integration tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imouapi.device import ImouDevice
from imouapi.device_entity import ImouBinarySensor, ImouSensor, ImouSwitch


@pytest.fixture
def mock_imou_device():
    """Create a fully mocked Imou device with all sensors."""
    device = MagicMock(spec=ImouDevice)
    device.get_name.return_value = "Test Camera"
    device.get_device_id.return_value = "test_device_123"
    device.get_model.return_value = "IPC-C22EP"
    device.get_manufacturer.return_value = "Imou"
    device.get_firmware.return_value = "2.800.0000000.51.R"
    device.get_status.return_value = True

    # Mock async methods
    device.async_initialize = AsyncMock()
    device.async_get_data = AsyncMock(return_value={
        "battery_level": 85,
        "online": True,
        "motion_detected": False,
    })
    device.async_get_battery_status = AsyncMock(return_value={
        "level": 85,
        "voltage": 3.8,
        "consumption": 0.5,
        "charging": False,
    })

    # Mock battery optimization methods
    device.async_enter_sleep_mode = AsyncMock()
    device.async_exit_sleep_mode = AsyncMock()
    device.async_set_power_mode = AsyncMock()
    device.async_set_motion_sensitivity = AsyncMock()
    device.async_set_recording_quality = AsyncMock()
    device.async_set_led_indicators = AsyncMock()

    # Also mock synchronous versions for backward compat
    device.set_power_mode = AsyncMock()
    device.set_led_status = AsyncMock()

    # Mock sensor discovery by platform
    def get_sensors_by_platform(platform):
        if platform == "switch":
            switch = ImouSwitch(None, "test_device_123", "Test Camera", "motionDetect")
            switch.is_on = MagicMock(return_value=True)
            switch.async_turn_on = AsyncMock()
            switch.async_turn_off = AsyncMock()
            return [switch]
        elif platform == "sensor":
            sensor = ImouSensor(None, "test_device_123", "Test Camera", "lastAlarm")
            sensor.get_state = MagicMock(return_value="2026-04-29 00:00:00")
            return [sensor]
        elif platform == "binary_sensor":
            binary = ImouBinarySensor(None, "test_device_123", "Test Camera", "online")
            binary.is_on = MagicMock(return_value=True)
            return [binary]
        elif platform == "button":
            return []
        elif platform == "select":
            return []
        elif platform == "camera":
            return []
        return []

    device.get_sensors_by_platform = get_sensors_by_platform

    return device


@pytest.fixture
def mock_imou_api():
    """Mock the Imou API client."""
    with patch("imouapi.api.ImouAPIClient") as mock_api:
        api_instance = MagicMock()
        api_instance.async_connect = AsyncMock()
        mock_api.return_value = api_instance
        yield api_instance


@pytest.fixture
def mock_discover_service():
    """Mock the Imou discover service."""
    with patch("imouapi.device.ImouDiscoverService") as mock_service:
        service_instance = MagicMock()
        service_instance.async_discover_devices = AsyncMock()
        mock_service.return_value = service_instance
        yield service_instance
