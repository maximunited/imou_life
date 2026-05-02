"""Tests for sensor and button platform setup functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSensorPlatformSetup:
    """Test sensor platform setup."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.device.get_sensors_by_platform.return_value = []
        coordinator.entities = []
        coordinator.is_rate_limited = False
        return coordinator

    @pytest.fixture
    def mock_config_entry(self, mock_coordinator):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry_123"
        config_entry.runtime_data = mock_coordinator
        return config_entry

    @pytest.mark.asyncio
    async def test_async_setup_entry_adds_api_status_sensor(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup adds API status diagnostic sensor."""
        from custom_components.imou_life.sensor import async_setup_entry

        async_add_devices = MagicMock()

        with patch(
            "custom_components.imou_life.sensor.setup_platform", new_callable=AsyncMock
        ) as mock_setup:
            await async_setup_entry(MagicMock(), mock_config_entry, async_add_devices)

            # Should call setup_platform for regular sensors
            mock_setup.assert_called_once()

            # Should also add API status sensor
            async_add_devices.assert_called_once()
            added_entities = async_add_devices.call_args[0][0]
            assert len(added_entities) == 1
            assert added_entities[0].__class__.__name__ == "ImouAPIStatusSensor"


class TestButtonPlatformSetup:
    """Test button platform setup."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.device.get_sensors_by_platform.return_value = []
        coordinator.entities = []
        return coordinator

    @pytest.fixture
    def mock_config_entry(self, mock_coordinator):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry_123"
        config_entry.runtime_data = mock_coordinator
        return config_entry

    @pytest.mark.asyncio
    async def test_async_setup_entry_no_buttons(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup with no button sensors."""
        from custom_components.imou_life.button import async_setup_entry

        async_add_devices = MagicMock()

        await async_setup_entry(MagicMock(), mock_config_entry, async_add_devices)

        # Should call async_add_devices with empty list
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 0

    @pytest.mark.asyncio
    async def test_async_setup_entry_with_buttons(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup with button sensors."""
        from custom_components.imou_life.button import async_setup_entry

        # Create mock sensor instances
        sensor1 = MagicMock()
        sensor1.get_description.return_value = "Button 1"

        sensor2 = MagicMock()
        sensor2.get_description.return_value = "Button 2"

        mock_coordinator.device.get_sensors_by_platform.return_value = [
            sensor1,
            sensor2,
        ]

        async_add_devices = MagicMock()

        await async_setup_entry(MagicMock(), mock_config_entry, async_add_devices)

        # Should add 2 button entities
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 2
        assert len(mock_coordinator.entities) == 2


class TestBatteryBinarySensorErrorPaths:
    """Test battery binary sensor error handling paths."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.last_update_success = True
        coordinator.device.get_status.return_value = True
        coordinator.data = None
        return coordinator

    @pytest.fixture
    def mock_config_entry(self, mock_coordinator):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry_123"
        config_entry.runtime_data = mock_coordinator
        return config_entry

    @pytest.mark.asyncio
    async def test_low_battery_sensor_no_coordinator_data(
        self, mock_coordinator, mock_config_entry
    ):
        """Test low battery sensor when coordinator has no data."""
        from custom_components.imou_life.battery_binary_sensor import (
            ImouBatteryBinarySensor,
        )

        sensor = ImouBatteryBinarySensor(
            mock_coordinator,
            mock_config_entry,
            "lowBattery",
            "Low Battery",
            "mdi:battery-alert",
            "low_battery",
        )

        # Coordinator has no data
        mock_coordinator.data = None
        mock_coordinator.get_battery_optimization_status = MagicMock(
            return_value={"battery_threshold": 20}
        )

        # Should return False (not low battery) when no data
        assert sensor.is_on is False

    @pytest.mark.asyncio
    async def test_charging_sensor_no_coordinator_data(
        self, mock_coordinator, mock_config_entry
    ):
        """Test charging sensor when coordinator has no data."""
        from custom_components.imou_life.battery_binary_sensor import (
            ImouBatteryBinarySensor,
        )

        sensor = ImouBatteryBinarySensor(
            mock_coordinator,
            mock_config_entry,
            "charging",
            "Charging",
            "mdi:battery-charging",
            "charging",
        )

        # Coordinator has no data
        mock_coordinator.data = None

        # Should return False when no data
        assert sensor.is_on is False

    @pytest.mark.asyncio
    async def test_power_saving_sensor_no_coordinator_status(
        self, mock_coordinator, mock_config_entry
    ):
        """Test power saving sensor when coordinator has no optimization status."""
        from custom_components.imou_life.battery_binary_sensor import (
            ImouBatteryBinarySensor,
        )

        sensor = ImouBatteryBinarySensor(
            mock_coordinator,
            mock_config_entry,
            "powerSavingActive",
            "Power Saving Active",
            "mdi:battery-saver",
            "power_saving_active",
        )

        # Remove get_battery_optimization_status method
        if hasattr(mock_coordinator, "get_battery_optimization_status"):
            delattr(mock_coordinator, "get_battery_optimization_status")

        # Should return False when method not available
        assert sensor.is_on is False

    @pytest.mark.asyncio
    async def test_sleep_mode_sensor_no_coordinator_method(
        self, mock_coordinator, mock_config_entry
    ):
        """Test sleep mode sensor when coordinator has no is_sleep_mode_active method."""
        from custom_components.imou_life.battery_binary_sensor import (
            ImouBatteryBinarySensor,
        )

        sensor = ImouBatteryBinarySensor(
            mock_coordinator,
            mock_config_entry,
            "sleepModeActive",
            "Sleep Mode Active",
            "mdi:power-sleep",
            "sleep_mode_active",
        )

        # Remove is_sleep_mode_active method
        if hasattr(mock_coordinator, "is_sleep_mode_active"):
            delattr(mock_coordinator, "is_sleep_mode_active")

        # Should return False when method not available
        assert sensor.is_on is False
