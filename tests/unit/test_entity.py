"""Tests for the Imou Life Entity base class."""
import pytest
from unittest.mock import MagicMock

from custom_components.imou_life.entity import ImouLifeEntity
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouLifeEntity:
    """Test the Imou Life Entity base class."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = {
            "device_info": {
                "device_id": "test_entity_123",
                "device_name": "Test Entity",
                "device_type": "entity"
            }
        }
        return coordinator

    @pytest.fixture
    def entity(self, mock_coordinator):
        """Create an entity instance."""
        return ImouLifeEntity(mock_coordinator, MOCK_CONFIG_ENTRY)

    def test_entity_initialization(self, entity):
        """Test entity initialization."""
        assert entity.coordinator is not None
        assert entity.config_entry == MOCK_CONFIG_ENTRY

    def test_entity_name(self, entity):
        """Test entity name property."""
        assert entity.name == "Test Entity"

    def test_entity_unique_id(self, entity):
        """Test entity unique ID."""
        assert entity.unique_id == "test_entity_123"

    def test_entity_should_poll(self, entity):
        """Test entity should_poll property."""
        assert entity.should_poll is False

    def test_entity_available(self, entity):
        """Test entity available property."""
        assert entity.available is True

    def test_entity_device_info(self, entity):
        """Test entity device info."""
        device_info = entity.device_info
        assert device_info["identifiers"] == {("imou_life", "test_entity_123")}
        assert device_info["name"] == "Test Entity"
        assert device_info["manufacturer"] == "Imou"

    def test_entity_extra_state_attributes(self, entity):
        """Test entity extra state attributes."""
        attrs = entity.extra_state_attributes
        assert "last_update" in attrs
        assert "device_type" in attrs
        assert attrs["device_type"] == "entity"

    def test_entity_state_attributes(self, entity):
        """Test entity state attributes."""
        attrs = entity.state_attributes
        assert "last_update" in attrs
        assert "device_type" in attrs
        assert attrs["device_type"] == "entity"

    def test_entity_has_entity_name(self, entity):
        """Test entity has_entity_name property."""
        assert entity.has_entity_name is True

    def test_entity_translation_key(self, entity):
        """Test entity translation key."""
        assert entity.translation_key == "imou_life"

    def test_entity_entity_id(self, entity):
        """Test entity entity ID."""
        # This will be None until the entity is added to Home Assistant
        assert entity.entity_id is None

    def test_entity_platform(self, entity):
        """Test entity platform."""
        # This will be None until the entity is added to Home Assistant
        assert entity.platform is None

    def test_entity_hass(self, entity):
        """Test entity hass property."""
        # This will be None until the entity is added to Home Assistant
        assert entity.hass is None

    def test_entity_icon(self, entity):
        """Test entity icon property."""
        # Base entity doesn't have a default icon
        assert entity.icon is None

    def test_entity_entity_picture(self, entity):
        """Test entity entity picture."""
        # Base entity doesn't have a default picture
        assert entity.entity_picture is None

    def test_entity_assumed_state(self, entity):
        """Test entity assumed state."""
        assert entity.assumed_state is False

    def test_entity_force_update(self, entity):
        """Test entity force update."""
        assert entity.force_update is False

    def test_entity_context(self, entity):
        """Test entity context."""
        context = entity.context
        assert context is not None
        assert hasattr(context, 'id')
        assert hasattr(context, 'parent_id')
        assert hasattr(context, 'user_id')
