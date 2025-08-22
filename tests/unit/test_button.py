"""Tests for the Imou Life Button platform."""
import pytest
from unittest.mock import MagicMock, patch

from custom_components.imou_life.button import ImouLifeButton
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouLifeButton:
    """Test the Imou Life Button."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = {
            "device_info": {
                "device_id": "test_button_123",
                "device_name": "Test Button",
                "device_type": "button"
            }
        }
        return coordinator

    @pytest.fixture
    def button(self, mock_coordinator):
        """Create a button instance."""
        return ImouLifeButton(mock_coordinator, MOCK_CONFIG_ENTRY, "restart")

    def test_button_name(self, button):
        """Test button name property."""
        assert button.name == "Test Button Restart"

    def test_button_unique_id(self, button):
        """Test button unique ID."""
        assert button.unique_id == "test_button_123_restart"

    def test_button_should_poll(self, button):
        """Test button should_poll property."""
        assert button.should_poll is False

    def test_button_icon(self, button):
        """Test button icon."""
        assert button.icon == "mdi:restart"

    def test_button_device_class(self, button):
        """Test button device class."""
        assert button.device_class == "restart"

    def test_button_available(self, button):
        """Test button available property."""
        assert button.available is True

    @pytest.mark.asyncio
    async def test_button_press(self, button):
        """Test button press functionality."""
        with patch.object(button, '_press_button') as mock_press:
            await button.async_press()
            mock_press.assert_called_once()

    def test_button_device_info(self, button):
        """Test button device info."""
        device_info = button.device_info
        assert device_info["identifiers"] == {("imou_life", "test_button_123")}
        assert device_info["name"] == "Test Button"
        assert device_info["manufacturer"] == "Imou"
