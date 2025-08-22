"""Tests for the Imou Life Entity base class."""

from unittest.mock import AsyncMock, MagicMock

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
        assert entity.name == "Test Entity Test"

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
