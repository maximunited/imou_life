"""Tests for the Imou Life Sensor platform."""
import pytest
from unittest.mock import MagicMock

from custom_components.imou_life.sensor import ImouLifeSensor
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouLifeSensor:
    """Test the Imou Life Sensor."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = {
            "device_info": {
                "device_id": "test_sensor_123",
                "device_name": "Test Sensor",
                "device_type": "sensor"
            },
            "sensor_data": {
                "temperature": 25.5,
                "humidity": 60.0,
                "battery": 85
            }
        }
        return coordinator

    @pytest.fixture
    def sensor(self, mock_coordinator):
        """Create a sensor instance."""
        return ImouLifeSensor(mock_coordinator, MOCK_CONFIG_ENTRY, "temperature")

    def test_sensor_name(self, sensor):
        """Test sensor name property."""
        assert sensor.name == "Test Sensor Temperature"

    def test_sensor_unique_id(self, sensor):
        """Test sensor unique ID."""
        assert sensor.unique_id == "test_sensor_123_temperature"

    def test_sensor_should_poll(self, sensor):
        """Test sensor should_poll property."""
        assert sensor.should_poll is False

    def test_sensor_native_value(self, sensor):
        """Test sensor native value."""
        assert sensor.native_value == 25.5

    def test_sensor_native_unit_of_measurement(self, sensor):
        """Test sensor native unit of measurement."""
        assert sensor.native_unit_of_measurement == "°C"

    def test_sensor_device_class(self, sensor):
        """Test sensor device class."""
        assert sensor.device_class == "temperature"

    def test_sensor_state_class(self, sensor):
        """Test sensor state class."""
        assert sensor.state_class == "measurement"

    def test_sensor_icon(self, sensor):
        """Test sensor icon."""
        assert sensor.icon == "mdi:thermometer"

    def test_sensor_available(self, sensor):
        """Test sensor available property."""
        assert sensor.available is True

    def test_sensor_device_info(self, sensor):
        """Test sensor device info."""
        device_info = sensor.device_info
        assert device_info["identifiers"] == {("imou_life", "test_sensor_123")}
        assert device_info["name"] == "Test Sensor"
        assert device_info["manufacturer"] == "Imou"

    def test_sensor_entity_category(self, sensor):
        """Test sensor entity category."""
        assert sensor.entity_category is None

    def test_sensor_extra_state_attributes(self, sensor):
        """Test sensor extra state attributes."""
        attrs = sensor.extra_state_attributes
        assert "last_update" in attrs
        assert "device_type" in attrs
        assert attrs["device_type"] == "sensor"
