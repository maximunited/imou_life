"""Test imou setup process."""

import pytest
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.imou_life import (
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.imou_life.const import DOMAIN
from custom_components.imou_life.coordinator import ImouDataUpdateCoordinator
from tests.fixtures.const import MOCK_CONFIG_ENTRY
from tests.fixtures.mocks import MockConfigEntry


@pytest.mark.asyncio
async def test_setup_unload_and_reload_entry(hass, api_ok):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ENTRY, entry_id="test", version=3
    )
    # test setup entry
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    assert hasattr(config_entry, "runtime_data")
    assert isinstance(config_entry.runtime_data, ImouDataUpdateCoordinator)

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert hasattr(config_entry, "runtime_data")
    assert isinstance(config_entry.runtime_data, ImouDataUpdateCoordinator)

    # Unload the entry and verify that unload succeeds
    assert await async_unload_entry(hass, config_entry)


@pytest.mark.asyncio
async def test_setup_entry_exception(hass, api_invalid_data):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_CONFIG_ENTRY, entry_id="test"
    )

    # In this case we are testing the condition where async_setup_entry
    # raises ConfigEntryNotReady
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)
