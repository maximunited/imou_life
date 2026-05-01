"""Class to manage fetching data from the API."""

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from imouapi.device import ImouDevice
from imouapi.exceptions import ImouException

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ImouDataUpdateCoordinator(DataUpdateCoordinator):
    """Implement the DataUpdateCoordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: ImouDevice,
        scan_interval: int,
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

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=self.scan_inteval),
        )
        _LOGGER.debug(
            "Initialized coordinator. Scan interval %d seconds", self.scan_inteval
        )

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
                    "Invalid credentials, please reauthenticate"
                ) from exception

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
                    f"Scan interval adjusted to {self.update_interval.total_seconds()}s. "
                    f"Estimated reset: {self.rate_limit_estimated_reset.strftime('%H:%M:%S UTC')}. "
                    f"Error: {error_str}"
                )
                _LOGGER.warning(error_msg)
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
