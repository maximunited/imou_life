"""Tests for config flow reauthentication."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.data_entry_flow import FlowResultType
from imouapi.exceptions import ImouException

from custom_components.imou_life.config_flow import ImouFlowHandler
from custom_components.imou_life.const import (
    CONF_API_SERVER,
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    DEFAULT_API_SERVER,
    DOMAIN,
)
from tests.fixtures.mocks import MockConfigEntry


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry for reauth."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_APP_ID: "old_app_id",
            CONF_APP_SECRET: "old_app_secret",
            CONF_DEVICE_ID: "test_device_123",
            CONF_DEVICE_NAME: "Test Camera",
            CONF_API_URL: "https://api.example.com",
            CONF_API_SERVER: DEFAULT_API_SERVER,
        },
        entry_id="test_entry_123",
        title="Test Camera",
        version=3,
    )


@pytest.fixture
def mock_hass(mock_config_entry):
    """Create a mock hass instance."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
    hass.config_entries.async_update_entry = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    return hass


class TestReauthFlow:
    """Test reauthentication flow."""

    @pytest.mark.asyncio
    async def test_reauth_flow_shows_form(self, mock_hass, mock_config_entry):
        """Test that reauth flow shows the confirmation form."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        # Trigger reauth
        result = await flow.async_step_reauth({})

        # Should show reauth_confirm form
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reauth_confirm"
        assert result["errors"] == {}

    @pytest.mark.asyncio
    async def test_reauth_successful(self, mock_hass, mock_config_entry):
        """Test successful reauthentication."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        # Mock successful API connection
        with (
            patch(
                "custom_components.imou_life.config_flow.ImouAPIClient"
            ) as mock_api_client,
            patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device,
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
        ):
            # Set up mocks
            api_instance = mock_api_client.return_value
            api_instance.async_connect = AsyncMock()

            device_instance = mock_device.return_value
            device_instance.async_initialize = AsyncMock()

            # Set entry attribute
            await flow.async_step_reauth({})

            # Submit new credentials
            result = await flow.async_step_reauth_confirm(
                {
                    CONF_APP_ID: "new_app_id",
                    CONF_APP_SECRET: "new_app_secret",
                }
            )

            # Should abort with success
            assert result["type"] == FlowResultType.ABORT
            assert result["reason"] == "reauth_successful"

            # Verify config entry was updated
            mock_hass.config_entries.async_update_entry.assert_called_once()
            update_call = mock_hass.config_entries.async_update_entry.call_args
            assert update_call[1]["data"][CONF_APP_ID] == "new_app_id"
            assert update_call[1]["data"][CONF_APP_SECRET] == "new_app_secret"

            # Verify integration was reloaded
            mock_hass.config_entries.async_reload.assert_called_once_with(
                "test_entry_123"
            )

    @pytest.mark.asyncio
    async def test_reauth_invalid_credentials(self, mock_hass, mock_config_entry):
        """Test reauthentication with invalid credentials."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        with (
            patch(
                "custom_components.imou_life.config_flow.ImouAPIClient"
            ) as mock_api_client,
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
        ):
            # Mock authentication failure
            api_instance = mock_api_client.return_value
            api_instance.async_connect = AsyncMock(
                side_effect=ImouException("Invalid credentials")
            )

            await flow.async_step_reauth({})

            # Submit new credentials
            result = await flow.async_step_reauth_confirm(
                {
                    CONF_APP_ID: "bad_app_id",
                    CONF_APP_SECRET: "bad_app_secret",
                }
            )

            # Should show form again with error
            assert result["type"] == FlowResultType.FORM
            assert result["step_id"] == "reauth_confirm"
            assert result["errors"]["base"] == "not_authorized"

    @pytest.mark.asyncio
    async def test_reauth_rate_limit_error(self, mock_hass, mock_config_entry):
        """Test reauthentication when rate limited."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        with (
            patch(
                "custom_components.imou_life.config_flow.ImouAPIClient"
            ) as mock_api_client,
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
        ):
            # Mock rate limit error
            api_instance = mock_api_client.return_value
            api_instance.async_connect = AsyncMock(
                side_effect=ImouException("OP1013: Call interface times exceed limit")
            )

            await flow.async_step_reauth({})

            result = await flow.async_step_reauth_confirm(
                {
                    CONF_APP_ID: "app_id",
                    CONF_APP_SECRET: "app_secret",
                }
            )

            # Should show form with rate limit error
            assert result["type"] == FlowResultType.FORM
            assert result["errors"]["base"] == "rate_limit_exceeded"

    @pytest.mark.asyncio
    async def test_reauth_connection_error(self, mock_hass, mock_config_entry):
        """Test reauthentication with connection error."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        with (
            patch(
                "custom_components.imou_life.config_flow.ImouAPIClient"
            ) as mock_api_client,
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
        ):
            # Mock connection failure
            api_instance = mock_api_client.return_value
            api_instance.async_connect = AsyncMock(
                side_effect=ImouException("Connection timeout")
            )

            await flow.async_step_reauth({})

            result = await flow.async_step_reauth_confirm(
                {
                    CONF_APP_ID: "app_id",
                    CONF_APP_SECRET: "app_secret",
                }
            )

            # Should show form with connection error
            assert result["type"] == FlowResultType.FORM
            assert result["errors"]["base"] == "connection_failed"

    @pytest.mark.asyncio
    async def test_reauth_generic_api_error(self, mock_hass, mock_config_entry):
        """Test reauthentication with generic API error."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        with (
            patch(
                "custom_components.imou_life.config_flow.ImouAPIClient"
            ) as mock_api_client,
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
        ):
            # Mock generic API error
            api_instance = mock_api_client.return_value
            api_instance.async_connect = AsyncMock(
                side_effect=ImouException("Unknown API error")
            )

            await flow.async_step_reauth({})

            result = await flow.async_step_reauth_confirm(
                {
                    CONF_APP_ID: "app_id",
                    CONF_APP_SECRET: "app_secret",
                }
            )

            # Should show form with generic error
            assert result["type"] == FlowResultType.FORM
            assert result["errors"]["base"] == "api_error"

    @pytest.mark.asyncio
    async def test_reauth_device_access_verification(
        self, mock_hass, mock_config_entry
    ):
        """Test that reauth verifies device access after authentication."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        with (
            patch(
                "custom_components.imou_life.config_flow.ImouAPIClient"
            ) as mock_api_client,
            patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device,
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
        ):
            # Set up mocks
            api_instance = mock_api_client.return_value
            api_instance.async_connect = AsyncMock()

            device_instance = mock_device.return_value
            device_instance.async_initialize = AsyncMock()

            await flow.async_step_reauth({})

            await flow.async_step_reauth_confirm(
                {
                    CONF_APP_ID: "new_app_id",
                    CONF_APP_SECRET: "new_app_secret",
                }
            )

            # Verify device was initialized to check access
            mock_device.assert_called_once_with(api_instance, "test_device_123")
            device_instance.async_initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_reauth_empty_device_name_fallback(self, mock_hass):
        """Test that empty device name falls back to entry title."""
        # Create entry with empty device name
        entry_empty_name = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_APP_ID: "old_app_id",
                CONF_APP_SECRET: "old_app_secret",
                CONF_DEVICE_ID: "test_device_123",
                CONF_DEVICE_NAME: "",  # Empty string
                CONF_API_URL: "https://api.example.com",
                CONF_API_SERVER: DEFAULT_API_SERVER,
            },
            entry_id="test_entry_123",
            title="Test Camera",
            version=3,
        )
        mock_hass.config_entries.async_get_entry = MagicMock(
            return_value=entry_empty_name
        )

        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        await flow.async_step_reauth({})

        # Show form without user input
        result = await flow.async_step_reauth_confirm(None)

        # Verify description_placeholders uses entry.title as fallback
        assert result["description_placeholders"]["device_name"] == "Test Camera"

    @pytest.mark.asyncio
    async def test_reauth_none_device_name_fallback(self, mock_hass):
        """Test that None device name falls back to entry title."""
        # Create entry with None device name
        entry_none_name = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_APP_ID: "old_app_id",
                CONF_APP_SECRET: "old_app_secret",
                CONF_DEVICE_ID: "test_device_123",
                CONF_DEVICE_NAME: None,  # None
                CONF_API_URL: "https://api.example.com",
                CONF_API_SERVER: DEFAULT_API_SERVER,
            },
            entry_id="test_entry_123",
            title="Test Camera",
            version=3,
        )
        mock_hass.config_entries.async_get_entry = MagicMock(
            return_value=entry_none_name
        )

        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "test_entry_123"}

        await flow.async_step_reauth({})

        result = await flow.async_step_reauth_confirm(None)

        # Verify description_placeholders uses entry.title as fallback
        assert result["description_placeholders"]["device_name"] == "Test Camera"

    @pytest.mark.asyncio
    async def test_reauth_auth_pattern_matching(self, mock_hass, mock_config_entry):
        """Test all authentication error patterns are detected."""
        auth_errors = [
            "authentication failed",
            "Invalid credentials provided",
            "Invalid App ID or Secret",
            "Token expired, please login again",
            "Unauthorized access",
            "OP1002: Authentication error",
        ]

        for error_msg in auth_errors:
            flow = ImouFlowHandler()
            flow.hass = mock_hass
            flow.context = {"entry_id": "test_entry_123"}

            with (
                patch(
                    "custom_components.imou_life.config_flow.ImouAPIClient"
                ) as mock_api_client,
                patch(
                    "custom_components.imou_life.config_flow.async_create_clientsession"
                ),
            ):
                api_instance = mock_api_client.return_value
                api_instance.async_connect = AsyncMock(
                    side_effect=ImouException(error_msg)
                )

                await flow.async_step_reauth({})
                result = await flow.async_step_reauth_confirm(
                    {
                        CONF_APP_ID: "app_id",
                        CONF_APP_SECRET: "app_secret",
                    }
                )

                # All should map to not_authorized
                assert (
                    result["errors"]["base"] == "not_authorized"
                ), f"Error '{error_msg}' should map to not_authorized"
