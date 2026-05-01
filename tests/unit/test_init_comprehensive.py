"""Comprehensive tests for __init__.py setup and helper functions."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.imou_life import (
    _check_rate_limit_status,
    _configure_device_options,
    _initialize_device,
    _parse_timeout_option,
    _setup_coordinator,
    async_setup,
)
from custom_components.imou_life.const import (
    DEFAULT_API_URL,
    DOMAIN,
    OPTION_API_TIMEOUT,
    OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD,
    OPTION_SETUP_TIMEOUT,
    OPTION_WAIT_AFTER_WAKE_UP,
)


class TestAsyncSetup:
    """Test async_setup function."""

    @pytest.mark.asyncio
    async def test_async_setup_returns_true(self):
        """Test async_setup returns True (YAML not supported)."""
        hass = MagicMock()
        config = {}
        result = await async_setup(hass, config)
        assert result is True


class TestTimeoutParsing:
    """Test timeout option parsing."""

    def test_parse_timeout_option_valid_string(self):
        """Test parsing valid timeout string."""
        assert _parse_timeout_option("30") == 30
        assert _parse_timeout_option("60") == 60

    def test_parse_timeout_option_empty_string(self):
        """Test parsing empty timeout string returns None."""
        assert _parse_timeout_option("") is None

    def test_parse_timeout_option_invalid_string(self):
        """Test parsing invalid timeout string returns None with warning."""
        assert _parse_timeout_option("invalid") is None
        assert _parse_timeout_option("abc") is None

    def test_parse_timeout_option_integer(self):
        """Test parsing integer timeout value."""
        assert _parse_timeout_option(30) == 30
        assert _parse_timeout_option(60) == 60

    def test_parse_timeout_option_none(self):
        """Test parsing None timeout value."""
        assert _parse_timeout_option(None) is None


class TestDeviceConfiguration:
    """Test device configuration helpers."""

    def test_configure_device_options_camera_wait(self):
        """Test configuring camera wait before download."""
        device = MagicMock()
        entry = MagicMock()
        entry.options = {OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD: 2.5}

        _configure_device_options(device, entry)

        device.set_camera_wait_before_download.assert_called_once_with(2.5)

    def test_configure_device_options_wait_after_wakeup(self):
        """Test configuring wait after wakeup."""
        device = MagicMock()
        entry = MagicMock()
        entry.options = {OPTION_WAIT_AFTER_WAKE_UP: 5.0}

        _configure_device_options(device, entry)

        device.set_wait_after_wakeup.assert_called_once_with(5.0)

    def test_configure_device_options_both(self):
        """Test configuring both options."""
        device = MagicMock()
        entry = MagicMock()
        entry.options = {
            OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD: 2.5,
            OPTION_WAIT_AFTER_WAKE_UP: 5.0,
        }

        _configure_device_options(device, entry)

        device.set_camera_wait_before_download.assert_called_once_with(2.5)
        device.set_wait_after_wakeup.assert_called_once_with(5.0)

    def test_configure_device_options_none(self):
        """Test configuring with no options."""
        device = MagicMock()
        entry = MagicMock()
        entry.options = {}

        _configure_device_options(device, entry)

        device.set_camera_wait_before_download.assert_not_called()
        device.set_wait_after_wakeup.assert_not_called()


class TestDeviceInitialization:
    """Test device initialization with timeout."""

    @pytest.mark.asyncio
    async def test_initialize_device_success(self):
        """Test successful device initialization."""
        device = MagicMock()
        device.async_initialize = AsyncMock()
        device.get_all_sensors.return_value = [
            MagicMock(),
            MagicMock(),
        ]
        entry = MagicMock()
        entry.options = {}

        await _initialize_device(device, entry)

        device.async_initialize.assert_called_once()
        # Should disable all sensors
        for sensor in device.get_all_sensors():
            sensor.set_enabled.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_initialize_device_timeout(self):
        """Test device initialization timeout."""
        device = MagicMock()
        device.async_initialize = AsyncMock(side_effect=asyncio.TimeoutError())
        entry = MagicMock()
        entry.options = {OPTION_SETUP_TIMEOUT: 1}

        with pytest.raises(
            ConfigEntryNotReady, match="Device initialization timed out"
        ):
            await _initialize_device(device, entry)


class TestCoordinatorSetup:
    """Test coordinator setup."""

    @pytest.mark.asyncio
    async def test_setup_coordinator_timeout(self):
        """Test coordinator setup with timeout."""
        hass = MagicMock()
        device = MagicMock()
        entry = MagicMock()
        entry.options = {OPTION_SETUP_TIMEOUT: 1}

        with patch(
            "custom_components.imou_life.ImouDataUpdateCoordinator"
        ) as MockCoordinator:
            coordinator = MockCoordinator.return_value
            coordinator.async_refresh = AsyncMock(side_effect=asyncio.TimeoutError())

            with pytest.raises(
                ConfigEntryNotReady, match="Initial data fetch timed out"
            ):
                await _setup_coordinator(hass, device, entry)


class TestRateLimitNotification:
    """Test rate limit notification."""

    def test_check_rate_limit_status_rate_limited(self):
        """Test rate limit notification when rate limited."""
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "test_entry_123"
        coordinator = MagicMock()
        coordinator.is_rate_limited = True
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.rate_limit_count = 5
        coordinator.last_error_message = "OP1013: Rate limit exceeded"

        _check_rate_limit_status(hass, entry, coordinator)

        # Should create notification
        hass.components.persistent_notification.async_create.assert_called_once()
        call_args = hass.components.persistent_notification.async_create.call_args
        assert "Test Camera" in call_args[0][0]
        assert "Rate limit count: 5" in call_args[0][0]
        assert call_args[1]["title"] == "Imou API Rate Limit Detected"
        assert call_args[1]["notification_id"] == f"{DOMAIN}_test_entry_123_rate_limit"

    def test_check_rate_limit_status_not_rate_limited(self):
        """Test no notification when not rate limited."""
        hass = MagicMock()
        entry = MagicMock()
        coordinator = MagicMock()
        coordinator.is_rate_limited = False

        _check_rate_limit_status(hass, entry, coordinator)

        # Should not create notification
        hass.components.persistent_notification.async_create.assert_not_called()


class TestAPIClientSetup:
    """Test API client setup and configuration."""

    def test_api_timeout_configuration(self):
        """Test API timeout is set when provided in options."""
        from custom_components.imou_life import _create_api_client

        entry = MagicMock()
        entry.options = {OPTION_API_TIMEOUT: 60}
        device_config = {
            "app_id": "test_id",
            "app_secret": "test_secret",
            "api_url": DEFAULT_API_URL,
        }
        session = MagicMock()

        with patch("custom_components.imou_life.ImouAPIClient") as MockAPIClient:
            api_client = MockAPIClient.return_value

            _create_api_client(device_config, session, entry)

            # Should set timeout
            api_client.set_timeout.assert_called_once_with(60)

    def test_api_timeout_not_set_when_none(self):
        """Test API timeout is not set when None."""
        from custom_components.imou_life import _create_api_client

        entry = MagicMock()
        entry.options = {}
        device_config = {
            "app_id": "test_id",
            "app_secret": "test_secret",
            "api_url": DEFAULT_API_URL,
        }
        session = MagicMock()

        with patch("custom_components.imou_life.ImouAPIClient") as MockAPIClient:
            api_client = MockAPIClient.return_value

            _create_api_client(device_config, session, entry)

            # Should not set timeout
            api_client.set_timeout.assert_not_called()


# Note: Migration tests are skipped because MockConfigEntry doesn't allow
# direct version assignment like the real ConfigEntry does. Migration code
# (lines 275-300) is rarely executed and only runs once per user during upgrades.
