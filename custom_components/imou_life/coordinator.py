"""Class to manage fetching data from the API."""

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from imouapi.device import ImouDevice, ImouDiscoverService
from imouapi.exceptions import ImouException

from .const import (
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    DEFAULT_API_URL,
    DEFAULT_DISCOVERY_INTERVAL,
    DOMAIN,
    OPTION_DISCOVERY_INTERVAL,
    STALE_DEVICE_ERROR_PATTERNS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ImouDataUpdateCoordinator(DataUpdateCoordinator):
    """Implement the DataUpdateCoordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: ImouDevice,
        scan_interval: int,
        config_entry=None,
    ) -> None:
        """Initialize."""
        self.device = device
        self.scan_inteval = scan_interval
        self.platforms: list = []
        self.entities: list = []

        # Rate limit tracking
        self.is_rate_limited: bool = False
        self.rate_limit_count: int = 0
        self.last_error_type: str | None = None
        self.last_error_message: str | None = None
        self.last_successful_update: datetime | None = None
        self.rate_limit_start_time: datetime | None = None
        self.rate_limit_estimated_reset: datetime | None = None

        # Scan interval management
        self._original_scan_interval: int = scan_interval
        self._is_interval_adjusted: bool = False

        # Stale device tracking
        self.stale_device_suspected: bool = False
        self.stale_device_failure_count: int = 0
        self.stale_device_last_error: str | None = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self.scan_inteval),
        )

        # Set config_entry AFTER super().__init__() to avoid it being reset
        self.config_entry = config_entry

        _LOGGER.debug(
            "Initialized coordinator. Scan interval %d seconds", self.scan_inteval
        )

    def _is_stale_device_error(self, error_str: str) -> bool:
        """Check if error indicates device no longer exists."""
        error_lower = error_str.lower()

        # Must NOT be an auth error (those go to reauth)
        auth_patterns = ["authentication failed", "token expired", "invalid app"]
        if any(p in error_lower for p in auth_patterns):
            return False

        # Check for stale device patterns
        return any(pattern in error_lower for pattern in STALE_DEVICE_ERROR_PATTERNS)

    async def _async_update_data(self):
        """HA calls this every DEFAULT_SCAN_INTERVAL to run the update."""
        try:
            data = await self.device.async_get_data()

            # Update succeeded - check if recovering from rate limit
            was_rate_limited = self.is_rate_limited
            self.is_rate_limited = False
            self.last_error_type = None
            self.last_error_message = None
            self.last_successful_update = dt_util.utcnow()

            # Reset stale device tracking on successful update
            self.stale_device_suspected = False
            self.stale_device_failure_count = 0
            self.stale_device_last_error = None

            # Restore original scan interval if it was adjusted
            if was_rate_limited and self._is_interval_adjusted:
                self._restore_scan_interval()
                self.rate_limit_start_time = None
                self.rate_limit_estimated_reset = None

            return data

        except ImouException as exception:
            error_str = str(exception)

            # Check for authentication errors first
            auth_error_patterns = [
                "authentication failed",
                "invalid credentials",
                "invalid app",
                "token expired",
                "unauthorized",
                "op1002",  # Common auth error code in Imou API
            ]
            if any(pattern in error_str.lower() for pattern in auth_error_patterns):
                # Set error tracking fields before raising
                self.is_rate_limited = False
                self.last_error_type = "auth_error"
                self.last_error_message = error_str

                raise ConfigEntryAuthFailed(
                    translation_domain=DOMAIN, translation_key="invalid_credentials"
                ) from exception

            # Check for stale device errors (device no longer exists on account)
            if self._is_stale_device_error(error_str):
                from .const import STALE_DEVICE_FAILURE_THRESHOLD

                self.stale_device_failure_count += 1
                self.stale_device_last_error = error_str

                # Fire event only when first reaching threshold (prevent spam)
                if (
                    self.stale_device_failure_count >= STALE_DEVICE_FAILURE_THRESHOLD
                    and not self.stale_device_suspected
                ):
                    self.stale_device_suspected = True
                    # Trigger repair issue creation via event
                    if self.config_entry is not None:
                        self.hass.bus.async_fire(
                            f"{DOMAIN}_stale_device_detected",
                            {"entry_id": self.config_entry.entry_id},
                        )

                error_msg = (
                    f"Device may no longer exist on account "
                    f"(failure {self.stale_device_failure_count}/{STALE_DEVICE_FAILURE_THRESHOLD}): "
                    f"{error_str}"
                )
                _LOGGER.warning(error_msg)
                raise UpdateFailed(error_msg) from exception

            # Non-stale error: reset stale tracking (ensures consecutive failures)
            self.stale_device_failure_count = 0
            self.stale_device_suspected = False
            self.stale_device_last_error = None

            # Check if this is a rate limit error
            if "OP1013" in error_str or "exceed limit" in error_str.lower():
                now = dt_util.utcnow()

                # Track when rate limiting started
                if not self.is_rate_limited:
                    self.rate_limit_start_time = now
                    # Imou API typically resets hourly, estimate next hour
                    self.rate_limit_estimated_reset = now + timedelta(hours=1)

                self.is_rate_limited = True
                self.rate_limit_count += 1
                self.last_error_type = "rate_limit"
                self.last_error_message = error_str

                # Adjust scan interval to reduce API calls
                self._adjust_scan_interval_for_rate_limit()

                error_msg = (
                    f"Imou API rate limit exceeded (#{self.rate_limit_count}). "
                    f"Polling paused until {self.rate_limit_estimated_reset.isoformat()}"
                )
                _LOGGER.warning(error_msg)
                raise UpdateFailed(error_msg) from exception
            else:
                self.is_rate_limited = False
                self.last_error_type = "api_error"
                self.last_error_message = error_str

                error_msg = f"Imou API error: {error_str}"
                _LOGGER.error(error_msg)
                raise UpdateFailed(error_msg) from exception

    def _adjust_scan_interval_for_rate_limit(self):
        """Increase scan interval when rate limited to reduce API calls."""
        if not self._is_interval_adjusted:
            # Double the scan interval (e.g., 15min -> 30min)
            new_interval = self._original_scan_interval * 2
            self.update_interval = timedelta(seconds=new_interval)
            self._is_interval_adjusted = True

            _LOGGER.info(
                "Adjusted scan interval from %ds to %ds due to rate limiting",
                self._original_scan_interval,
                new_interval,
            )

    def _restore_scan_interval(self):
        """Restore original scan interval after rate limit clears."""
        if self._is_interval_adjusted:
            self.update_interval = timedelta(seconds=self._original_scan_interval)
            self._is_interval_adjusted = False

            _LOGGER.info(
                "Restored original scan interval to %ds (rate limit cleared)",
                self._original_scan_interval,
            )


class ImouDiscoveryCoordinator(DataUpdateCoordinator):
    """Coordinator for discovering new devices."""

    def __init__(self, hass: HomeAssistant, api_client, entry) -> None:
        """Initialize discovery coordinator."""
        self.api_client = api_client
        self.entry = entry
        self.discovered_devices = {}

        # Get discovery interval from options
        discovery_interval = entry.options.get(
            OPTION_DISCOVERY_INTERVAL, DEFAULT_DISCOVERY_INTERVAL
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_discovery",
            update_interval=timedelta(seconds=discovery_interval),
        )

        _LOGGER.debug(
            "Initialized discovery coordinator. Poll interval %d seconds",
            discovery_interval,
        )

    async def _async_update_data(self):
        """Poll for new devices."""
        try:
            _LOGGER.debug("Polling for new Imou devices...")
            discover_service = ImouDiscoverService(self.api_client)
            devices = await discover_service.async_discover_devices()

            # Check for new devices
            for device_id, device in devices.items():
                await self._handle_discovered_device(device_id, device)

            return devices
        except ImouException as err:
            # Log but don't fail - discovery is not critical
            _LOGGER.debug(
                "Device discovery poll failed (will retry next cycle): %s", err
            )
            return {}

    async def _handle_discovered_device(self, device_id, device):
        """Handle a discovered device."""
        # Check if device already has config entry
        existing_entries = self.hass.config_entries.async_entries(DOMAIN)
        for entry in existing_entries:
            if entry.data.get(CONF_DEVICE_ID) == device_id:
                return  # Device already configured

        # New device found - trigger discovery flow
        device_name = "Unknown"
        try:
            if hasattr(device, "get_name"):
                device_name = device.get_name()
        except Exception:
            pass  # If get_name() fails, use "Unknown"

        _LOGGER.info(
            "New Imou device discovered: %s (%s). Starting confirmation flow.",
            device_name,
            device_id,
        )

        await self.hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "discovery"},
            data={
                "device_id": device_id,
                "device": device,
                "api_credentials": {
                    "app_id": self.entry.data[CONF_APP_ID],
                    "app_secret": self.entry.data[CONF_APP_SECRET],
                    "api_url": self.entry.data.get(CONF_API_URL, DEFAULT_API_URL),
                },
            },
        )
