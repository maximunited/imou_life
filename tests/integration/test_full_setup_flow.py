"""End-to-end test for complete integration setup flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries

from custom_components.imou_life.const import (
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    DOMAIN,
)
from tests.fixtures.mocks import MockConfigEntry


@pytest.mark.asyncio
async def test_full_setup_flow_with_discovery(hass, api_ok, mock_imou_device):
    """Test complete setup flow from config to entity creation with device discovery."""
    # Step 1: Initialize config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["step_id"] == "login"

    # Step 2: Submit login credentials with discovery enabled
    with patch(
        "imouapi.device.ImouDiscoverService.async_discover_devices",
        return_value={"test_device_123": mock_imou_device},
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_API_URL: "https://openapi.easy4ip.com/openapi",
                CONF_APP_ID: "test_app_id",
                CONF_APP_SECRET: "test_app_secret",
                "enable_discover": True,
            },
        )

    assert result["type"] == "form"
    assert result["step_id"] == "discover"

    # Step 3: Select discovered device
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_DEVICE_NAME: "Test Camera",
            "discovered_device": "test_device_123",
        },
    )

    # Verify config entry created
    assert result["type"] == "create_entry"
    assert result["title"] == "Test Camera"
    assert result["data"][CONF_DEVICE_ID] == "test_device_123"

    # Step 4: Verify integration setup completes
    config_entry = result["result"]
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify coordinator is created
    assert DOMAIN in hass.data
    assert config_entry.entry_id in hass.data[DOMAIN]

    # Verify entities are created (would be in entity registry in real HA)
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    assert coordinator is not None
    assert coordinator.device.get_device_id() == "test_device_123"


@pytest.mark.asyncio
async def test_full_setup_flow_manual_entry(hass, api_ok, mock_imou_device):
    """Test complete setup flow with manual device ID entry."""
    # Step 1: Initialize config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["step_id"] == "login"

    # Step 2: Submit login credentials without discovery
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_API_URL: "https://openapi.easy4ip.com/openapi",
            CONF_APP_ID: "test_app_id",
            CONF_APP_SECRET: "test_app_secret",
            "enable_discover": False,
        },
    )

    assert result["type"] == "form"
    assert result["step_id"] == "manual"

    # Step 3: Enter device ID manually
    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_DEVICE_ID: "test_device_123",
                CONF_DEVICE_NAME: "Manual Camera",
            },
        )

    # Verify config entry created
    assert result["type"] == "create_entry"
    assert result["title"] == "Manual Camera"
    assert result["data"][CONF_DEVICE_ID] == "test_device_123"


@pytest.mark.asyncio
async def test_setup_and_entity_state_updates(hass, api_ok, mock_imou_device):
    """Test that entity states update when coordinator refreshes data."""
    # Setup integration
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_URL: "https://openapi.easy4ip.com/openapi",
            CONF_APP_ID: "test_app_id",
            CONF_APP_SECRET: "test_app_secret",
            CONF_DEVICE_ID: "test_device_123",
            CONF_DEVICE_NAME: "Test Camera",
        },
        entry_id="test_entry",
        version=3,
    )
    config_entry.add_to_hass(hass)

    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    # Get coordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    assert coordinator is not None

    # Initial data state
    initial_data = coordinator.data
    assert initial_data is not None

    # Update device data
    mock_imou_device.async_get_data.return_value = {
        "battery_level": 75,  # Changed from 85
        "online": True,
        "motion_detected": True,  # Changed from False
    }

    # Trigger coordinator refresh
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    # Verify data updated
    updated_data = coordinator.data
    assert updated_data["battery_level"] == 75
    assert updated_data["motion_detected"] is True


@pytest.mark.asyncio
async def test_setup_reload_and_unload(hass, api_ok, mock_imou_device):
    """Test integration can be reloaded and unloaded properly."""
    from custom_components.imou_life import async_reload_entry, async_unload_entry

    # Setup
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_URL: "https://openapi.easy4ip.com/openapi",
            CONF_APP_ID: "test_app_id",
            CONF_APP_SECRET: "test_app_secret",
            CONF_DEVICE_ID: "test_device_123",
            CONF_DEVICE_NAME: "Test Camera",
        },
        entry_id="test_entry",
        version=3,
    )
    config_entry.add_to_hass(hass)

    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    # Verify setup
    assert DOMAIN in hass.data
    assert config_entry.entry_id in hass.data[DOMAIN]

    # Reload
    with patch("imouapi.device.ImouDevice", return_value=mock_imou_device):
        await async_reload_entry(hass, config_entry)
        await hass.async_block_till_done()

    # Verify still working after reload
    assert DOMAIN in hass.data
    assert config_entry.entry_id in hass.data[DOMAIN]

    # Unload
    assert await async_unload_entry(hass, config_entry)
    await hass.async_block_till_done()

    # Verify cleanup
    assert config_entry.entry_id not in hass.data[DOMAIN]
