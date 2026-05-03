"""Test device removal functionality."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from custom_components.imou_life import async_remove_config_entry_device
from custom_components.imou_life.const import CONF_DEVICE_ID, CONF_DEVICE_NAME, DOMAIN
from tests.fixtures.mocks import MockConfigEntry


@pytest.mark.asyncio
async def test_async_remove_config_entry_device_matching_device(hass: HomeAssistant):
    """Test that matching device can be removed."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_DEVICE_ID: "test_device_123",
            CONF_DEVICE_NAME: "Test Camera",
        },
        entry_id="test_entry_id",
        version=3,
        title="Test Camera",
    )

    # Create a mock device entry with matching identifier
    # Note: Entities use config_entry.entry_id as device identifier, not device_id
    device_entry = DeviceEntry(
        id="device_id_123",
        identifiers={(DOMAIN, "test_entry_id")},  # Matches config_entry.entry_id
        manufacturer="Imou",
        model="Test Model",
        name="Test Camera",
    )

    # Should return True - device belongs to this config entry
    result = await async_remove_config_entry_device(hass, config_entry, device_entry)
    assert result is True


@pytest.mark.asyncio
async def test_async_remove_config_entry_device_non_matching_device(
    hass: HomeAssistant,
):
    """Test that non-matching device cannot be removed."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_DEVICE_ID: "test_device_123",
            CONF_DEVICE_NAME: "Test Camera",
        },
        entry_id="test_entry_id",
        version=3,
        title="Test Camera",
    )

    # Create a mock device entry with different identifier
    device_entry = DeviceEntry(
        id="device_id_456",
        identifiers={(DOMAIN, "different_device_456")},
        manufacturer="Imou",
        model="Test Model",
        name="Different Camera",
    )

    # Should return False - device doesn't belong to this config entry
    result = await async_remove_config_entry_device(hass, config_entry, device_entry)
    assert result is False


@pytest.mark.asyncio
async def test_async_remove_config_entry_device_multiple_identifiers(
    hass: HomeAssistant,
):
    """Test device removal with multiple identifiers."""
    # Create a mock config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_DEVICE_ID: "test_device_123",
            CONF_DEVICE_NAME: "Test Camera",
        },
        entry_id="test_entry_id",
        version=3,
        title="Test Camera",
    )

    # Create a mock device entry with multiple identifiers (one matches)
    # Note: Entities use config_entry.entry_id as device identifier
    device_entry = DeviceEntry(
        id="device_id_123",
        identifiers={
            ("other_domain", "other_id"),
            (DOMAIN, "test_entry_id"),  # This one matches config_entry.entry_id
        },
        manufacturer="Imou",
        model="Test Model",
        name="Test Camera",
    )

    # Should return True - one of the identifiers matches
    result = await async_remove_config_entry_device(hass, config_entry, device_entry)
    assert result is True


@pytest.mark.asyncio
async def test_async_remove_config_entry_device_no_device_id(hass: HomeAssistant):
    """Test device removal when config entry has no device_id in data.

    This test verifies that device_id in config data is not required for removal,
    since the function compares against config_entry.entry_id, not device_id.
    """
    # Create a mock config entry without device_id (edge case)
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_DEVICE_NAME: "Test Camera",
            # Missing CONF_DEVICE_ID - but this doesn't affect removal logic
        },
        entry_id="test_entry_id",
        version=3,
        title="Test Camera",
    )

    # Create a mock device entry with non-matching identifier
    device_entry = DeviceEntry(
        id="device_id_123",
        identifiers={(DOMAIN, "test_device_123")},  # Doesn't match entry_id
        manufacturer="Imou",
        model="Test Model",
        name="Test Camera",
    )

    # Should return False - identifier doesn't match config_entry.entry_id
    result = await async_remove_config_entry_device(hass, config_entry, device_entry)
    assert result is False
