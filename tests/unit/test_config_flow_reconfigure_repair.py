"""Tests for config flow reconfigure and stale-device repair steps."""

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
    """Config entry for reconfigure/repair flows."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_APP_ID: "app_id",
            CONF_APP_SECRET: "app_secret",
            CONF_DEVICE_ID: "device_123",
            CONF_DEVICE_NAME: "Front Door",
            CONF_API_URL: "https://openapi.easy4ip.com/openapi",
        },
        entry_id="test_entry_123",
        title="Front Door",
        version=3,
    )


@pytest.fixture
def mock_hass(mock_config_entry):
    """Mock Home Assistant with config entry helpers."""
    hass = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_get_entry = MagicMock(return_value=mock_config_entry)
    hass.config_entries.async_update_entry = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    hass.config_entries.async_remove = AsyncMock()
    return hass


class TestReconfigureFlow:
    """Test reconfiguration flow."""

    @pytest.mark.asyncio
    async def test_reconfigure_entry_not_found(self, mock_hass):
        """Abort when the config entry no longer exists."""
        mock_hass.config_entries.async_get_entry.return_value = None
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": "missing_entry"}

        result = await flow.async_step_reconfigure({})

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "entry_not_found"

    @pytest.mark.asyncio
    async def test_reconfigure_shows_confirm_form(self, mock_hass, mock_config_entry):
        """Reconfigure redirects to the confirmation form."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": mock_config_entry.entry_id}

        result = await flow.async_step_reconfigure({})

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "reconfigure_confirm"

    @pytest.mark.asyncio
    async def test_reconfigure_success(self, mock_hass, mock_config_entry):
        """Successful reconfiguration updates credentials and reloads."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.context = {"entry_id": mock_config_entry.entry_id}
        flow.entry = mock_config_entry

        with (
            patch("custom_components.imou_life.config_flow.ImouAPIClient") as mock_api,
            patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device,
            patch("custom_components.imou_life.config_flow.async_get_clientsession"),
        ):
            mock_api.return_value.async_connect = AsyncMock()
            mock_device.return_value.async_initialize = AsyncMock()

            result = await flow.async_step_reconfigure_confirm(
                {
                    CONF_APP_ID: "new_app_id",
                    CONF_APP_SECRET: "new_secret",
                    CONF_API_SERVER: DEFAULT_API_SERVER,
                }
            )

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "reconfigure_successful"
        mock_hass.config_entries.async_update_entry.assert_called_once()
        mock_hass.config_entries.async_reload.assert_awaited_once_with(
            mock_config_entry.entry_id
        )

    @pytest.mark.asyncio
    async def test_reconfigure_custom_url_required(self, mock_hass, mock_config_entry):
        """Custom server without URL shows validation error."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.entry = mock_config_entry

        result = await flow.async_step_reconfigure_confirm(
            {
                CONF_APP_ID: "app_id",
                CONF_APP_SECRET: "secret",
                CONF_API_SERVER: "custom",
                CONF_API_URL: "",
            }
        )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "custom_url_required"

    @pytest.mark.asyncio
    async def test_reconfigure_invalid_credentials(self, mock_hass, mock_config_entry):
        """API auth failure maps to not_authorized error."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.entry = mock_config_entry

        with (
            patch("custom_components.imou_life.config_flow.ImouAPIClient") as mock_api,
            patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device,
            patch("custom_components.imou_life.config_flow.async_get_clientsession"),
        ):
            mock_api.return_value.async_connect = AsyncMock(
                side_effect=ImouException("invalid credentials")
            )
            mock_device.return_value.async_initialize = AsyncMock()

            result = await flow.async_step_reconfigure_confirm(
                {
                    CONF_APP_ID: "bad_id",
                    CONF_APP_SECRET: "bad_secret",
                    CONF_API_SERVER: DEFAULT_API_SERVER,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "not_authorized"
        mock_hass.config_entries.async_update_entry.assert_not_called()
        mock_hass.config_entries.async_reload.assert_not_called()

    @pytest.mark.asyncio
    async def test_reconfigure_failure_does_not_persist(
        self, mock_hass, mock_config_entry
    ):
        """Failed validation must not update credentials or reload."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.entry = mock_config_entry

        with (
            patch("custom_components.imou_life.config_flow.ImouAPIClient") as mock_api,
            patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device,
            patch("custom_components.imou_life.config_flow.async_get_clientsession"),
        ):
            mock_api.return_value.async_connect = AsyncMock()
            mock_device.return_value.async_initialize = AsyncMock(
                side_effect=ImouException("invalid credentials")
            )

            result = await flow.async_step_reconfigure_confirm(
                {
                    CONF_APP_ID: "bad_id",
                    CONF_APP_SECRET: "bad_secret",
                    CONF_API_SERVER: DEFAULT_API_SERVER,
                }
            )

        assert result["type"] == FlowResultType.FORM
        mock_hass.config_entries.async_update_entry.assert_not_called()
        mock_hass.config_entries.async_reload.assert_not_called()

    @pytest.mark.asyncio
    async def test_reconfigure_rate_limit(self, mock_hass, mock_config_entry):
        """Rate limit during validation maps to rate_limit_exceeded."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.entry = mock_config_entry

        with (
            patch("custom_components.imou_life.config_flow.ImouAPIClient") as mock_api,
            patch("custom_components.imou_life.config_flow.ImouDevice") as mock_device,
            patch("custom_components.imou_life.config_flow.async_get_clientsession"),
        ):
            mock_api.return_value.async_connect = AsyncMock(
                side_effect=ImouException("OP1013 exceed limit")
            )
            mock_device.return_value.async_initialize = AsyncMock()

            result = await flow.async_step_reconfigure_confirm(
                {
                    CONF_APP_ID: "app_id",
                    CONF_APP_SECRET: "secret",
                    CONF_API_SERVER: DEFAULT_API_SERVER,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "rate_limit_exceeded"

    @pytest.mark.asyncio
    async def test_reconfigure_unexpected_error(self, mock_hass, mock_config_entry):
        """Unexpected exceptions map to generic_error."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.entry = mock_config_entry

        with (
            patch("custom_components.imou_life.config_flow.ImouAPIClient") as mock_api,
            patch("custom_components.imou_life.config_flow.async_get_clientsession"),
        ):
            mock_api.return_value.async_connect = AsyncMock(
                side_effect=RuntimeError("boom")
            )

            result = await flow.async_step_reconfigure_confirm(
                {
                    CONF_APP_ID: "app_id",
                    CONF_APP_SECRET: "secret",
                    CONF_API_SERVER: DEFAULT_API_SERVER,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert result["errors"]["base"] == "generic_error"


class TestRepairStaleDeviceFlow:
    """Test stale device repair flow."""

    @pytest.fixture
    def repair_flow(self, mock_hass, mock_config_entry):
        """Flow handler with stale-device repair context."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.init_data = {
            "entry_id": mock_config_entry.entry_id,
            "device_name": "Front Door",
            "device_id": "device_123",
            "error_message": "Device not found",
        }
        return flow

    @pytest.mark.asyncio
    async def test_repair_invalid_init_data(self, mock_hass):
        """Abort when repair data is not a dict."""
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.init_data = "invalid"

        result = await flow.async_step_repair_stale_device({})

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "invalid_data"

    @pytest.mark.asyncio
    async def test_repair_entry_not_found(self, mock_hass):
        """Abort when the config entry no longer exists."""
        mock_hass.config_entries.async_get_entry.return_value = None
        flow = ImouFlowHandler()
        flow.hass = mock_hass
        flow.init_data = {
            "entry_id": "missing",
            "device_name": "Camera",
            "device_id": "id",
            "error_message": "gone",
        }

        result = await flow.async_step_repair_stale_device({})

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "entry_not_found"

    @pytest.mark.asyncio
    async def test_repair_shows_form(self, repair_flow):
        """Show repair options when no user input yet."""
        result = await repair_flow.async_step_repair_stale_device(None)

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "repair_stale_device"

    @pytest.mark.asyncio
    async def test_repair_remove_device(
        self, repair_flow, mock_hass, mock_config_entry
    ):
        """Remove action deletes the config entry."""
        result = await repair_flow.async_step_repair_stale_device({"action": "remove"})

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "device_removed"
        mock_hass.config_entries.async_remove.assert_awaited_once_with(
            mock_config_entry.entry_id
        )

    @pytest.mark.asyncio
    async def test_repair_retry_connection(
        self, repair_flow, mock_hass, mock_config_entry
    ):
        """Retry action resets stale counters and reloads."""
        coordinator = MagicMock()
        coordinator.stale_device_failure_count = 3
        coordinator.stale_device_suspected = True
        mock_config_entry.runtime_data = coordinator

        result = await repair_flow.async_step_repair_stale_device({"action": "retry"})

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "retrying"
        assert coordinator.stale_device_failure_count == 0
        assert coordinator.stale_device_suspected is False
        mock_hass.config_entries.async_reload.assert_awaited_once_with(
            mock_config_entry.entry_id
        )

    @pytest.mark.asyncio
    async def test_repair_ignore_warning(self, repair_flow, mock_config_entry):
        """Ignore action clears stale tracking without reload."""
        coordinator = MagicMock()
        coordinator.stale_device_failure_count = 3
        coordinator.stale_device_suspected = True
        coordinator.stale_device_last_error = "Device not found"
        mock_config_entry.runtime_data = coordinator

        result = await repair_flow.async_step_repair_stale_device({"action": "ignore"})

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "ignored"
        assert coordinator.stale_device_failure_count == 0
        assert coordinator.stale_device_suspected is False
        assert coordinator.stale_device_last_error is None

    @pytest.mark.asyncio
    async def test_repair_retry_without_runtime_data(
        self, repair_flow, mock_hass, mock_config_entry
    ):
        """Retry still reloads when coordinator is not initialized."""
        mock_config_entry.runtime_data = None

        result = await repair_flow.async_step_repair_stale_device({"action": "retry"})

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "retrying"
        mock_hass.config_entries.async_reload.assert_awaited_once_with(
            mock_config_entry.entry_id
        )

    @pytest.mark.asyncio
    async def test_repair_ignore_without_runtime_data(
        self, repair_flow, mock_config_entry
    ):
        """Ignore succeeds when coordinator is not initialized."""
        mock_config_entry.runtime_data = None

        result = await repair_flow.async_step_repair_stale_device({"action": "ignore"})

        assert result["type"] == FlowResultType.ABORT
        assert result["reason"] == "ignored"
