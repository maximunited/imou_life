"""Tests for entity mixins."""

from unittest.mock import MagicMock, patch

from custom_components.imou_life.entity_mixins import (
    DeviceClassMixin,
    StateUpdateMixin,
)


class TestDeviceClassMixin:
    """Test the DeviceClassMixin."""

    def test_get_device_class_by_name_found(self):
        """Test getting device class when mapping exists."""
        mixin = DeviceClassMixin()
        class_mapping = {
            "restartDevice": "restart",
            "motionDetect": "motion",
        }

        assert (
            mixin._get_device_class_by_name("restartDevice", class_mapping) == "restart"
        )
        assert (
            mixin._get_device_class_by_name("motionDetect", class_mapping) == "motion"
        )

    def test_get_device_class_by_name_not_found(self):
        """Test getting device class when mapping doesn't exist."""
        mixin = DeviceClassMixin()
        class_mapping = {"restartDevice": "restart"}

        assert mixin._get_device_class_by_name("unknownSensor", class_mapping) is None

    def test_get_device_class_by_name_empty_mapping(self):
        """Test getting device class with empty mapping."""
        mixin = DeviceClassMixin()
        class_mapping = {}

        assert mixin._get_device_class_by_name("anySensor", class_mapping) is None


class TestStateUpdateMixin:
    """Test the StateUpdateMixin."""

    @patch("custom_components.imou_life.entity_mixins._LOGGER")
    def test_update_ha_state(self, mock_logger):
        """Test updating HA state with logging."""

        # Create a mock object that has both the mixin and required attributes
        class MockEntity(StateUpdateMixin):
            def __init__(self):
                self.device = MagicMock()
                self.device.get_name.return_value = "Test Device"
                self.sensor_instance = MagicMock()
                self.sensor_instance.get_description.return_value = "Test Sensor"
                self.async_write_ha_state = MagicMock()

        entity = MockEntity()
        entity._update_ha_state()

        # Verify async_write_ha_state was called
        entity.async_write_ha_state.assert_called_once()

        # Verify debug logging was called (covers lines 33-37)
        mock_logger.debug.assert_called_once()
        args = mock_logger.debug.call_args[0]
        # args[0] is the format string, args[1] and args[2] are the parameters
        assert args[0] == "[%s] Updated state for %s"
        assert args[1] == "Test Device"
        assert args[2] == "Test Sensor"

    @patch("custom_components.imou_life.entity_mixins._LOGGER")
    def test_update_ha_state_with_different_names(self, mock_logger):
        """Test updating HA state with different device/sensor names."""

        class MockEntity(StateUpdateMixin):
            def __init__(self, device_name, sensor_desc):
                self.device = MagicMock()
                self.device.get_name.return_value = device_name
                self.sensor_instance = MagicMock()
                self.sensor_instance.get_description.return_value = sensor_desc
                self.async_write_ha_state = MagicMock()

        entity = MockEntity("Camera 1", "Battery Level")
        entity._update_ha_state()

        entity.async_write_ha_state.assert_called_once()
        mock_logger.debug.assert_called_once()
        args = mock_logger.debug.call_args[0]
        assert "Camera 1" in args[1]
        assert "Battery Level" in args[2]
