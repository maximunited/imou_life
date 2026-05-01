"""Comprehensive unit tests for Imou switch entities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.imou_life.const import ENABLED_SWITCHES, OPTION_CALLBACK_URL
from custom_components.imou_life.switch import ImouSwitch


class TestImouSwitch:
    """Test ImouSwitch class."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.device.get_model.return_value = "IPC-TestModel"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_device_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = MagicMock()
        return coordinator

    @pytest.fixture
    def mock_config_entry(self):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry_123"
        config_entry.options = {OPTION_CALLBACK_URL: "https://example.com/callback"}
        return config_entry

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "motionDetect"
        sensor.get_description.return_value = "Motion Detection"
        sensor.get_attributes.return_value = {"enabled": True}
        sensor.is_on.return_value = True
        sensor.async_turn_on = AsyncMock()
        sensor.async_turn_off = AsyncMock()
        sensor.async_toggle = AsyncMock()
        return sensor

    @pytest.fixture
    def switch_entity(self, mock_coordinator, mock_config_entry, mock_sensor_instance):
        """Create a switch entity."""
        return ImouSwitch(
            mock_coordinator,
            mock_config_entry,
            mock_sensor_instance,
            "switch.{}",
        )

    def test_switch_initialization(self, switch_entity):
        """Test switch initialization."""
        assert switch_entity.coordinator is not None
        assert switch_entity.config_entry is not None
        assert switch_entity.sensor_instance is not None

    def test_switch_is_on_true(self, switch_entity, mock_sensor_instance):
        """Test switch is_on property when on."""
        mock_sensor_instance.is_on.return_value = True
        assert switch_entity.is_on is True

    def test_switch_is_on_false(self, switch_entity, mock_sensor_instance):
        """Test switch is_on property when off."""
        mock_sensor_instance.is_on.return_value = False
        assert switch_entity.is_on is False

    def test_switch_entity_registry_enabled_default_true(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Test switch enabled by default for switches in ENABLED_SWITCHES."""
        # Set sensor name to one that's enabled by default
        mock_sensor_instance.get_name.return_value = next(iter(ENABLED_SWITCHES))
        switch = ImouSwitch(
            mock_coordinator,
            mock_config_entry,
            mock_sensor_instance,
            "switch.{}",
        )
        assert switch.entity_registry_enabled_default is True

    def test_switch_entity_registry_enabled_default_false(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Test switch disabled by default for other switches."""
        mock_sensor_instance.get_name.return_value = "unknown_switch"
        switch = ImouSwitch(
            mock_coordinator,
            mock_config_entry,
            mock_sensor_instance,
            "switch.{}",
        )
        assert switch.entity_registry_enabled_default is False

    @pytest.mark.asyncio
    async def test_switch_async_turn_on_normal_switch(
        self, switch_entity, mock_sensor_instance
    ):
        """Test turning on a normal switch."""
        mock_sensor_instance.get_name.return_value = "motionDetect"
        mock_sensor_instance.async_turn_on = AsyncMock()

        with patch.object(switch_entity, "async_write_ha_state"):
            await switch_entity.async_turn_on()

        mock_sensor_instance.async_turn_on.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_switch_async_turn_on_push_notifications(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Test turning on push notifications switch with callback URL."""
        mock_sensor_instance.get_name.return_value = "pushNotifications"
        mock_sensor_instance.async_turn_on = AsyncMock()
        mock_config_entry.options = {
            OPTION_CALLBACK_URL: "https://callback.example.com"
        }

        switch = ImouSwitch(
            mock_coordinator,
            mock_config_entry,
            mock_sensor_instance,
            "switch.{}",
        )

        with patch.object(switch, "async_write_ha_state"):
            await switch.async_turn_on()

        mock_sensor_instance.async_turn_on.assert_called_once_with(
            url="https://callback.example.com"
        )

    @pytest.mark.asyncio
    async def test_switch_async_turn_on_push_notifications_no_url(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Test turning on push notifications without callback URL raises error."""
        mock_sensor_instance.get_name.return_value = "pushNotifications"
        mock_config_entry.options = {OPTION_CALLBACK_URL: ""}

        switch = ImouSwitch(
            mock_coordinator,
            mock_config_entry,
            mock_sensor_instance,
            "switch.{}",
        )

        with pytest.raises(ValueError, match="No callback URL provided"):
            await switch.async_turn_on()

    @pytest.mark.asyncio
    async def test_switch_async_turn_on_push_notifications_missing_option(
        self, mock_coordinator, mock_config_entry, mock_sensor_instance
    ):
        """Test push notifications without callback URL option."""
        mock_sensor_instance.get_name.return_value = "pushNotifications"
        mock_config_entry.options = {}

        switch = ImouSwitch(
            mock_coordinator,
            mock_config_entry,
            mock_sensor_instance,
            "switch.{}",
        )

        with pytest.raises(ValueError, match="No callback URL provided"):
            await switch.async_turn_on()

    @pytest.mark.asyncio
    async def test_switch_async_turn_off(self, switch_entity, mock_sensor_instance):
        """Test turning off switch."""
        mock_sensor_instance.async_turn_off = AsyncMock()

        with patch.object(switch_entity, "async_write_ha_state"):
            await switch_entity.async_turn_off()

        mock_sensor_instance.async_turn_off.assert_called_once()

    @pytest.mark.asyncio
    async def test_switch_async_toggle(self, switch_entity, mock_sensor_instance):
        """Test toggling switch."""
        mock_sensor_instance.async_toggle = AsyncMock()

        with patch.object(switch_entity, "async_write_ha_state"):
            await switch_entity.async_toggle()

        mock_sensor_instance.async_toggle.assert_called_once()

    def test_switch_name(self, switch_entity):
        """Test switch name."""
        assert switch_entity.name == "Motion Detection"

    def test_switch_unique_id(self, switch_entity, mock_config_entry):
        """Test switch unique ID."""
        expected_id = f"{mock_config_entry.entry_id}_motionDetect"
        assert switch_entity.unique_id == expected_id

    def test_switch_device_info(self, switch_entity):
        """Test switch device info."""
        device_info = switch_entity.device_info

        assert device_info["identifiers"] == {
            ("imou_life", switch_entity.config_entry.entry_id)
        }
        assert device_info["name"] == "Test Camera"
        assert device_info["model"] == "IPC-TestModel"
        assert device_info["manufacturer"] == "Imou"
        assert device_info["sw_version"] == "1.0.0"
        assert device_info["hw_version"] == "test_device_123"

    def test_switch_extra_state_attributes(self, switch_entity):
        """Test switch extra state attributes."""
        attrs = switch_entity.extra_state_attributes
        assert "enabled" in attrs
        assert attrs["enabled"] is True

    @pytest.mark.asyncio
    async def test_switch_async_turn_on_writes_state(self, switch_entity):
        """Test that turn_on writes state to HA."""
        with patch.object(switch_entity, "async_write_ha_state") as mock_write:
            await switch_entity.async_turn_on()
            mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_switch_async_turn_off_writes_state(self, switch_entity):
        """Test that turn_off writes state to HA."""
        with patch.object(switch_entity, "async_write_ha_state") as mock_write:
            await switch_entity.async_turn_off()
            mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_switch_async_toggle_writes_state(self, switch_entity):
        """Test that toggle writes state to HA."""
        with patch.object(switch_entity, "async_write_ha_state") as mock_write:
            await switch_entity.async_toggle()
            mock_write.assert_called_once()

    def test_switch_available(self, switch_entity):
        """Test switch availability."""
        assert switch_entity.available is True

    def test_switch_available_device_offline(self, switch_entity, mock_coordinator):
        """Test switch unavailable when device offline."""
        mock_coordinator.device.get_status.return_value = False
        assert switch_entity.available is False

    @pytest.mark.asyncio
    async def test_all_enabled_switches_enabled_by_default(
        self, mock_coordinator, mock_config_entry
    ):
        """Test that all ENABLED_SWITCHES are enabled by default."""
        for switch_name in ENABLED_SWITCHES:
            sensor = MagicMock()
            sensor.get_name.return_value = switch_name
            sensor.get_description.return_value = f"{switch_name} Description"
            sensor.get_attributes.return_value = {}

            switch = ImouSwitch(
                mock_coordinator,
                mock_config_entry,
                sensor,
                "switch.{}",
            )

            assert (
                switch.entity_registry_enabled_default is True
            ), f"Switch '{switch_name}' should be enabled by default"
