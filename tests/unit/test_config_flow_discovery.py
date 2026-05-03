"""Test imou_life config flow discovery steps."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant import data_entry_flow

from custom_components.imou_life.const import (
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    DEFAULT_API_URL,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent actual integration setup during tests."""
    with (
        patch(
            "custom_components.imou_life.async_setup",
            return_value=True,
        ),
        patch(
            "custom_components.imou_life.async_setup_entry",
            return_value=True,
        ),
    ):
        yield


@pytest.mark.asyncio
async def test_discovery_flow_creates_entry(hass):
    """Test that discovery flow creates a config entry."""
    # Mock device
    mock_device = MagicMock()
    mock_device.get_name = MagicMock(return_value="Discovered Camera")

    # Discovery data - this is what the coordinator passes
    discovery_data = {
        "device_id": "test_device_123",
        "device": mock_device,
        "api_credentials": {
            "app_id": "test_app_id",
            "app_secret": "test_app_secret",
            "api_url": DEFAULT_API_URL,
        },
    }

    # Initialize discovery flow - source "discovery" triggers async_step_discovery
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "discovery"},
        data=discovery_data,
    )

    # Should show confirmation form
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"

    # Confirm discovery with custom name
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_DEVICE_NAME: "My Camera"},
    )

    # Should create entry
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "My Camera"
    assert result["data"][CONF_DEVICE_ID] == "test_device_123"
    assert result["data"][CONF_DEVICE_NAME] == "My Camera"
    assert result["data"][CONF_APP_ID] == "test_app_id"
    assert result["data"][CONF_APP_SECRET] == "test_app_secret"
    assert result["data"][CONF_API_URL] == DEFAULT_API_URL


@pytest.mark.asyncio
async def test_discovery_flow_default_device_name(hass):
    """Test that discovery flow uses device's default name when user doesn't provide one."""
    # Mock device
    mock_device = MagicMock()
    mock_device.get_name = MagicMock(return_value="Default Camera Name")

    # Initialize discovery flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "discovery"},
        data={
            "device_id": "test_device_456",
            "device": mock_device,
            "api_credentials": {
                "app_id": "test_app_id",
                "app_secret": "test_app_secret",
                "api_url": DEFAULT_API_URL,
            },
        },
    )

    # Confirm without providing custom name (empty dict uses defaults)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_DEVICE_NAME: ""},  # Empty name should use default
    )

    # Should use device's default name
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Default Camera Name"
    assert result["data"][CONF_DEVICE_NAME] == "Default Camera Name"


@pytest.mark.asyncio
async def test_discovery_flow_prevents_duplicates(hass):
    """Test that discovery flow prevents duplicate entries using unique_id."""
    # Mock device
    mock_device = MagicMock()
    mock_device.get_name = MagicMock(return_value="Duplicate Camera")

    discovery_data = {
        "device_id": "duplicate_device_789",
        "device": mock_device,
        "api_credentials": {
            "app_id": "test_app_id",
            "app_secret": "test_app_secret",
            "api_url": DEFAULT_API_URL,
        },
    }

    # Create first entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "discovery"}, data=discovery_data
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_DEVICE_NAME: "First Entry"},
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY

    # Try to create duplicate entry with same device_id
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "discovery"}, data=discovery_data
    )

    # Should abort due to existing unique_id
    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_discovery_flow_confirmation_description(hass):
    """Test that discovery confirmation shows device information."""
    # Mock device
    mock_device = MagicMock()
    mock_device.get_name = MagicMock(return_value="Test Camera")

    # Initialize discovery flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "discovery"},
        data={
            "device_id": "device_description_test",
            "device": mock_device,
            "api_credentials": {
                "app_id": "test_app_id",
                "app_secret": "test_app_secret",
                "api_url": DEFAULT_API_URL,
            },
        },
    )

    # Check description placeholders
    assert result.get("description_placeholders") is not None
    assert result["description_placeholders"]["device_name"] == "Test Camera"
    assert result["description_placeholders"]["device_id"] == "device_description_test"


@pytest.mark.asyncio
async def test_discovery_flow_with_custom_api_url(hass):
    """Test discovery flow with custom API URL."""
    # Mock device
    mock_device = MagicMock()
    mock_device.get_name = MagicMock(return_value="Custom API Camera")

    # Discovery data with custom API URL
    custom_api_url = "https://custom.api.url/openapi"

    # Initialize and complete flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "discovery"},
        data={
            "device_id": "custom_api_device",
            "device": mock_device,
            "api_credentials": {
                "app_id": "custom_app_id",
                "app_secret": "custom_app_secret",
                "api_url": custom_api_url,
            },
        },
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_DEVICE_NAME: "Custom Camera"},
    )

    # Should preserve custom API URL
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_API_URL] == custom_api_url


@pytest.mark.asyncio
async def test_discovery_flow_handles_device_without_get_name(hass):
    """Test discovery flow handles device that doesn't have get_name method."""
    # Mock device without get_name method
    mock_device = MagicMock(spec=[])

    # Initialize discovery flow - should not raise exception
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "discovery"},
        data={
            "device_id": "no_name_device",
            "device": mock_device,
            "api_credentials": {
                "app_id": "test_app_id",
                "app_secret": "test_app_secret",
                "api_url": DEFAULT_API_URL,
            },
        },
    )

    # Should show confirmation form with fallback name
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"


@pytest.mark.asyncio
async def test_discovery_flow_multiple_sequential_discoveries(hass):
    """Test multiple devices can be discovered sequentially."""
    # Mock devices
    devices = [
        (MagicMock(), "device_1", "Camera 1"),
        (MagicMock(), "device_2", "Camera 2"),
        (MagicMock(), "device_3", "Camera 3"),
    ]

    for mock_device, device_id, device_name in devices:
        mock_device.get_name = MagicMock(return_value=device_name)

        # Initialize and complete flow
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "discovery"},
            data={
                "device_id": device_id,
                "device": mock_device,
                "api_credentials": {
                    "app_id": "test_app_id",
                    "app_secret": "test_app_secret",
                    "api_url": DEFAULT_API_URL,
                },
            },
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_DEVICE_NAME: device_name},
        )

        # Each should create entry successfully
        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_DEVICE_ID] == device_id
        assert result["data"][CONF_DEVICE_NAME] == device_name

    # Verify all entries were created
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 3


@pytest.mark.asyncio
async def test_discovery_flow_preserves_credentials(hass):
    """Test that discovery flow preserves API credentials from first entry."""
    # Mock device
    mock_device = MagicMock()
    mock_device.get_name = MagicMock(return_value="Credentials Test Camera")

    # Discovery data with specific credentials
    app_id = "preserved_app_id"
    app_secret = "preserved_app_secret"

    # Complete flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "discovery"},
        data={
            "device_id": "credentials_test",
            "device": mock_device,
            "api_credentials": {
                "app_id": app_id,
                "app_secret": app_secret,
                "api_url": DEFAULT_API_URL,
            },
        },
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_DEVICE_NAME: "Test Camera"},
    )

    # Verify credentials are preserved
    assert result["data"][CONF_APP_ID] == app_id
    assert result["data"][CONF_APP_SECRET] == app_secret
