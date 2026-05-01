"""Comprehensive tests for config flow (login, discover, manual, options)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.data_entry_flow import FlowResultType
from imouapi.exceptions import ImouException

from custom_components.imou_life.config_flow import (
    ImouFlowHandler,
    ImouOptionsFlowHandler,
)
from custom_components.imou_life.const import (
    CONF_API_SERVER,
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DISCOVERED_DEVICE,
    CONF_ENABLE_DISCOVER,
    DEFAULT_API_SERVER,
    DOMAIN,
    OPTION_API_TIMEOUT,
    OPTION_CALLBACK_URL,
    OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD,
    OPTION_SCAN_INTERVAL,
    OPTION_WAIT_AFTER_WAKE_UP,
)
from tests.fixtures.mocks import MockConfigEntry


class TestConfigFlowLogin:
    """Test login step of config flow."""

    @pytest.mark.asyncio
    async def test_async_step_user_redirects_to_login(self):
        """Test user step redirects to login."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()

        with patch(
            "custom_components.imou_life.config_flow.async_create_clientsession"
        ):
            result = await flow.async_step_user()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "login"

    @pytest.mark.asyncio
    async def test_async_step_login_custom_url_missing(self):
        """Test login with custom server but no URL shows error."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()

        with patch(
            "custom_components.imou_life.config_flow.async_create_clientsession"
        ):
            result = await flow.async_step_login(
                {
                    CONF_APP_ID: "test_id",
                    CONF_APP_SECRET: "test_secret",
                    CONF_API_SERVER: "custom",
                    CONF_API_URL: "",
                    CONF_ENABLE_DISCOVER: True,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["api_url"] == "custom_url_required"

    @pytest.mark.asyncio
    async def test_async_step_login_success_with_discovery(self):
        """Test successful login redirects to discover step."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()

        with (
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
            patch("custom_components.imou_life.config_flow.ImouAPIClient") as mock_api,
            patch(
                "custom_components.imou_life.config_flow.ImouDiscoverService"
            ) as mock_discover,
        ):
            api_instance = mock_api.return_value
            api_instance.async_connect = AsyncMock()

            discover_instance = mock_discover.return_value
            discover_instance.async_discover_devices = AsyncMock(return_value={})

            result = await flow.async_step_login(
                {
                    CONF_APP_ID: "test_id",
                    CONF_APP_SECRET: "test_secret",
                    CONF_API_SERVER: DEFAULT_API_SERVER,
                    CONF_ENABLE_DISCOVER: True,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "manual"  # No devices found, redirects to manual

    @pytest.mark.asyncio
    async def test_async_step_login_success_with_manual(self):
        """Test successful login redirects to manual step."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()

        with (
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
            patch("custom_components.imou_life.config_flow.ImouAPIClient") as mock_api,
            patch("custom_components.imou_life.config_flow.ImouDiscoverService"),
        ):
            api_instance = mock_api.return_value
            api_instance.async_connect = AsyncMock()

            result = await flow.async_step_login(
                {
                    CONF_APP_ID: "test_id",
                    CONF_APP_SECRET: "test_secret",
                    CONF_API_SERVER: DEFAULT_API_SERVER,
                    CONF_ENABLE_DISCOVER: False,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "manual"

    @pytest.mark.asyncio
    async def test_async_step_login_invalid_credentials(self):
        """Test login with invalid credentials shows error."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()

        with (
            patch("custom_components.imou_life.config_flow.async_create_clientsession"),
            patch("custom_components.imou_life.config_flow.ImouAPIClient") as mock_api,
        ):
            api_instance = mock_api.return_value
            api_instance.async_connect = AsyncMock(
                side_effect=ImouException("Invalid credentials")
            )

            result = await flow.async_step_login(
                {
                    CONF_APP_ID: "bad_id",
                    CONF_APP_SECRET: "bad_secret",
                    CONF_API_SERVER: DEFAULT_API_SERVER,
                    CONF_ENABLE_DISCOVER: True,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert "base" in result["errors"]


class TestConfigFlowDiscover:
    """Test discover step of config flow."""

    @pytest.mark.asyncio
    async def test_async_step_discover_success(self):
        """Test successful device discovery."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._api_url = "https://api.example.com"
        flow._app_id = "test_id"
        flow._app_secret = "test_secret"

        mock_device = MagicMock()
        mock_device.get_name.return_value = "Test Camera"
        mock_device.get_device_id.return_value = "device_123"

        flow._discover_service = MagicMock()
        flow._discover_service.async_discover_devices = AsyncMock(
            return_value={"device_123": mock_device}
        )

        result = await flow.async_step_discover()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "discover"
        assert CONF_DISCOVERED_DEVICE in result["data_schema"].schema

    @pytest.mark.asyncio
    async def test_async_step_discover_rate_limit(self):
        """Test discovery with rate limit error."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()

        flow._discover_service = MagicMock()
        flow._discover_service.async_discover_devices = AsyncMock(
            side_effect=ImouException("OP1013: exceed limit")
        )

        result = await flow.async_step_discover()

        # Should redirect to manual entry on rate limit
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "manual"

    @pytest.mark.asyncio
    async def test_async_step_discover_no_devices(self):
        """Test discovery with no devices found."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()

        flow._discover_service = MagicMock()
        flow._discover_service.async_discover_devices = AsyncMock(return_value={})

        result = await flow.async_step_discover()

        # Should redirect to manual entry
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "manual"

    @pytest.mark.asyncio
    async def test_async_step_discover_device_selection(self):
        """Test selecting a discovered device."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._api_url = "https://api.example.com"
        flow._app_id = "test_id"
        flow._app_secret = "test_secret"

        mock_device = MagicMock()
        mock_device.get_name.return_value = "Test Camera"
        mock_device.get_device_id.return_value = "device_123"

        flow._discovered_devices = {"device_123": mock_device}

        with (
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "async_create_entry") as mock_create,
        ):
            mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}

            result = await flow.async_step_discover(
                {CONF_DISCOVERED_DEVICE: "device_123", CONF_DEVICE_NAME: "My Camera"}
            )

        assert result["type"] == FlowResultType.CREATE_ENTRY


class TestConfigFlowManual:
    """Test manual step of config flow."""

    @pytest.mark.asyncio
    async def test_async_step_manual_success(self):
        """Test manual device entry with valid device ID."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._api_client = MagicMock()
        flow._api_url = "https://api.example.com"
        flow._app_id = "test_id"
        flow._app_secret = "test_secret"

        with (
            patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device,
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "async_create_entry") as mock_create,
        ):
            device_instance = mock_device.return_value
            device_instance.async_initialize = AsyncMock()
            device_instance.get_name.return_value = "Test Camera"
            device_instance.get_device_id.return_value = "device_123"

            mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}

            result = await flow.async_step_manual(
                {CONF_DEVICE_ID: "device_123", CONF_DEVICE_NAME: ""}
            )

        assert result["type"] == FlowResultType.CREATE_ENTRY

    @pytest.mark.asyncio
    async def test_async_step_manual_invalid_device(self):
        """Test manual device entry with invalid device ID."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._api_client = MagicMock()

        with patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device:
            device_instance = mock_device.return_value
            device_instance.async_initialize = AsyncMock(
                side_effect=ImouException("Device not found")
            )

            result = await flow.async_step_manual(
                {CONF_DEVICE_ID: "invalid_123", CONF_DEVICE_NAME: ""}
            )

        assert result["type"] == FlowResultType.FORM
        assert "base" in result["errors"]

    @pytest.mark.asyncio
    async def test_async_step_manual_rate_limit(self):
        """Test manual entry with rate limit creates entry anyway."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._api_client = MagicMock()
        flow._api_url = "https://api.example.com"
        flow._app_id = "test_id"
        flow._app_secret = "test_secret"

        with (
            patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device,
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "async_create_entry") as mock_create,
        ):
            device_instance = mock_device.return_value
            device_instance.async_initialize = AsyncMock(
                side_effect=ImouException("OP1013: exceed limit")
            )
            device_instance.get_name.return_value = "Test Camera"
            device_instance.get_device_id.return_value = "device_123"

            mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}

            result = await flow.async_step_manual(
                {CONF_DEVICE_ID: "device_123", CONF_DEVICE_NAME: ""}
            )

        # Should create entry despite rate limit
        assert result["type"] == FlowResultType.CREATE_ENTRY


class TestConfigFlowHelpers:
    """Test config flow helper methods."""

    @pytest.mark.asyncio
    async def test_create_entry_from_device_with_custom_name(self):
        """Test creating entry with custom device name."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._api_url = "https://api.example.com"
        flow._app_id = "test_id"
        flow._app_secret = "test_secret"

        mock_device = MagicMock()
        mock_device.get_name.return_value = "Default Name"
        mock_device.get_device_id.return_value = "device_123"

        with (
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "async_create_entry") as mock_create,
        ):
            mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}

            await flow._create_entry_from_device(
                mock_device, {CONF_DEVICE_NAME: "My Custom Name"}
            )

        mock_create.assert_called_once()
        call_args = mock_create.call_args
        assert call_args[1]["title"] == "My Custom Name"
        assert call_args[1]["data"][CONF_DEVICE_NAME] == "My Custom Name"

    @pytest.mark.asyncio
    async def test_create_entry_from_device_with_default_name(self):
        """Test creating entry with device's default name."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._api_url = "https://api.example.com"
        flow._app_id = "test_id"
        flow._app_secret = "test_secret"

        mock_device = MagicMock()
        mock_device.get_name.return_value = "Device Default Name"
        mock_device.get_device_id.return_value = "device_123"

        with (
            patch.object(flow, "async_set_unique_id"),
            patch.object(flow, "async_create_entry") as mock_create,
        ):
            mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}

            await flow._create_entry_from_device(mock_device, {CONF_DEVICE_NAME: ""})

        mock_create.assert_called_once()
        call_args = mock_create.call_args
        assert call_args[1]["title"] == "Device Default Name"


class TestOptionsFlow:
    """Test options flow."""

    @pytest.mark.asyncio
    async def test_async_get_options_flow(self):
        """Test async_get_options_flow returns options handler."""
        config_entry = MockConfigEntry(domain=DOMAIN, data={}, options={})
        options_flow = ImouFlowHandler.async_get_options_flow(config_entry)
        assert isinstance(options_flow, ImouOptionsFlowHandler)

    @pytest.mark.asyncio
    async def test_options_flow_init_show_form(self):
        """Test options flow shows form on init."""
        hass = MagicMock()
        config_entry = MockConfigEntry(
            domain=DOMAIN, data={}, options={OPTION_SCAN_INTERVAL: 900}
        )
        config_entry.add_to_hass(hass)

        flow = ImouOptionsFlowHandler()
        flow.hass = hass
        flow.handler = config_entry.entry_id

        result = await flow.async_step_init()

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "init"

    @pytest.mark.asyncio
    async def test_options_flow_update_options(self):
        """Test options flow updates options."""
        hass = MagicMock()
        config_entry = MockConfigEntry(
            domain=DOMAIN, data={}, options={OPTION_SCAN_INTERVAL: 900}
        )
        config_entry.add_to_hass(hass)

        flow = ImouOptionsFlowHandler()
        flow.hass = hass
        flow.handler = config_entry.entry_id

        result = await flow.async_step_init(
            {
                OPTION_SCAN_INTERVAL: 1800,
                OPTION_API_TIMEOUT: "30",
                OPTION_CALLBACK_URL: "https://example.com",
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY

    @pytest.mark.asyncio
    async def test_options_flow_sanitize_empty_strings(self):
        """Test options flow sanitizes empty strings to None."""
        hass = MagicMock()
        config_entry = MockConfigEntry(domain=DOMAIN, data={}, options={})
        config_entry.add_to_hass(hass)

        flow = ImouOptionsFlowHandler()
        flow.hass = hass
        flow.handler = config_entry.entry_id

        await flow.async_step_init(
            {
                OPTION_SCAN_INTERVAL: 900,
                OPTION_API_TIMEOUT: "",
                OPTION_CALLBACK_URL: "",
                OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD: "",
                OPTION_WAIT_AFTER_WAKE_UP: "",
            }
        )

        # Empty strings should be removed (converted to None, then filtered out)
        assert OPTION_API_TIMEOUT not in flow.options
        assert OPTION_CALLBACK_URL not in flow.options
        assert OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD not in flow.options
        assert OPTION_WAIT_AFTER_WAKE_UP not in flow.options

    @pytest.mark.asyncio
    async def test_options_flow_convert_numeric_values(self):
        """Test options flow converts numeric string values."""
        hass = MagicMock()
        config_entry = MockConfigEntry(domain=DOMAIN, data={}, options={})
        config_entry.add_to_hass(hass)

        flow = ImouOptionsFlowHandler()
        flow.hass = hass
        flow.handler = config_entry.entry_id

        await flow.async_step_init(
            {
                OPTION_SCAN_INTERVAL: 900,
                OPTION_API_TIMEOUT: "30",
                OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD: "2.5",
                OPTION_WAIT_AFTER_WAKE_UP: "5.0",
            }
        )

        # String values should be converted to int/float
        assert flow.options[OPTION_API_TIMEOUT] == 30
        assert flow.options[OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD] == 2.5
        assert flow.options[OPTION_WAIT_AFTER_WAKE_UP] == 5.0

    @pytest.mark.asyncio
    async def test_options_flow_invalid_numeric_values(self):
        """Test options flow handles invalid numeric values."""
        hass = MagicMock()
        config_entry = MockConfigEntry(domain=DOMAIN, data={}, options={})
        config_entry.add_to_hass(hass)

        flow = ImouOptionsFlowHandler()
        flow.hass = hass
        flow.handler = config_entry.entry_id

        await flow.async_step_init(
            {
                OPTION_SCAN_INTERVAL: 900,
                OPTION_API_TIMEOUT: "invalid",
                OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD: "not_a_float",
                OPTION_WAIT_AFTER_WAKE_UP: "bad_value",
            }
        )

        # Invalid values should be removed (converted to None, then filtered out)
        assert OPTION_API_TIMEOUT not in flow.options
        assert OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD not in flow.options
        assert OPTION_WAIT_AFTER_WAKE_UP not in flow.options
