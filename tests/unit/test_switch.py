"""Test imou_life switch."""

from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.imou_life.const import DOMAIN
from tests.fixtures.const import MOCK_CONFIG_ENTRY
from tests.fixtures.mocks import MockConfigEntry


# This fixture bypasses the actual setup of the integration
@pytest.fixture(autouse=True)
def bypass_added_to_hass() -> Generator[None, None, None]:
    """Prevent added to hass."""
    with (
        patch(
            "custom_components.imou_life.entity.ImouEntity.async_added_to_hass",
            return_value=True,
        ),
        patch(
            "custom_components.imou_life.entity.ImouEntity.async_will_remove_from_hass",
            return_value=True,
        ),
    ):
        yield


@pytest.mark.asyncio
async def test_switch(hass: HomeAssistant) -> None:
    """Test switch services."""
    # Create mock switch sensor with tracked methods
    mock_sensor = MagicMock()
    mock_sensor.get_name.return_value = "motionDetect"
    mock_sensor.get_description.return_value = "Motion Detection"
    mock_sensor.get_attributes.return_value = {}
    mock_sensor.is_on.return_value = False
    mock_sensor.async_turn_on = AsyncMock()
    mock_sensor.async_turn_off = AsyncMock()
    mock_sensor.set_enabled = MagicMock()
    mock_sensor.async_update = AsyncMock()

    # Create mock device
    mock_device = MagicMock()
    mock_device.get_name.return_value = "device_name"
    mock_device.get_device_id.return_value = "device_id"
    mock_device.get_model.return_value = "Test Model"
    mock_device.get_manufacturer.return_value = "Imou"
    mock_device.get_firmware.return_value = "1.0.0"
    mock_device.get_status.return_value = True

    def mock_get_sensors(platform):
        if platform == "switch":
            return [mock_sensor]
        return []

    mock_device.get_sensors_by_platform = mock_get_sensors

    # Create mock coordinator
    mock_coordinator = MagicMock()
    mock_coordinator.device = mock_device
    mock_coordinator.entities = []
    mock_coordinator.last_update_success = True
    mock_coordinator.hass = hass

    # Create config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ENTRY, entry_id="test", version=3
    )
    config_entry.add_to_hass(hass)

    # Patch to use our mock coordinator
    with patch.object(config_entry, "runtime_data", mock_coordinator):
        # Manually set up switch platform
        from custom_components.imou_life.switch import async_setup_entry

        async_add_devices = MagicMock()
        await async_setup_entry(hass, config_entry, async_add_devices)
        await hass.async_block_till_done()

        # Get the created switch entity
        async_add_devices.assert_called_once()
        switch_entities = async_add_devices.call_args[0][0]
        assert len(switch_entities) == 1
        switch_entity = switch_entities[0]

        # Add entity to hass manually
        switch_entity.hass = hass
        await switch_entity.async_added_to_hass()

        # Register the entity with hass
        hass.states.async_set(
            switch_entity.entity_id,
            "off",
            switch_entity.extra_state_attributes,
        )

        # Test turn_on (patch async_write_ha_state to avoid HA internal complexity)
        with patch.object(switch_entity, "async_write_ha_state"):
            await switch_entity.async_turn_on()
        assert mock_sensor.async_turn_on.called

        # Test turn_off
        with patch.object(switch_entity, "async_write_ha_state"):
            await switch_entity.async_turn_off()
        assert mock_sensor.async_turn_off.called
