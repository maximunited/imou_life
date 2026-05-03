"""Unit tests for stale device detection."""

from unittest.mock import AsyncMock, Mock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from imouapi.exceptions import ImouException

from custom_components.imou_life.coordinator import ImouDataUpdateCoordinator


@pytest.fixture
def mock_device():
    """Create a mock ImouDevice."""
    device = Mock()
    device.async_get_data = AsyncMock()
    device.get_name = Mock(return_value="Test Camera")
    device.get_device_id = Mock(return_value="test_device_123")
    device.get_model = Mock(return_value="Test Model")
    return device


@pytest.fixture
def mock_config_entry():
    """Create a mock ConfigEntry."""
    entry = Mock(spec=ConfigEntry)
    entry.entry_id = "test_entry_123"
    entry.data = {
        "device_id": "test_device_123",
        "device_name": "Test Camera",
    }
    entry.options = {}
    return entry


@pytest.fixture
def coordinator(hass: HomeAssistant, mock_device, mock_config_entry):
    """Create a coordinator instance for testing."""
    coordinator = ImouDataUpdateCoordinator(
        hass,
        mock_device,
        900,
        mock_config_entry,
    )
    return coordinator


async def test_is_stale_device_error_detects_patterns(hass: HomeAssistant, coordinator):
    """Test that _is_stale_device_error correctly identifies stale device errors."""
    # Test stale device patterns
    assert coordinator._is_stale_device_error("Device not found") is True
    assert coordinator._is_stale_device_error("Invalid device ID") is True
    assert (
        coordinator._is_stale_device_error("Not authorized to operate on the device")
        is True
    )

    # Test case insensitivity
    assert coordinator._is_stale_device_error("DEVICE NOT FOUND") is True
    assert coordinator._is_stale_device_error("device not found") is True


async def test_is_stale_device_error_excludes_auth_errors(
    hass: HomeAssistant, coordinator
):
    """Test that auth errors are NOT detected as stale device errors."""
    # These should NOT trigger stale device detection (they go to reauth flow)
    assert coordinator._is_stale_device_error("Authentication failed") is False
    assert (
        coordinator._is_stale_device_error("Token expired, please login again") is False
    )
    assert coordinator._is_stale_device_error("Invalid app credentials") is False
    assert coordinator._is_stale_device_error("AUTHENTICATION FAILED") is False


async def test_is_stale_device_error_excludes_other_errors(
    hass: HomeAssistant, coordinator
):
    """Test that other errors are not detected as stale device errors."""
    # Rate limit errors
    assert coordinator._is_stale_device_error("OP1013: Rate limit exceeded") is False

    # Connection errors
    assert coordinator._is_stale_device_error("Connection timeout") is False

    # Generic errors
    assert coordinator._is_stale_device_error("Unknown error occurred") is False


async def test_stale_device_detection_threshold(
    hass: HomeAssistant, coordinator, mock_device
):
    """Test device marked stale after 3 consecutive failures."""
    mock_device.async_get_data.side_effect = ImouException("Device not found")

    # First failure
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.stale_device_failure_count == 1
    assert coordinator.stale_device_suspected is False
    assert coordinator.stale_device_last_error == "Device not found"

    # Second failure
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.stale_device_failure_count == 2
    assert coordinator.stale_device_suspected is False

    # Third failure - should trigger stale detection
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.stale_device_failure_count == 3
    assert coordinator.stale_device_suspected is True


async def test_stale_device_reset_on_success(
    hass: HomeAssistant, coordinator, mock_device
):
    """Test counter resets when update succeeds after failures."""
    # Cause 2 failures
    mock_device.async_get_data.side_effect = ImouException("Device not found")

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.stale_device_failure_count == 2
    assert coordinator.stale_device_last_error == "Device not found"

    # Now succeed
    mock_device.async_get_data.side_effect = None
    mock_device.async_get_data.return_value = {"status": "ok"}

    result = await coordinator._async_update_data()

    assert result == {"status": "ok"}
    assert coordinator.stale_device_failure_count == 0
    assert coordinator.stale_device_suspected is False
    assert coordinator.stale_device_last_error is None


async def test_stale_device_vs_auth_error(
    hass: HomeAssistant, coordinator, mock_device
):
    """Test auth errors don't trigger stale detection."""
    mock_device.async_get_data.side_effect = ImouException("Authentication failed")

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()

    # Counter should NOT increment for auth errors
    assert coordinator.stale_device_failure_count == 0
    assert coordinator.stale_device_suspected is False


async def test_stale_device_vs_rate_limit(
    hass: HomeAssistant, coordinator, mock_device
):
    """Test rate limit errors don't trigger stale detection."""
    mock_device.async_get_data.side_effect = ImouException(
        "OP1013: Rate limit exceeded"
    )

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    # Counter should NOT increment for rate limit errors
    assert coordinator.stale_device_failure_count == 0
    assert coordinator.stale_device_suspected is False

    # Rate limit tracking should work normally
    assert coordinator.is_rate_limited is True


async def test_stale_device_mixed_errors(hass: HomeAssistant, coordinator, mock_device):
    """Test that non-stale errors reset counter (ensures consecutive failures)."""
    # First: stale device error
    mock_device.async_get_data.side_effect = ImouException("Device not found")
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    assert coordinator.stale_device_failure_count == 1

    # Second: rate limit error (non-stale error resets counter)
    mock_device.async_get_data.side_effect = ImouException("OP1013")
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    # Counter should be reset to 0 (non-stale error breaks the streak)
    assert coordinator.stale_device_failure_count == 0
    assert coordinator.stale_device_suspected is False
    assert coordinator.stale_device_last_error is None

    # Third: stale device error again (starts new streak)
    mock_device.async_get_data.side_effect = ImouException("Invalid device")
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    # Counter restarts from 1
    assert coordinator.stale_device_failure_count == 1


async def test_stale_device_suspected_only_at_threshold(
    hass: HomeAssistant, coordinator, mock_device
):
    """Test suspected flag only set when threshold is reached."""
    mock_device.async_get_data.side_effect = ImouException("Device not found")

    # First two failures - not suspected yet
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.stale_device_suspected is False

    # Third failure - now suspected
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.stale_device_suspected is True

    # Fourth failure - still suspected (stays true)
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.stale_device_suspected is True
    assert coordinator.stale_device_failure_count == 4


async def test_stale_device_error_message_format(
    hass: HomeAssistant, coordinator, mock_device
):
    """Test error message includes failure count and threshold."""
    mock_device.async_get_data.side_effect = ImouException("Device not found")

    # First failure
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
