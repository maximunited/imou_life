"""Tests for the Imou Life Binary Sensor platform."""
import pytest
from unittest.mock import MagicMock

from custom_components.imou_life.binary_sensor import ImouLifeBinarySensor
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouLifeBinarySensor:
    """Test the Imou Life Binary Sensor."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = {
            "device_info": {
                "device_id": "test_binary_123",
                "device_name": "Test Motion Sensor",
                "device_type": "binary_sensor"
            },
            "motion_detected": True,
            "door_open": False
        }
        return coordinator

    @pytest.fixture
    def motion_sensor(self, mock_coordinator):
        """Create a motion sensor instance."""
        return ImouLifeBinarySensor(mock_coordinator, MOCK_CONFIG_ENTRY, "motion")

    @pytest.fixture
    def door_sensor(self, mock_coordinator):
        """Create a door sensor instance."""
        return ImouLifeBinarySensor(mock_coordinator, MOCK_CONFIG_ENTRY, "door")

    def test_motion_sensor_name(self, motion_sensor):
        """Test motion sensor name property."""
        assert motion_sensor.name == "Test Motion Sensor Motion"

    def test_motion_sensor_unique_id(self, motion_sensor):
        """Test motion sensor unique ID."""
        assert motion_sensor.unique_id == "test_binary_123_motion"

    def test_motion_sensor_should_poll(self, motion_sensor):
        """Test motion sensor should_poll property."""
        assert motion_sensor.should_poll is False

    def test_motion_sensor_is_on(self, motion_sensor):
        """Test motion sensor is_on property."""
        assert motion_sensor.is_on is True

    def test_door_sensor_is_on(self, door_sensor):
        """Test door sensor is_on property."""
        assert door_sensor.is_on is False

    def test_motion_sensor_device_class(self, motion_sensor):
        """Test motion sensor device class."""
        assert motion_sensor.device_class == "motion"

    def test_door_sensor_device_class(self, door_sensor):
        """Test door sensor device class."""
        assert door_sensor.device_class == "door"

    def test_motion_sensor_icon(self, motion_sensor):
        """Test motion sensor icon."""
        assert motion_sensor.icon == "mdi:motion-sensor"

    def test_door_sensor_icon(self, door_sensor):
        """Test door sensor icon."""
        assert door_sensor.icon == "mdi:door-open"

    def test_motion_sensor_available(self, motion_sensor):
        """Test motion sensor available property."""
        assert motion_sensor.available is True

    def test_motion_sensor_device_info(self, motion_sensor):
        """Test motion sensor device info."""
        device_info = motion_sensor.device_info
        assert device_info["identifiers"] == {("imou_life", "test_binary_123")}
        assert device_info["name"] == "Test Motion Sensor"
        assert device_info["manufacturer"] == "Imou"

    def test_motion_sensor_entity_category(self, motion_sensor):
        """Test motion sensor entity category."""
        assert motion_sensor.entity_category is None

    def test_motion_sensor_extra_state_attributes(self, motion_sensor):
        """Test motion sensor extra state attributes."""
        attrs = motion_sensor.extra_state_attributes
        assert "last_update" in attrs
        assert "device_type" in attrs
        assert attrs["device_type"] == "binary_sensor"

    def test_motion_sensor_state_attributes(self, motion_sensor):
        """Test motion sensor state attributes."""
        attrs = motion_sensor.state_attributes
        assert "last_update" in attrs
        assert "device_type" in attrs
        assert attrs["device_type"] == "binary_sensor"
