"""Tests for the Imou Life Select platform."""
import pytest
from unittest.mock import MagicMock, patch

from custom_components.imou_life.select import ImouLifeSelect
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouLifeSelect:
    """Test the Imou Life Select."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = {
            "device_info": {
                "device_id": "test_select_123",
                "device_name": "Test Select",
                "device_type": "select"
            },
            "current_option": "option1"
        }
        return coordinator

    @pytest.fixture
    def select(self, mock_coordinator):
        """Create a select instance."""
        return ImouLifeSelect(mock_coordinator, MOCK_CONFIG_ENTRY, "mode")

    def test_select_name(self, select):
        """Test select name property."""
        assert select.name == "Test Select Mode"

    def test_select_unique_id(self, select):
        """Test select unique ID."""
        assert select.unique_id == "test_select_123_mode"

    def test_select_should_poll(self, select):
        """Test select should_poll property."""
        assert select.should_poll is False

    def test_select_current_option(self, select):
        """Test select current option."""
        assert select.current_option == "option1"

    def test_select_options(self, select):
        """Test select options."""
        options = select.options
        assert "option1" in options
        assert "option2" in options
        assert "option3" in options

    def test_select_icon(self, select):
        """Test select icon."""
        assert select.icon == "mdi:format-list-bulleted"

    def test_select_available(self, select):
        """Test select available property."""
        assert select.available is True

    @pytest.mark.asyncio
    async def test_select_select_option(self, select):
        """Test select option selection."""
        with patch.object(select, '_select_option') as mock_select:
            await select.async_select_option("option2")
            mock_select.assert_called_once_with("option2")

    def test_select_device_info(self, select):
        """Test select device info."""
        device_info = select.device_info
        assert device_info["identifiers"] == {("imou_life", "test_select_123")}
        assert device_info["name"] == "Test Select"
        assert device_info["manufacturer"] == "Imou"
