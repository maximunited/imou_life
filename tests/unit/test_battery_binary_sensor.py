"""Unit tests for battery optimization binary sensor entities."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.imou_life.battery_binary_sensor import ImouBatteryBinarySensor


class TestImouBatteryBinarySensor:
    """Test battery optimization binary sensor entities."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Device"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_device_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = MagicMock()
        return coordinator

    @pytest.fixture
    def mock_config_entry(self):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry_123"
        config_entry.options = {
            "battery_threshold": 20,
        }
        return config_entry

    @pytest.fixture
    def low_battery_sensor(self, mock_coordinator, mock_config_entry):
        """Create a low battery binary sensor entity."""
        return ImouBatteryBinarySensor(
            mock_coordinator,
            mock_config_entry,
            "lowBattery",
            "Low Battery",
            "mdi:battery-alert",
            "low_battery",
        )

    @pytest.fixture
    def charging_sensor(self, mock_coordinator, mock_config_entry):
        """Create a charging binary sensor entity."""
        return ImouBatteryBinarySensor(
            mock_coordinator,
            mock_config_entry,
            "charging",
            "Charging",
            "mdi:battery-charging",
            "charging",
        )

    @pytest.fixture
    def power_saving_sensor(self, mock_coordinator, mock_config_entry):
        """Create a power saving active binary sensor entity."""
        return ImouBatteryBinarySensor(
            mock_coordinator,
            mock_config_entry,
            "powerSavingActive",
            "Power Saving Active",
            "mdi:battery-saver",
            "power_saving_active",
        )

    @pytest.fixture
    def sleep_mode_sensor(self, mock_coordinator, mock_config_entry):
        """Create a sleep mode active binary sensor entity."""
        return ImouBatteryBinarySensor(
            mock_coordinator,
            mock_config_entry,
            "sleepModeActive",
            "Sleep Mode Active",
            "mdi:power-sleep",
            "sleep_mode_active",
        )

    def test_sensor_initialization(self, low_battery_sensor):
        """Test binary sensor entity initialization."""
        assert low_battery_sensor.sensor_type == "lowBattery"
        assert low_battery_sensor._description == "Low Battery"
        assert low_battery_sensor._icon == "mdi:battery-alert"
        assert low_battery_sensor._attribute_name == "low_battery"

    def test_sensor_name(self, low_battery_sensor):
        """Test binary sensor entity name."""
        assert low_battery_sensor.name == "Test Device Low Battery"

    def test_sensor_unique_id(self, low_battery_sensor, mock_config_entry):
        """Test binary sensor entity unique ID."""
        expected_id = f"{mock_config_entry.entry_id}_lowBattery"
        assert low_battery_sensor.unique_id == expected_id

    def test_sensor_icon(self, low_battery_sensor):
        """Test binary sensor entity icon."""
        assert low_battery_sensor.icon == "mdi:battery-alert"

    def test_low_battery_sensor_below_threshold(
        self, low_battery_sensor, mock_coordinator
    ):
        """Test low battery sensor when battery is below threshold."""
        mock_coordinator.get_battery_optimization_status.return_value = {
            "battery_threshold": 20
        }

        # Mock battery level below threshold
        with patch.object(low_battery_sensor, "_is_low_battery", return_value=True):
            assert low_battery_sensor.is_on is True

    def test_low_battery_sensor_above_threshold(
        self, low_battery_sensor, mock_coordinator
    ):
        """Test low battery sensor when battery is above threshold."""
        mock_coordinator.get_battery_optimization_status.return_value = {
            "battery_threshold": 20
        }

        # Mock battery level above threshold
        with patch.object(low_battery_sensor, "_is_low_battery", return_value=False):
            assert low_battery_sensor.is_on is False

    def test_low_battery_sensor_coordinator_method_not_found(self, low_battery_sensor):
        """Test low battery sensor when coordinator method is not found."""
        # Remove the get_battery_optimization_status method from coordinator
        delattr(low_battery_sensor.coordinator, "get_battery_optimization_status")

        # Should return False when method not found
        assert low_battery_sensor.is_on is False

    def test_charging_sensor_true(self, charging_sensor):
        """Test charging sensor when device is charging."""
        with patch.object(charging_sensor, "_is_charging", return_value=True):
            assert charging_sensor.is_on is True

    def test_charging_sensor_false(self, charging_sensor):
        """Test charging sensor when device is not charging."""
        with patch.object(charging_sensor, "_is_charging", return_value=False):
            assert charging_sensor.is_on is False

    def test_power_saving_sensor_active(self, power_saving_sensor, mock_coordinator):
        """Test power saving sensor when power saving is active."""
        mock_coordinator.get_battery_optimization_status.return_value = {"active": True}

        assert power_saving_sensor.is_on is True

    def test_power_saving_sensor_inactive(self, power_saving_sensor, mock_coordinator):
        """Test power saving sensor when power saving is inactive."""
        mock_coordinator.get_battery_optimization_status.return_value = {
            "active": False
        }

        assert power_saving_sensor.is_on is False

    def test_power_saving_sensor_coordinator_method_not_found(
        self, power_saving_sensor
    ):
        """Test power saving sensor when coordinator method is not found."""
        # Remove the get_battery_optimization_status method from coordinator
        delattr(power_saving_sensor.coordinator, "get_battery_optimization_status")

        # Should return False when method not found
        assert power_saving_sensor.is_on is False

    def test_sleep_mode_sensor_active(self, sleep_mode_sensor, mock_coordinator):
        """Test sleep mode sensor when sleep mode is active."""
        mock_coordinator._is_sleep_mode_active.return_value = True

        assert sleep_mode_sensor.is_on is True

    def test_sleep_mode_sensor_inactive(self, sleep_mode_sensor, mock_coordinator):
        """Test sleep mode sensor when sleep mode is inactive."""
        mock_coordinator._is_sleep_mode_active.return_value = False

        assert sleep_mode_sensor.is_on is False

    def test_sleep_mode_sensor_coordinator_method_not_found(self, sleep_mode_sensor):
        """Test sleep mode sensor when coordinator method is not found."""
        # Remove the _is_sleep_mode_active method from coordinator
        delattr(sleep_mode_sensor.coordinator, "_is_sleep_mode_active")

        # Should return False when method not found
        assert sleep_mode_sensor.is_on is False

    def test_sensor_exception_handling(self, low_battery_sensor):
        """Test binary sensor exception handling."""
        # Mock _is_low_battery to raise exception
        with patch.object(
            low_battery_sensor, "_is_low_battery", side_effect=Exception("Test error")
        ):
            # Should handle exception gracefully and return False
            assert low_battery_sensor.is_on is False

    def test_sensor_available(self, low_battery_sensor):
        """Test binary sensor entity availability."""
        assert low_battery_sensor.available is True

    def test_sensor_available_device_offline(
        self, low_battery_sensor, mock_coordinator
    ):
        """Test binary sensor entity availability when device is offline."""
        mock_coordinator.device.get_status.return_value = False

        assert low_battery_sensor.available is False

    @pytest.mark.asyncio
    async def test_sensor_added_to_hass(self, low_battery_sensor):
        """Test binary sensor entity added to hass."""
        await low_battery_sensor.async_added_to_hass()
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_sensor_will_remove_from_hass(self, low_battery_sensor):
        """Test binary sensor entity will be removed from hass."""
        await low_battery_sensor.async_will_remove_from_hass()
        # Should not raise any exceptions

    def test_sensor_device_info(self, low_battery_sensor):
        """Test binary sensor entity device info."""
        device_info = low_battery_sensor.device_info

        assert device_info["identifiers"] == {
            ("imou_life", low_battery_sensor.config_entry.entry_id)
        }
        assert device_info["name"] == "Test Device"
        assert device_info["model"] == "Test Model"
        assert device_info["manufacturer"] == "Imou"
        assert device_info["sw_version"] == "1.0.0"
        assert device_info["hw_version"] == "test_device_123"

    def test_all_sensor_types(self, mock_coordinator, mock_config_entry):
        """Test all sensor types have correct properties."""
        sensor_configs = [
            ("lowBattery", "Low Battery", "mdi:battery-alert", "low_battery"),
            ("charging", "Charging", "mdi:battery-charging", "charging"),
            (
                "powerSavingActive",
                "Power Saving Active",
                "mdi:battery-saver",
                "power_saving_active",
            ),
            (
                "sleepModeActive",
                "Sleep Mode Active",
                "mdi:power-sleep",
                "sleep_mode_active",
            ),
        ]

        for sensor_type, description, icon, attribute_name in sensor_configs:
            sensor = ImouBatteryBinarySensor(
                mock_coordinator,
                mock_config_entry,
                sensor_type,
                description,
                icon,
                attribute_name,
            )

            assert sensor.sensor_type == sensor_type
            assert sensor._description == description
            assert sensor._icon == icon
            assert sensor._attribute_name == attribute_name
            assert sensor.name == f"Test Device {description}"

    def test_low_battery_threshold_calculation(
        self, low_battery_sensor, mock_coordinator
    ):
        """Test low battery threshold calculation logic."""
        mock_coordinator.get_battery_optimization_status.return_value = {
            "battery_threshold": 20
        }

        # Test with different battery levels
        with patch.object(low_battery_sensor, "_is_low_battery") as mock_method:
            # Battery level 15% (below threshold 20%)
            mock_method.return_value = True
            assert low_battery_sensor.is_on is True

            # Battery level 25% (above threshold 20%)
            mock_method.return_value = False
            assert low_battery_sensor.is_on is False

    def test_power_saving_status_retrieval(self, power_saving_sensor, mock_coordinator):
        """Test power saving status retrieval from coordinator."""
        # Test active status
        mock_coordinator.get_battery_optimization_status.return_value = {"active": True}
        assert power_saving_sensor.is_on is True

        # Test inactive status
        mock_coordinator.get_battery_optimization_status.return_value = {
            "active": False
        }
        assert power_saving_sensor.is_on is False

    def test_sleep_mode_status_retrieval(self, sleep_mode_sensor, mock_coordinator):
        """Test sleep mode status retrieval from coordinator."""
        # Test active status
        mock_coordinator._is_sleep_mode_active.return_value = True
        assert sleep_mode_sensor.is_on is True

        # Test inactive status
        mock_coordinator._is_sleep_mode_active.return_value = False
        assert sleep_mode_sensor.is_on is False

    def test_sensor_error_logging(self, low_battery_sensor):
        """Test that sensor errors are logged."""
        with patch(
            "custom_components.imou_life.battery_binary_sensor._LOGGER"
        ) as mock_logger:
            # Mock _is_low_battery to raise exception
            with patch.object(
                low_battery_sensor,
                "_is_low_battery",
                side_effect=Exception("Test error"),
            ):
                low_battery_sensor.is_on

                # Check that error message was logged
                mock_logger.error.assert_called_once()
                log_message = mock_logger.error.call_args[0][0]
                assert "Error getting binary sensor state" in log_message

    def test_sensor_availability_inheritance(
        self, low_battery_sensor, mock_coordinator
    ):
        """Test that sensor availability inherits from parent entity."""
        # Test when parent is available
        mock_coordinator.device.get_status.return_value = True
        assert low_battery_sensor.available is True

        # Test when parent is unavailable
        mock_coordinator.device.get_status.return_value = False
        assert low_battery_sensor.available is False

    def test_sensor_entity_registry_integration(self, low_battery_sensor):
        """Test that sensor integrates properly with entity registry."""
        # Test unique ID format
        assert low_battery_sensor.unique_id.startswith("test_entry_123_")
        assert low_battery_sensor.unique_id.endswith("lowBattery")

        # Test device info structure
        device_info = low_battery_sensor.device_info
        assert "identifiers" in device_info
        assert "name" in device_info
        assert "model" in device_info
        assert "manufacturer" in device_info
        assert "sw_version" in device_info
        assert "hw_version" in device_info
