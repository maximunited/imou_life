"""Tests for the Imou Life Binary Sensor platform."""
from unittest.mock import MagicMock

import pytest

from custom_components.imou_life.binary_sensor import ImouBinarySensor
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouBinarySensor:
    """Test the Imou Life Binary Sensor."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Motion Sensor"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_binary_123"
        coordinator.device.get_status.return_value = True
        return coordinator

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "motionAlarm"
        sensor.get_description.return_value = "Motion"
        sensor.is_on.return_value = True
        sensor.get_attributes.return_value = {"last_update": "2023-01-01T00:00:00Z"}
        return sensor

    @pytest.fixture
    def binary_sensor(self, mock_coordinator, mock_sensor_instance):
        """Create a binary sensor instance."""
        return ImouBinarySensor(
            mock_coordinator,
            MOCK_CONFIG_ENTRY,
            mock_sensor_instance,
            "binary_sensor.{}",
        )

    def test_binary_sensor_name(self, binary_sensor):
        """Test binary sensor name property."""
        assert binary_sensor.name == "Test Motion Sensor Motion"

    def test_binary_sensor_unique_id(self, binary_sensor):
        """Test binary sensor unique ID."""
        assert binary_sensor.unique_id == f"{MOCK_CONFIG_ENTRY.entry_id}_motionAlarm"

    def test_binary_sensor_should_poll(self, binary_sensor):
        """Test binary sensor should_poll property."""
        assert binary_sensor.should_poll is False

    def test_binary_sensor_is_on(self, binary_sensor):
        """Test binary sensor is_on property."""
        assert binary_sensor.is_on is True

    def test_binary_sensor_device_class(self, binary_sensor):
        """Test binary sensor device class."""
        assert binary_sensor.device_class == "motion"

    def test_binary_sensor_icon(self, binary_sensor):
        """Test binary sensor icon."""
        assert binary_sensor.icon == "mdi:motion-sensor"

    def test_binary_sensor_available(self, binary_sensor):
        """Test binary sensor available property."""
        assert binary_sensor.available is True

    def test_binary_sensor_device_info(self, binary_sensor):
        """Test binary sensor device info."""
        device_info = binary_sensor.device_info
        assert device_info["identifiers"] == {("imou_life", MOCK_CONFIG_ENTRY.entry_id)}
        assert device_info["name"] == "Test Motion Sensor"
        assert device_info["manufacturer"] == "Imou"

    def test_binary_sensor_extra_state_attributes(self, binary_sensor):
        """Test binary sensor extra state attributes."""
        attrs = binary_sensor.extra_state_attributes
        assert "last_update" in attrs
        assert attrs["last_update"] == "2023-01-01T00:00:00Z"
