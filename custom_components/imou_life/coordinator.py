"""Class to manage fetching data from the API."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
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
            return await self.device.async_get_data()
        except ImouException as exception:
            error_str = str(exception)
            # Provide helpful message for rate limit errors
            if "OP1013" in error_str or "exceed limit" in error_str.lower():
                error_msg = (
                    f"Imou API rate limit exceeded. "
                    f"The integration will retry on the next update cycle. "
                    f"Error: {error_str}"
                )
                _LOGGER.warning(error_msg)
            else:
                error_msg = f"Imou API error: {error_str}"
                _LOGGER.error(error_msg)
            raise UpdateFailed(error_msg) from exception
