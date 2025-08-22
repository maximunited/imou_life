"""Tests for the Imou Life Siren platform."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.imou_life.siren import ImouSiren
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouSiren:
    """Test the Imou Life Siren."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Siren"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_siren_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = MagicMock()
        return coordinator

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "siren"
        sensor.get_description.return_value = "Siren"
        sensor.is_on.return_value = False
        sensor.get_attributes.return_value = {"last_update": "2023-01-01T00:00:00Z"}
        sensor.async_turn_on = MagicMock()
        sensor.async_turn_off = MagicMock()
        sensor.async_toggle = MagicMock()
        return sensor

    @pytest.fixture
    def siren(self, mock_coordinator, mock_sensor_instance):
        """Create a siren instance."""
        return ImouSiren(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "siren.{}"
        )

    def test_siren_name(self, siren):
        """Test siren name property."""
        assert siren.name == "Test Siren Siren"

    def test_siren_unique_id(self, siren):
        """Test siren unique ID."""
        assert siren.unique_id == f"{MOCK_CONFIG_ENTRY.entry_id}_siren"

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
        with patch.object(siren, "async_write_ha_state") as mock_write:
            await siren.async_turn_on()
            siren._sensor_instance.async_turn_on.assert_called_once()
            mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_siren_turn_off(self, siren):
        """Test siren turn off."""
        with patch.object(siren, "async_write_ha_state") as mock_write:
            await siren.async_turn_off()
            siren._sensor_instance.async_turn_off.assert_called_once()
            mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_siren_toggle(self, siren):
        """Test siren toggle."""
        with patch.object(siren, "async_write_ha_state") as mock_write:
            await siren.async_toggle()
            siren._sensor_instance.async_toggle.assert_called_once()
            mock_write.assert_called_once()

    def test_siren_device_info(self, siren):
        """Test siren device info."""
        device_info = siren.device_info
        assert device_info["identifiers"] == {("imou_life", MOCK_CONFIG_ENTRY.entry_id)}
        assert device_info["name"] == "Test Siren"
        assert device_info["manufacturer"] == "Imou"

    def test_siren_extra_state_attributes(self, siren):
        """Test siren extra state attributes."""
        attrs = siren.extra_state_attributes
        assert "last_update" in attrs
        assert attrs["last_update"] == "2023-01-01T00:00:00Z"

    def test_siren_supported_features(self, siren):
        """Test siren supported features."""
        from homeassistant.components.siren import SirenEntityFeature

        expected_features = SirenEntityFeature.TURN_OFF | SirenEntityFeature.TURN_ON
        assert siren._attr_supported_features == expected_features
