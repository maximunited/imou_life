"""Tests for the Imou Life Siren platform."""
import pytest
from unittest.mock import MagicMock, patch

from custom_components.imou_life.siren import ImouLifeSiren
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouLifeSiren:
    """Test the Imou Life Siren."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = {
            "device_info": {
                "device_id": "test_siren_123",
                "device_name": "Test Siren",
                "device_type": "siren"
            },
            "siren_on": False
        }
        return coordinator

    @pytest.fixture
    def siren(self, mock_coordinator):
        """Create a siren instance."""
        return ImouLifeSiren(mock_coordinator, MOCK_CONFIG_ENTRY)

    def test_siren_name(self, siren):
        """Test siren name property."""
        assert siren.name == "Test Siren"

    def test_siren_unique_id(self, siren):
        """Test siren unique ID."""
        assert siren.unique_id == "test_siren_123"

    def test_siren_should_poll(self, siren):
        """Test siren should_poll property."""
        assert siren.should_poll is False

    def test_siren_is_on(self, siren):
        """Test siren is_on property."""
        assert siren.is_on is False

    def test_siren_icon(self, siren):
        """Test siren icon."""
        assert siren.icon == "mdi:alarm-light"

    def test_siren_available(self, siren):
        """Test siren available property."""
        assert siren.available is True

    @pytest.mark.asyncio
    async def test_siren_turn_on(self, siren):
        """Test siren turn on."""
        with patch.object(siren, '_turn_on') as mock_on:
            await siren.async_turn_on()
            mock_on.assert_called_once()

    @pytest.mark.asyncio
    async def test_siren_turn_off(self, siren):
        """Test siren turn off."""
        with patch.object(siren, '_turn_off') as mock_off:
            await siren.async_turn_off()
            mock_off.assert_called_once()

    def test_siren_device_info(self, siren):
        """Test siren device info."""
        device_info = siren.device_info
        assert device_info["identifiers"] == {("imou_life", "test_siren_123")}
        assert device_info["name"] == "Test Siren"
        assert device_info["manufacturer"] == "Imou"
