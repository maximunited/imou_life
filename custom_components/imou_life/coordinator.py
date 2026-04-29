"""Class to manage fetching data from the API."""

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
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

            # Update succeeded - clear error status
            self.is_rate_limited = False
            self.last_error_type = None
            self.last_error_message = None
            self.last_successful_update = dt_util.utcnow()

            return data

        except ImouException as exception:
            error_str = str(exception)

            # Check if this is a rate limit error
            if "OP1013" in error_str or "exceed limit" in error_str.lower():
                self.is_rate_limited = True
                self.rate_limit_count += 1
                self.last_error_type = "rate_limit"
                self.last_error_message = error_str

                error_msg = (
                    f"Imou API rate limit exceeded (#{self.rate_limit_count}). "
                    f"The integration will retry on the next update cycle. "
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
