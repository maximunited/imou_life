"""Tests for config flow discovery and discovery_confirm steps."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.data_entry_flow import FlowResultType
from imouapi.exceptions import ImouException

from custom_components.imou_life.config_flow import ImouFlowHandler
from custom_components.imou_life.const import CONF_DEVICE_ID, CONF_DEVICE_NAME


class TestDiscoverySteps:
    """Test automatic discovery confirmation flow."""

    @pytest.mark.asyncio
    async def test_discovery_confirm_creates_entry(self):
        """Confirmed discovery creates a config entry."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._device_id = "device_abc"
        flow._device = MagicMock()
        flow._device.get_name.return_value = "Garden Cam"
        flow._api_credentials = {
            "app_id": "app",
            "app_secret": "secret",
            "api_url": "https://api.example.com",
        }

        with (
            patch.object(flow, "async_create_entry") as mock_create,
            patch.object(flow, "async_set_unique_id", new_callable=AsyncMock),
        ):
            mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}

            result = await flow.async_step_discovery_confirm(
                {CONF_DEVICE_NAME: "Garden Cam"}
            )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        mock_create.assert_called_once()
        entry_data = mock_create.call_args[1]["data"]
        assert entry_data[CONF_DEVICE_ID] == "device_abc"
        assert entry_data[CONF_DEVICE_NAME] == "Garden Cam"

    @pytest.mark.asyncio
    async def test_discovery_confirm_uses_device_name_fallback(self):
        """Missing name falls back to device API name."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._device_id = "device_abc"
        flow._device = MagicMock()
        flow._device.get_name.return_value = "API Camera Name"
        flow._api_credentials = {
            "app_id": "app",
            "app_secret": "secret",
            "api_url": "https://api.example.com",
        }

        with (
            patch.object(flow, "async_create_entry") as mock_create,
            patch.object(flow, "async_set_unique_id", new_callable=AsyncMock),
        ):
            mock_create.return_value = {"type": FlowResultType.CREATE_ENTRY}

            await flow.async_step_discovery_confirm({CONF_DEVICE_NAME: ""})

        entry_data = mock_create.call_args[1]["data"]
        assert entry_data[CONF_DEVICE_NAME] == "API Camera Name"

    @pytest.mark.asyncio
    async def test_discovery_step_routes_to_confirm(self):
        """Discovery step stores info and shows confirmation."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        device = MagicMock()
        device.get_name.return_value = "Porch"

        with (
            patch.object(flow, "async_set_unique_id", new_callable=AsyncMock),
            patch.object(flow, "_abort_if_unique_id_configured"),
            patch.object(
                flow,
                "async_step_discovery_confirm",
                new_callable=AsyncMock,
                return_value={"type": FlowResultType.FORM},
            ) as mock_confirm,
        ):
            result = await flow.async_step_discovery(
                {
                    "device_id": "dev_1",
                    "device": device,
                    "api_credentials": {"app_id": "a", "app_secret": "s"},
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert flow._device_id == "dev_1"
        mock_confirm.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_discover_non_rate_limit_error_sets_base_error(self):
        """Non-rate-limit discovery errors surface on the discover form."""
        flow = ImouFlowHandler()
        flow.hass = MagicMock()
        flow._discovered_devices = {}
        flow._errors = {}

        exception = ImouException("connection failed")
        exception.get_title = MagicMock(return_value="connection_failed")

        discover_service = MagicMock()
        discover_service.async_discover_devices = AsyncMock(side_effect=exception)
        flow._discover_service = discover_service

        with patch.object(
            flow, "async_step_manual", new_callable=AsyncMock
        ) as mock_manual:
            mock_manual.return_value = {"type": FlowResultType.FORM}

            await flow.async_step_discover(None)

        assert flow._errors["base"] == "connection_failed"
        mock_manual.assert_awaited_once()
