"""Tests for the Imou Life Entity base class."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.imou_life.entity import ImouEntity
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouEntity:
    """Test the Imou Life Entity base class."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Entity"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_entity_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = MagicMock()
        return coordinator

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "testSensor"
        sensor.get_description.return_value = "Test"
        sensor.get_attributes.return_value = {"last_update": "2023-01-01T00:00:00Z"}
        sensor.set_enabled = MagicMock()
        sensor.async_update = AsyncMock()
        return sensor

    @pytest.fixture
    def entity(self, mock_coordinator, mock_sensor_instance):
        """Create an entity instance."""
        return ImouEntity(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "test.{}"
        )

    def test_entity_initialization(self, entity):
        """Test entity initialization."""
        assert entity.coordinator is not None
        assert entity.config_entry == MOCK_CONFIG_ENTRY
        assert entity.device is not None
        assert entity.sensor_instance is not None

    def test_entity_name(self, entity):
        """Test entity name property."""
        # With has_entity_name=True, name is just the sensor description
        assert entity.name == "Test"

    def test_entity_unique_id(self, entity):
        """Test entity unique ID."""
        assert entity.unique_id == f"{MOCK_CONFIG_ENTRY.entry_id}_testSensor"

    def test_entity_should_poll(self, entity):
        """Test entity should_poll property."""
        assert entity.should_poll is False

    def test_entity_available(self, entity):
        """Test entity available property."""
        assert entity.available is True

    def test_entity_device_info(self, entity):
        """Test entity device info."""
        device_info = entity.device_info
        assert device_info["identifiers"] == {("imou_life", MOCK_CONFIG_ENTRY.entry_id)}
        assert device_info["name"] == "Test Entity"
        assert device_info["manufacturer"] == "Imou"
        assert device_info["model"] == "Test Model"
        assert device_info["sw_version"] == "1.0.0"
        assert device_info["hw_version"] == "test_entity_123"

    def test_entity_extra_state_attributes(self, entity):
        """Test entity extra state attributes."""
        attrs = entity.extra_state_attributes
        assert "last_update" in attrs
        assert attrs["last_update"] == "2023-01-01T00:00:00Z"

    def test_entity_icon(self, entity):
        """Test entity icon property."""
        # Icon comes from SENSOR_ICONS based on sensor name
        assert entity.icon is not None

    @pytest.mark.asyncio
    async def test_entity_async_added_to_hass(self, entity):
        """Test entity added to hass."""
        await entity.async_added_to_hass()
        entity.sensor_instance.set_enabled.assert_called_once_with(True)
        entity.sensor_instance.async_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_entity_async_will_remove_from_hass(self, entity):
        """Test entity removed from hass."""
        await entity.async_will_remove_from_hass()
        entity.sensor_instance.set_enabled.assert_called_once_with(False)

    def test_entity_availability_logging_on_unavailable(self, entity, mock_coordinator):
        """Test that entity logs warning when becoming unavailable."""
        # Initially available
        mock_coordinator.device.get_status.return_value = True
        assert entity.available is True

        # Become unavailable - should log warning
        mock_coordinator.device.get_status.return_value = False
        with patch("custom_components.imou_life.entity._LOGGER") as mock_logger:
            assert entity.available is False
            # Check that warning was logged
            mock_logger.warning.assert_called_once()
            log_message = mock_logger.warning.call_args[0][0]
            assert "became unavailable" in log_message

    def test_entity_availability_no_logging_when_staying_unavailable(
        self, entity, mock_coordinator
    ):
        """Test that entity doesn't log when staying unavailable."""
        # Initially unavailable
        mock_coordinator.device.get_status.return_value = False
        assert entity.available is False

        # Stay unavailable - should not log
        with patch("custom_components.imou_life.entity._LOGGER") as mock_logger:
            assert entity.available is False
            mock_logger.warning.assert_not_called()

    def test_entity_availability_no_logging_when_becoming_available(
        self, entity, mock_coordinator
    ):
        """Test that entity doesn't log when becoming available."""
        # Initially unavailable
        mock_coordinator.device.get_status.return_value = False
        assert entity.available is False

        # Become available - should not log
        mock_coordinator.device.get_status.return_value = True
        with patch("custom_components.imou_life.entity._LOGGER") as mock_logger:
            assert entity.available is True
            mock_logger.warning.assert_not_called()
