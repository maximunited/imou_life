"""Tests for the Imou Life Sensor platform."""

from unittest.mock import MagicMock

import pytest

from custom_components.imou_life.sensor import ImouSensor
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouSensor:
    """Test the Imou Life Sensor."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Sensor"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_sensor_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = MagicMock()
        return coordinator

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "battery"
        sensor.get_description.return_value = "Battery"
        sensor.get_state.return_value = 85
        sensor.get_attributes.return_value = {"last_update": "2023-01-01T00:00:00Z"}
        return sensor

    @pytest.fixture
    def sensor(self, mock_coordinator, mock_sensor_instance):
        """Create a sensor instance."""
        return ImouSensor(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "sensor.{}"
        )

    def test_sensor_name(self, sensor):
        """Test sensor name property."""
        assert sensor.name == "Test Sensor Battery"

    def test_sensor_unique_id(self, sensor):
        """Test sensor unique ID."""
        assert sensor.unique_id == f"{MOCK_CONFIG_ENTRY.entry_id}_battery"

    def test_sensor_should_poll(self, sensor):
        """Test sensor should_poll property."""
        assert sensor.should_poll is False

    def test_sensor_state(self, sensor):
        """Test sensor state property."""
        assert sensor.state == 85

    def test_sensor_unit_of_measurement(self, sensor):
        """Test sensor unit of measurement."""
        assert sensor.unit_of_measurement == "%"

    def test_sensor_device_class(self, sensor):
        """Test sensor device class."""
        assert sensor.device_class is None

    def test_sensor_icon(self, sensor):
        """Test sensor icon."""
        assert sensor.icon == "mdi:battery"

    def test_sensor_available(self, sensor):
        """Test sensor available property."""
        assert sensor.available is True

    def test_sensor_device_info(self, sensor):
        """Test sensor device info."""
        device_info = sensor.device_info
        assert device_info["identifiers"] == {("imou_life", MOCK_CONFIG_ENTRY.entry_id)}
        assert device_info["name"] == "Test Sensor"
        assert device_info["manufacturer"] == "Imou"

    def test_sensor_extra_state_attributes(self, sensor):
        """Test sensor extra state attributes."""
        attrs = sensor.extra_state_attributes
        assert "last_update" in attrs
        assert attrs["last_update"] == "2023-01-01T00:00:00Z"

    def test_sensor_timestamp_device_class(self, mock_coordinator):
        """Test sensor with timestamp device class."""
        mock_sensor = MagicMock()
        mock_sensor.get_name.return_value = "lastAlarm"
        mock_sensor.get_description.return_value = "Last Alarm"
        mock_sensor.get_state.return_value = "2023-01-01T00:00:00Z"
        mock_sensor.get_attributes.return_value = {}

        sensor = ImouSensor(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor, "sensor.{}"
        )
        assert sensor.device_class == "timestamp"

    def test_sensor_storage_unit(self, mock_coordinator):
        """Test sensor with storage unit."""
        mock_sensor = MagicMock()
        mock_sensor.get_name.return_value = "storageUsed"
        mock_sensor.get_description.return_value = "Storage Used"
        mock_sensor.get_state.return_value = 75
        mock_sensor.get_attributes.return_value = {}

        sensor = ImouSensor(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor, "sensor.{}"
        )
        assert sensor.unit_of_measurement == "%"
