"""Tests for __init__.py error handling and edge cases."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.imou_life import (
    _create_stale_device_repair_issue,
    _is_first_entry,
    _setup_discovery_coordinator,
    _transfer_discovery_to_next_entry,
    async_migrate_entry,
    async_setup_entry,
)
from custom_components.imou_life.const import (
    CONF_API_URL,
    CONF_DEVICE_ID,
    DEFAULT_API_URL,
    DOMAIN,
    OPTION_API_URL,
    OPTION_ENABLE_DISCOVERY,
)


class TestStaleDeviceHandling:
    """Test stale device detection and repair issue creation."""

    @pytest.mark.asyncio
    async def test_create_stale_device_repair_issue(self):
        """Test creating repair issue for stale device (covers lines 310-314)."""
        # Create mocks
        hass = MagicMock()
        hass.config_entries.flow.async_init = AsyncMock()

        entry = MagicMock()
        entry.entry_id = "test_entry_123"

        coordinator = MagicMock()
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.device.get_device_id.return_value = "device_123"
        coordinator.stale_device_last_error = "Device not found in cloud"

        # Call the function
        await _create_stale_device_repair_issue(hass, entry, coordinator)

        # Verify flow was initiated
        hass.config_entries.flow.async_init.assert_called_once_with(
            DOMAIN,
            context={"source": "repair_stale_device"},
            data={
                "entry_id": "test_entry_123",
                "device_name": "Test Camera",
                "device_id": "device_123",
                "error_message": "Device not found in cloud",
            },
        )

    @pytest.mark.asyncio
    async def test_stale_device_callback_triggered(self):
        """Test stale device callback is triggered (covers lines 72-73)."""
        with patch(
            "custom_components.imou_life._create_stale_device_repair_issue"
        ) as mock_create_repair:
            with patch(
                "custom_components.imou_life._setup_api_client_and_device"
            ) as mock_setup:
                with patch(
                    "custom_components.imou_life._setup_coordinator"
                ) as mock_coordinator:
                    with patch(
                        "custom_components.imou_life._initialize_device",
                        new_callable=AsyncMock,
                    ):
                        with patch("custom_components.imou_life._setup_platforms"):
                            # Setup mocks
                            hass = MagicMock()
                            entry = MagicMock()
                            entry.entry_id = "test_entry_123"
                            entry.data = {
                                CONF_DEVICE_ID: "device_123",
                                "name": "Test",
                                CONF_API_URL: DEFAULT_API_URL,
                                "app_id": "test",
                                "app_secret": "test",
                            }
                            entry.options = {}

                            api_client = MagicMock()
                            device = MagicMock()
                            mock_setup.return_value = (api_client, device)

                            coordinator_mock = MagicMock()
                            coordinator_mock.platforms = []
                            mock_coordinator.return_value = coordinator_mock

                            # Track the callback
                            stale_device_callback = None

                            def capture_callback(event_type, callback):
                                nonlocal stale_device_callback
                                if "stale_device" in event_type:
                                    stale_device_callback = callback
                                return MagicMock()

                            hass.bus.async_listen = capture_callback

                            # Setup entry
                            await async_setup_entry(hass, entry)

                            # Trigger the stale device event
                            assert stale_device_callback is not None
                            event = MagicMock()
                            event.data = {"entry_id": "test_entry_123"}
                            await stale_device_callback(event)

                            # Verify repair issue was created with correct arguments
                            mock_create_repair.assert_called_once_with(
                                hass, entry, coordinator_mock
                            )


class TestDiscoveryHandling:
    """Test discovery coordinator setup and transfer logic."""

    def test_is_first_entry_true(self):
        """Test _is_first_entry when entry is first (covers line 331)."""
        hass = MagicMock()
        entry1 = MagicMock()
        entry1.entry_id = "entry_1"
        entry2 = MagicMock()
        entry2.entry_id = "entry_2"

        hass.config_entries.async_entries.return_value = [entry1, entry2]

        # First entry should return True
        assert _is_first_entry(hass, entry1) is True

    def test_is_first_entry_false(self):
        """Test _is_first_entry when entry is not first (covers line 331)."""
        hass = MagicMock()
        entry1 = MagicMock()
        entry1.entry_id = "entry_1"
        entry2 = MagicMock()
        entry2.entry_id = "entry_2"

        hass.config_entries.async_entries.return_value = [entry1, entry2]

        # Second entry should return False
        assert _is_first_entry(hass, entry2) is False

    def test_is_first_entry_no_entries(self):
        """Test _is_first_entry when no entries exist."""
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "entry_1"

        hass.config_entries.async_entries.return_value = []

        # Should return True when no entries exist
        assert _is_first_entry(hass, entry) is True

    @pytest.mark.asyncio
    async def test_setup_discovery_coordinator_disabled(self):
        """Test discovery setup when disabled (covers lines 340-341)."""
        hass = MagicMock()
        api_client = MagicMock()
        entry = MagicMock()
        entry.options = {OPTION_ENABLE_DISCOVERY: False}

        with patch("custom_components.imou_life._LOGGER") as mock_logger:
            result = await _setup_discovery_coordinator(hass, api_client, entry)

            # Should return None when disabled
            assert result is None
            # Should log debug message
            mock_logger.debug.assert_called_once()
            assert "disabled" in mock_logger.debug.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_setup_discovery_coordinator_default_enabled(self):
        """Test discovery setup with default enabled setting."""
        hass = MagicMock()
        api_client = MagicMock()
        entry = MagicMock()
        entry.options = {}  # No explicit option, should use default

        with patch(
            "custom_components.imou_life.ImouDiscoveryCoordinator"
        ) as mock_coordinator_class:
            mock_coordinator = MagicMock()
            mock_coordinator_class.return_value = mock_coordinator

            result = await _setup_discovery_coordinator(hass, api_client, entry)

            # Should create coordinator when using default (enabled)
            assert result == mock_coordinator
            mock_coordinator_class.assert_called_once_with(hass, api_client, entry)

    @pytest.mark.asyncio
    async def test_transfer_discovery_to_next_entry(self):
        """Test discovery transfer to next entry (covers lines 354-368)."""
        hass = MagicMock()
        hass.config_entries.async_reload = AsyncMock()

        entry1 = MagicMock()
        entry1.entry_id = "entry_1"
        entry2 = MagicMock()
        entry2.entry_id = "entry_2"

        hass.config_entries.async_entries.return_value = [entry1, entry2]
        hass.data = {DOMAIN: {"discovery": MagicMock()}}

        with patch("custom_components.imou_life._LOGGER") as mock_logger:
            await _transfer_discovery_to_next_entry(hass, entry1)

            # Should set discovery to None
            assert hass.data[DOMAIN]["discovery"] is None

            # Should reload next entry
            hass.config_entries.async_reload.assert_called_once_with("entry_2")

            # Should log the transfer
            mock_logger.debug.assert_called_once()
            assert "transferring discovery" in mock_logger.debug.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_transfer_discovery_no_remaining_entries(self):
        """Test discovery transfer when no remaining entries."""
        hass = MagicMock()
        hass.config_entries.async_reload = AsyncMock()
        entry = MagicMock()
        entry.entry_id = "entry_1"

        hass.config_entries.async_entries.return_value = [entry]
        original_discovery = MagicMock()
        hass.data = {DOMAIN: {"discovery": original_discovery}}

        await _transfer_discovery_to_next_entry(hass, entry)

        # Should not reload any entries when no remaining entries
        hass.config_entries.async_reload.assert_not_called()
        # Discovery should remain unchanged (not set to None)
        assert hass.data[DOMAIN]["discovery"] is original_discovery

    @pytest.mark.asyncio
    async def test_cleanup_discovery_callback_triggered(self):
        """Test cleanup_discovery callback is triggered (covers lines 97-98)."""
        with patch(
            "custom_components.imou_life._transfer_discovery_to_next_entry"
        ) as mock_transfer:
            with patch(
                "custom_components.imou_life._setup_api_client_and_device"
            ) as mock_setup:
                with patch(
                    "custom_components.imou_life._setup_coordinator"
                ) as mock_coordinator:
                    with patch(
                        "custom_components.imou_life._initialize_device",
                        new_callable=AsyncMock,
                    ):
                        with patch("custom_components.imou_life._setup_platforms"):
                            with patch(
                                "custom_components.imou_life._is_first_entry",
                                return_value=True,
                            ):
                                with patch(
                                    "custom_components.imou_life._setup_discovery_coordinator"
                                ):
                                    # Setup mocks
                                    hass = MagicMock()
                                    entry = MagicMock()
                                    entry.entry_id = "test_entry_123"
                                    entry.data = {
                                        CONF_DEVICE_ID: "device_123",
                                        "name": "Test",
                                        CONF_API_URL: DEFAULT_API_URL,
                                        "app_id": "test",
                                        "app_secret": "test",
                                    }
                                    entry.options = {}

                                    api_client = MagicMock()
                                    device = MagicMock()
                                    mock_setup.return_value = (api_client, device)

                                    coordinator_mock = MagicMock()
                                    coordinator_mock.platforms = []
                                    mock_coordinator.return_value = coordinator_mock

                                    # Track the callback
                                    cleanup_callback = None

                                    def capture_callback(event_type, callback):
                                        nonlocal cleanup_callback
                                        if "entry_unload" in event_type:
                                            cleanup_callback = callback
                                        return MagicMock()

                                    hass.bus.async_listen = capture_callback

                                    # Setup entry
                                    await async_setup_entry(hass, entry)

                                    # Trigger the cleanup event
                                    assert cleanup_callback is not None
                                    event = MagicMock()
                                    event.data = {"entry_id": "test_entry_123"}
                                    await cleanup_callback(event)

                                    # Verify transfer was called
                                    mock_transfer.assert_called_once()


class TestConfigMigration:
    """Test config entry migration logic."""

    @pytest.mark.asyncio
    async def test_migrate_entry_version_1_to_2(self):
        """Test migration from version 1 to 2 (covers lines 454-459)."""
        hass = MagicMock()
        config_entry = MagicMock()
        config_entry.version = 1
        config_entry.data = {CONF_DEVICE_ID: "device_123", "app_id": "test"}
        config_entry.options = {OPTION_API_URL: "https://custom.url"}

        result = await async_migrate_entry(hass, config_entry)

        # Should succeed
        assert result is True

        # Should update to version 2
        assert config_entry.version == 3  # Goes through both migrations

        # Should have added API URL from options
        updated_data = hass.config_entries.async_update_entry.call_args[1]["data"]
        assert CONF_API_URL in updated_data
        assert updated_data[CONF_API_URL] == "https://custom.url"

    @pytest.mark.asyncio
    async def test_migrate_entry_version_1_no_option_api_url(self):
        """Test migration from version 1 without option API URL."""
        hass = MagicMock()
        config_entry = MagicMock()
        config_entry.version = 1
        config_entry.data = {CONF_DEVICE_ID: "device_123"}
        config_entry.options = {}  # No API URL option

        result = await async_migrate_entry(hass, config_entry)

        # Should succeed
        assert result is True

        # Should use default API URL
        updated_data = hass.config_entries.async_update_entry.call_args[1]["data"]
        assert updated_data[CONF_API_URL] == DEFAULT_API_URL

    @pytest.mark.asyncio
    async def test_migrate_entry_version_2_to_3(self):
        """Test migration from version 2 to 3 (covers lines 461-467)."""
        hass = MagicMock()
        config_entry = MagicMock()
        config_entry.version = 2
        config_entry.data = {
            CONF_DEVICE_ID: "device_123",
            CONF_API_URL: "",  # Empty API URL
        }
        config_entry.options = {OPTION_API_URL: "https://custom.url"}

        result = await async_migrate_entry(hass, config_entry)

        # Should succeed
        assert result is True

        # Should update to version 3
        assert config_entry.version == 3

        # Should replace empty API URL with default
        updated_data = hass.config_entries.async_update_entry.call_args[1]["data"]
        assert updated_data[CONF_API_URL] == DEFAULT_API_URL

        # Should remove OPTION_API_URL from options
        updated_options = hass.config_entries.async_update_entry.call_args[1]["options"]
        assert OPTION_API_URL not in updated_options

    @pytest.mark.asyncio
    async def test_migrate_entry_version_2_with_valid_api_url(self):
        """Test migration from version 2 with valid API URL."""
        hass = MagicMock()
        config_entry = MagicMock()
        config_entry.version = 2
        config_entry.data = {
            CONF_DEVICE_ID: "device_123",
            CONF_API_URL: "https://custom.url",  # Valid API URL
        }
        config_entry.options = {OPTION_API_URL: "https://old.url"}

        result = await async_migrate_entry(hass, config_entry)

        # Should succeed
        assert result is True

        # API URL should remain unchanged (not empty)
        updated_data = hass.config_entries.async_update_entry.call_args[1]["data"]
        assert updated_data[CONF_API_URL] == "https://custom.url"
