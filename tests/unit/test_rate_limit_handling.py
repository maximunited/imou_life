"""Test rate limit error handling."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed
from imouapi.exceptions import APIError

from custom_components.imou_life import async_setup_entry
from custom_components.imou_life.const import DOMAIN
from custom_components.imou_life.coordinator import ImouDataUpdateCoordinator
from tests.fixtures.const import MOCK_CONFIG_ENTRY
from tests.fixtures.mocks import MockConfigEntry


@pytest.mark.asyncio
async def test_rate_limit_during_initialization(hass):
    """Test that OP1013 rate limit errors during init are handled gracefully."""
    # Create a config entry
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY.data,
        entry_id="test_rate_limit",
        version=3,
    )

    # Mock the API client and device to raise rate limit error on initialization
    with (
        patch("custom_components.imou_life.ImouAPIClient") as mock_api_client_class,
        patch("custom_components.imou_life.ImouDevice") as mock_device_class,
    ):
        mock_api_instance = MagicMock()
        mock_api_client_class.return_value = mock_api_instance

        mock_device = AsyncMock()
        # Simulate rate limit error during initialization
        mock_device.async_initialize.side_effect = APIError(
            "OP1013: Call interface times exceed limit (total)"
        )
        mock_device_class.return_value = mock_device

        # Add entry to hass
        config_entry.add_to_hass(hass)

        # Setup should raise ConfigEntryNotReady (not the raw APIError)
        with pytest.raises(ConfigEntryNotReady) as exc_info:
            await async_setup_entry(hass, config_entry)

        # Verify the error message mentions rate limit and retry
        assert "rate limit" in str(exc_info.value).lower()
        assert "retry" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_rate_limit_during_coordinator_update(hass):
    """Test that OP1013 rate limit errors during updates are handled gracefully."""
    # Create a mock device that raises rate limit error
    mock_device = AsyncMock()
    mock_device.async_get_data.side_effect = APIError(
        "OP1013: Call interface times exceed limit (total)"
    )

    # Create coordinator
    coordinator = ImouDataUpdateCoordinator(
        hass=hass, device=mock_device, scan_interval=60
    )

    # Update should raise UpdateFailed (not the raw APIError)
    with pytest.raises(UpdateFailed) as exc_info:
        await coordinator._async_update_data()

    # Verify the error message mentions rate limit
    assert "rate limit" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_other_api_errors_still_raised(hass):
    """Test that non-rate-limit API errors are still raised normally."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY.data,
        entry_id="test_other_error",
        version=3,
    )

    with (
        patch("custom_components.imou_life.ImouAPIClient") as mock_api_client_class,
        patch("custom_components.imou_life.ImouDevice") as mock_device_class,
    ):
        mock_api_instance = MagicMock()
        mock_api_client_class.return_value = mock_api_instance

        mock_device = AsyncMock()
        # Simulate a different API error (not rate limit)
        mock_device.async_initialize.side_effect = APIError("OP9999: Some other error")
        mock_device_class.return_value = mock_device

        config_entry.add_to_hass(hass)

        # Setup should raise the APIError directly (not ConfigEntryNotReady)
        with pytest.raises(APIError) as exc_info:
            await async_setup_entry(hass, config_entry)

        assert "OP9999" in str(exc_info.value)
        assert "OP1013" not in str(exc_info.value)


@pytest.mark.asyncio
async def test_rate_limit_variations(hass):
    """Test that various rate limit error messages are detected."""
    mock_device = AsyncMock()
    coordinator = ImouDataUpdateCoordinator(
        hass=hass, device=mock_device, scan_interval=60
    )

    # Test different rate limit error message variations
    rate_limit_messages = [
        "OP1013: Call interface times exceed limit (total)",
        "OP1013: exceed limit",
        "API calls exceed limit",
        "Rate limit exceeded",
    ]

    for error_msg in rate_limit_messages:
        mock_device.async_get_data.side_effect = APIError(error_msg)

        with pytest.raises(UpdateFailed) as exc_info:
            await coordinator._async_update_data()

        # All should be caught and logged as rate limit errors
        assert "rate limit" in str(exc_info.value).lower()
