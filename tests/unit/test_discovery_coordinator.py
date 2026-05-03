"""Tests for the Imou Discovery Coordinator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from imouapi.exceptions import ImouException

from custom_components.imou_life.const import (
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    DEFAULT_API_URL,
    DEFAULT_DISCOVERY_INTERVAL,
    DOMAIN,
    OPTION_DISCOVERY_INTERVAL,
)
from custom_components.imou_life.coordinator import ImouDiscoveryCoordinator


class TestImouDiscoveryCoordinator:
    """Test the Imou Discovery Coordinator."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        return MagicMock()

    @pytest.fixture
    def mock_config_entry(self):
        """Create a mock config entry."""
        entry = MagicMock()
        entry.entry_id = "test_entry_id"
        entry.data = {
            CONF_APP_ID: "test_app_id",
            CONF_APP_SECRET: "test_app_secret",
            CONF_API_URL: DEFAULT_API_URL,
        }
        entry.options = {}
        return entry

    @pytest.fixture
    def mock_hass(self):
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        hass.config_entries.async_entries = MagicMock(return_value=[])
        hass.config_entries.flow.async_init = AsyncMock()
        return hass

    @pytest.fixture
    def coordinator(self, mock_hass, mock_api_client, mock_config_entry):
        """Create a discovery coordinator instance."""
        return ImouDiscoveryCoordinator(mock_hass, mock_api_client, mock_config_entry)

    def test_coordinator_initialization(self, coordinator, mock_config_entry):
        """Test coordinator initialization."""
        assert coordinator.api_client is not None
        assert coordinator.entry == mock_config_entry
        assert coordinator.discovered_devices == {}
        assert coordinator.name == f"{DOMAIN}_discovery"

    def test_coordinator_default_update_interval(self, coordinator):
        """Test coordinator uses default update interval."""
        from datetime import timedelta

        assert coordinator.update_interval == timedelta(
            seconds=DEFAULT_DISCOVERY_INTERVAL
        )

    def test_coordinator_custom_update_interval(
        self, mock_hass, mock_api_client, mock_config_entry
    ):
        """Test coordinator uses custom update interval from options."""
        from datetime import timedelta

        mock_config_entry.options = {OPTION_DISCOVERY_INTERVAL: 1800}
        coordinator = ImouDiscoveryCoordinator(
            mock_hass, mock_api_client, mock_config_entry
        )
        assert coordinator.update_interval == timedelta(seconds=1800)

    @pytest.mark.asyncio
    async def test_async_update_data_no_devices(self, coordinator):
        """Test update when no devices are discovered."""
        with patch(
            "custom_components.imou_life.coordinator.ImouDiscoverService"
        ) as mock_discover_service_class:
            mock_discover_service = MagicMock()
            mock_discover_service.async_discover_devices = AsyncMock(return_value={})
            mock_discover_service_class.return_value = mock_discover_service

            result = await coordinator._async_update_data()

            assert result == {}
            mock_discover_service.async_discover_devices.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_update_data_with_new_device(self, coordinator, mock_hass):
        """Test update when a new device is discovered."""
        mock_device = MagicMock()
        mock_device.get_name = MagicMock(return_value="Test Camera")

        with patch(
            "custom_components.imou_life.coordinator.ImouDiscoverService"
        ) as mock_discover_service_class:
            mock_discover_service = MagicMock()
            mock_discover_service.async_discover_devices = AsyncMock(
                return_value={"device_123": mock_device}
            )
            mock_discover_service_class.return_value = mock_discover_service

            result = await coordinator._async_update_data()

            assert result == {"device_123": mock_device}
            mock_discover_service.async_discover_devices.assert_called_once()
            # Should trigger discovery flow
            mock_hass.config_entries.flow.async_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_update_data_with_existing_device(self, coordinator, mock_hass):
        """Test update when discovered device already has a config entry."""
        mock_device = MagicMock()
        mock_device.get_name = MagicMock(return_value="Existing Camera")

        # Mock existing config entry
        existing_entry = MagicMock()
        existing_entry.data = {CONF_DEVICE_ID: "device_123"}
        mock_hass.config_entries.async_entries = MagicMock(
            return_value=[existing_entry]
        )

        with patch(
            "custom_components.imou_life.coordinator.ImouDiscoverService"
        ) as mock_discover_service_class:
            mock_discover_service = MagicMock()
            mock_discover_service.async_discover_devices = AsyncMock(
                return_value={"device_123": mock_device}
            )
            mock_discover_service_class.return_value = mock_discover_service

            result = await coordinator._async_update_data()

            assert result == {"device_123": mock_device}
            # Should NOT trigger discovery flow for existing device
            mock_hass.config_entries.flow.async_init.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_update_data_api_exception(self, coordinator):
        """Test update handles API exceptions gracefully."""
        with patch(
            "custom_components.imou_life.coordinator.ImouDiscoverService"
        ) as mock_discover_service_class:
            mock_discover_service = MagicMock()
            mock_discover_service.async_discover_devices = AsyncMock(
                side_effect=ImouException("API error")
            )
            mock_discover_service_class.return_value = mock_discover_service

            # Should not raise, just return empty dict
            result = await coordinator._async_update_data()

            assert result == {}
            mock_discover_service.async_discover_devices.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_update_data_rate_limit_exception(self, coordinator):
        """Test update handles rate limit exceptions gracefully."""
        with patch(
            "custom_components.imou_life.coordinator.ImouDiscoverService"
        ) as mock_discover_service_class:
            mock_discover_service = MagicMock()
            mock_discover_service.async_discover_devices = AsyncMock(
                side_effect=ImouException("OP1013 exceed limit")
            )
            mock_discover_service_class.return_value = mock_discover_service

            # Should not raise, just return empty dict
            result = await coordinator._async_update_data()

            assert result == {}

    @pytest.mark.asyncio
    async def test_handle_discovered_device_triggers_flow(self, coordinator, mock_hass):
        """Test that discovering a new device triggers the config flow."""
        mock_device = MagicMock()
        mock_device.get_name = MagicMock(return_value="New Camera")

        await coordinator._handle_discovered_device("device_456", mock_device)

        # Should trigger discovery flow
        mock_hass.config_entries.flow.async_init.assert_called_once_with(
            DOMAIN,
            context={"source": "discovery"},
            data={
                "device_id": "device_456",
                "device": mock_device,
                "api_credentials": {
                    "app_id": coordinator.entry.data[CONF_APP_ID],
                    "app_secret": coordinator.entry.data[CONF_APP_SECRET],
                    "api_url": coordinator.entry.data.get(
                        CONF_API_URL, DEFAULT_API_URL
                    ),
                },
            },
        )

    @pytest.mark.asyncio
    async def test_handle_discovered_device_without_get_name(
        self, coordinator, mock_hass
    ):
        """Test handling device that doesn't have get_name method."""
        mock_device = MagicMock(spec=[])  # Device without get_name method

        # Should not raise exception
        await coordinator._handle_discovered_device("device_789", mock_device)

        # Should still trigger discovery flow
        mock_hass.config_entries.flow.async_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_discovered_device_get_name_fails(
        self, coordinator, mock_hass
    ):
        """Test handling device where get_name raises exception."""
        mock_device = MagicMock()
        mock_device.get_name = MagicMock(side_effect=Exception("Name error"))

        # Should not raise exception
        await coordinator._handle_discovered_device("device_999", mock_device)

        # Should still trigger discovery flow
        mock_hass.config_entries.flow.async_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_devices_discovered(self, coordinator, mock_hass):
        """Test discovering multiple new devices in one poll."""
        mock_device_1 = MagicMock()
        mock_device_1.get_name = MagicMock(return_value="Camera 1")
        mock_device_2 = MagicMock()
        mock_device_2.get_name = MagicMock(return_value="Camera 2")
        mock_device_3 = MagicMock()
        mock_device_3.get_name = MagicMock(return_value="Camera 3")

        with patch(
            "custom_components.imou_life.coordinator.ImouDiscoverService"
        ) as mock_discover_service_class:
            mock_discover_service = MagicMock()
            mock_discover_service.async_discover_devices = AsyncMock(
                return_value={
                    "device_1": mock_device_1,
                    "device_2": mock_device_2,
                    "device_3": mock_device_3,
                }
            )
            mock_discover_service_class.return_value = mock_discover_service

            result = await coordinator._async_update_data()

            assert len(result) == 3
            # Should trigger discovery flow for each device
            assert mock_hass.config_entries.flow.async_init.call_count == 3

    @pytest.mark.asyncio
    async def test_mixed_new_and_existing_devices(self, coordinator, mock_hass):
        """Test discovering mix of new and existing devices."""
        mock_device_new = MagicMock()
        mock_device_new.get_name = MagicMock(return_value="New Camera")
        mock_device_existing = MagicMock()
        mock_device_existing.get_name = MagicMock(return_value="Existing Camera")

        # Mock existing config entry
        existing_entry = MagicMock()
        existing_entry.data = {CONF_DEVICE_ID: "device_existing"}
        mock_hass.config_entries.async_entries = MagicMock(
            return_value=[existing_entry]
        )

        with patch(
            "custom_components.imou_life.coordinator.ImouDiscoverService"
        ) as mock_discover_service_class:
            mock_discover_service = MagicMock()
            mock_discover_service.async_discover_devices = AsyncMock(
                return_value={
                    "device_new": mock_device_new,
                    "device_existing": mock_device_existing,
                }
            )
            mock_discover_service_class.return_value = mock_discover_service

            result = await coordinator._async_update_data()

            assert len(result) == 2
            # Should only trigger discovery flow for new device
            assert mock_hass.config_entries.flow.async_init.call_count == 1
            call_args = mock_hass.config_entries.flow.async_init.call_args
            assert call_args[1]["data"]["device_id"] == "device_new"
