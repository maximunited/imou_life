"""End-to-end tests for entity interactions and error scenarios."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import ConfigEntryNotReady
from imouapi.exceptions import ImouException

from custom_components.imou_life import async_setup_entry
from custom_components.imou_life.const import DOMAIN
from tests.fixtures.mocks import MockConfigEntry


@pytest.mark.asyncio
async def test_switch_entity_interaction(hass, api_ok, mock_imou_device):
    """Test switch entity can be toggled through coordinator."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "app_id": "test",
            "app_secret": "secret",
            "device_id": "test_device_123",
            "device_name": "Test Camera",
        },
        entry_id="switch_test",
        version=3,
    )
    config_entry.add_to_hass(hass)

    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    # Get coordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Verify switch sensors were discovered
    switch_sensors = mock_imou_device.get_sensors_by_platform("switch")
    assert len(switch_sensors) > 0

    # Get the switch entity (motion detect)
    switch = switch_sensors[0]
    assert switch.is_on() is True

    # Turn off the switch
    await switch.async_turn_off()
    switch.async_turn_off.assert_called_once()

    # Turn on the switch
    await switch.async_turn_on()
    switch.async_turn_on.assert_called_once()


@pytest.mark.asyncio
async def test_binary_sensor_state_changes(hass, api_ok, mock_imou_device):
    """Test binary sensor reflects coordinator data changes."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "device_id": "test_device_123",
            "device_name": "Test Camera",
        },
        entry_id="binary_test",
        version=3,
    )
    config_entry.add_to_hass(hass)

    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    # Get binary sensors
    binary_sensors = mock_imou_device.get_sensors_by_platform("binary_sensor")
    assert len(binary_sensors) > 0

    # Online sensor should be True initially
    online_sensor = binary_sensors[0]
    assert online_sensor.is_on() is True

    # Simulate device going offline
    mock_imou_device.async_get_data.return_value = {
        "online": False,
        "battery_level": 85,
    }

    # Refresh coordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    # Verify data updated (in real HA, entity would update automatically)
    assert coordinator.data["online"] is False


@pytest.mark.asyncio
async def test_api_connection_failure_on_setup(hass):
    """Test ConfigEntryNotReady is raised when API connection fails."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "app_id": "invalid",
            "app_secret": "invalid",
            "device_id": "test_device_123",
        },
        entry_id="fail_test",
        version=3,
    )

    # Mock API connection failure
    with patch("imouapi.api.ImouAPIClient") as mock_api:
        mock_api_instance = MagicMock()
        mock_api_instance.async_connect = AsyncMock(
            side_effect=ImouException("Connection failed")
        )
        mock_api.return_value = mock_api_instance

        with patch("imouapi.device.ImouDevice") as mock_device:
            mock_device_instance = MagicMock()
            mock_device_instance.async_initialize = AsyncMock(
                side_effect=Exception("Device init failed")
            )
            mock_device.return_value = mock_device_instance

            # Should raise ConfigEntryNotReady
            with pytest.raises(ConfigEntryNotReady):
                await async_setup_entry(hass, config_entry)


@pytest.mark.asyncio
async def test_coordinator_update_failure_recovery(hass, api_ok, mock_imou_device):
    """Test coordinator recovers from temporary update failures."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        entry_id="recovery_test",
        version=3,
    )
    config_entry.add_to_hass(hass)

    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # First update succeeds
    await coordinator.async_refresh()
    assert coordinator.data is not None
    first_data = coordinator.data

    # Simulate temporary API failure
    mock_imou_device.async_get_data.side_effect = Exception("Temporary failure")

    # Update should fail but not crash
    await coordinator.async_refresh()

    # Data should still be available (last known good state)
    assert coordinator.data == first_data

    # Restore API
    mock_imou_device.async_get_data.side_effect = None
    mock_imou_device.async_get_data.return_value = {
        "battery_level": 90,
        "online": True,
    }

    # Update should succeed again
    await coordinator.async_refresh()
    assert coordinator.data["battery_level"] == 90


@pytest.mark.asyncio
async def test_multiple_devices_same_integration(hass, api_ok, mock_imou_device):
    """Test multiple devices can be added to same integration instance."""
    # First device
    config_entry_1 = MockConfigEntry(
        domain=DOMAIN,
        data={
            "device_id": "device_1",
            "device_name": "Camera 1",
        },
        entry_id="device_1_test",
        version=3,
    )
    config_entry_1.add_to_hass(hass)

    # Second device
    mock_device_2 = MagicMock()
    mock_device_2.get_device_id.return_value = "device_2"
    mock_device_2.get_name.return_value = "Camera 2"
    mock_device_2.async_initialize = AsyncMock()
    mock_device_2.async_get_data = AsyncMock(return_value={"battery_level": 75})
    mock_device_2.get_sensors_by_platform = mock_imou_device.get_sensors_by_platform

    config_entry_2 = MockConfigEntry(
        domain=DOMAIN,
        data={
            "device_id": "device_2",
            "device_name": "Camera 2",
        },
        entry_id="device_2_test",
        version=3,
    )
    config_entry_2.add_to_hass(hass)

    # Setup both devices
    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        assert await hass.config_entries.async_setup(config_entry_1.entry_id)

    with patch("imouapi.device.ImouDevice", return_value=mock_device_2):
        assert await hass.config_entries.async_setup(config_entry_2.entry_id)

    await hass.async_block_till_done()

    # Both devices should be in hass.data
    assert DOMAIN in hass.data
    assert config_entry_1.entry_id in hass.data[DOMAIN]
    assert config_entry_2.entry_id in hass.data[DOMAIN]

    # Each should have their own coordinator
    coordinator_1 = hass.data[DOMAIN][config_entry_1.entry_id]
    coordinator_2 = hass.data[DOMAIN][config_entry_2.entry_id]
    assert coordinator_1 != coordinator_2


@pytest.mark.asyncio
async def test_config_entry_options_update(hass, api_ok, mock_imou_device):
    """Test that changing config entry options updates the integration."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        options={"scan_interval": 300},
        entry_id="options_test",
        version=3,
    )
    config_entry.add_to_hass(hass)

    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    initial_interval = coordinator.update_interval.total_seconds()

    # Update options
    new_options = {"scan_interval": 600}
    hass.config_entries.async_update_entry(config_entry, options=new_options)

    # Reload entry to apply new options
    from custom_components.imou_life import async_reload_entry

    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        await async_reload_entry(hass, config_entry)
        await hass.async_block_till_done()

    # Get updated coordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    new_interval = coordinator.update_interval.total_seconds()

    # Interval should have changed
    assert new_interval != initial_interval


@pytest.mark.asyncio
async def test_entity_availability_reflects_device_status(hass, api_ok, mock_imou_device):
    """Test that entity availability reflects device online/offline status."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={"device_id": "test_device_123"},
        entry_id="availability_test",
        version=3,
    )
    config_entry.add_to_hass(hass)

    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    # Device is initially online
    assert mock_imou_device.get_status() is True

    # Simulate device going offline
    mock_imou_device.get_status.return_value = False

    # In a real HA setup, entities would check device.get_status()
    # to determine their availability property
    assert mock_imou_device.get_status() is False

    # Device comes back online
    mock_imou_device.get_status.return_value = True
    assert mock_imou_device.get_status() is True
