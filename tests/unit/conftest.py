"""Shared fixtures for battery coordinator tests."""

from unittest.mock import MagicMock

import pytest

from custom_components.imou_life.battery_coordinator import (
    BatteryOptimizationCoordinator,
)


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    return MagicMock()


@pytest.fixture
def mock_device():
    """Create a mock device."""
    device = MagicMock()
    device.get_name.return_value = "Test Device"
    return device


@pytest.fixture
def mock_config_entry():
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
def coordinator(mock_hass, mock_device, mock_config_entry):
    """Create a battery optimization coordinator instance."""
    return BatteryOptimizationCoordinator(
        mock_hass,
        mock_device,
        mock_config_entry,
        scan_interval=300,
    )


def create_coordinator_with_options(mock_hass, mock_device, options):
    """Helper function to create coordinator with specific options."""
    config_entry = MagicMock()
    config_entry.options = options
    return BatteryOptimizationCoordinator(
        mock_hass, mock_device, config_entry, scan_interval=300
    )
