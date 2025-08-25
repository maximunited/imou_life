"""Unit tests for battery coordinator initialization and configuration."""

from datetime import time

from tests.unit.conftest import create_coordinator_with_options


class TestBatteryCoordinatorInit:
    """Test battery coordinator initialization and configuration."""

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
        coordinator = create_coordinator_with_options(mock_hass, mock_device, {})
        assert coordinator._power_mode == "balanced"
        assert coordinator._motion_sensitivity == "medium"
        assert coordinator._recording_quality == "standard"
        assert coordinator._led_indicators is True
        assert coordinator._auto_sleep is False
        assert coordinator._battery_threshold == 20

    def test_load_settings_custom_sleep_schedule(self, mock_hass, mock_device):
        """Test loading custom sleep schedule settings."""
        options = {
            "sleep_schedule": "custom",
            "sleep_start_time": "23:00",
            "sleep_end_time": "07:00",
        }
        coordinator = create_coordinator_with_options(mock_hass, mock_device, options)

        assert coordinator._sleep_schedule == "custom"
        assert coordinator._sleep_start_time == time(23, 0)
        assert coordinator._sleep_end_time == time(7, 0)

    def test_load_settings_invalid_sleep_times(self, mock_hass, mock_device):
        """Test loading invalid sleep schedule times."""
        options = {
            "sleep_schedule": "custom",
            "sleep_start_time": "invalid",
            "sleep_end_time": "invalid",
        }
        coordinator = create_coordinator_with_options(mock_hass, mock_device, options)

        # Should fall back to defaults
        assert coordinator._sleep_start_time == time(22, 0)
        assert coordinator._sleep_end_time == time(6, 0)
