"""Select platform for Imou."""

import logging

from homeassistant.components.select import ENTITY_ID_FORMAT, SelectEntity

from .entity import ImouEntity
from .platform_setup import setup_platform

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Configure platform."""
    await setup_platform(
        hass, entry, "select", ImouSelect, ENTITY_ID_FORMAT, async_add_devices
    )


class ImouSelect(ImouEntity, SelectEntity):
    """imou select class."""

    @property
    def current_option(self):
        """Return current option."""
        return self.sensor_instance.get_current_option()

    @property
    def options(self):
        """Return available options."""
        return self.sensor_instance.get_available_options()

    async def async_select_option(self, option: str) -> None:
        """Se the option."""
        # control the switch
        await self.sensor_instance.async_select_option(option)
        # save the new state to the state machine (otherwise will be reset by HA
        # and set to the correct value only upon the next update)
        self.async_write_ha_state()
        _LOGGER.debug(
            "[%s] Set %s to %s",
            self.device.get_name(),
            self.sensor_instance.get_description(),
            option,
        )
