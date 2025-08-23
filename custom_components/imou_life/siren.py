"""Siren platform for Imou."""

import logging

from homeassistant.components.siren import SirenEntity, SirenEntityFeature

from .entity import ImouEntity
from .platform_setup import setup_platform

ENTITY_ID_FORMAT = "siren" + ".{}"
_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Configure platform."""
    await setup_platform(
        hass, entry, "siren", ImouSiren, ENTITY_ID_FORMAT, async_add_devices
    )


class ImouSiren(ImouEntity, SirenEntity):
    """imou siren class."""

    # siren features
    _attr_supported_features = SirenEntityFeature.TURN_OFF | SirenEntityFeature.TURN_ON

    @property
    def is_on(self):
        """Return true if the siren is on."""
        return self.sensor_instance.is_on()

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the siren."""
        await self.sensor_instance.async_turn_on()
        # save the new state to the state machine (otherwise will be reset by HA
        # and set to the correct value only upon the next update)
        self.async_write_ha_state()
        _LOGGER.debug(
            "[%s] Turned %s ON",
            self.device.get_name(),
            self.sensor_instance.get_description(),
        )

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the siren."""
        await self.sensor_instance.async_turn_off()
        # save the new state to the state machine (otherwise will be reset by HA
        # and set to the correct value only upon the next update)
        self.async_write_ha_state()
        _LOGGER.debug(
            "[%s] Turned %s OFF",
            self.device.get_name(),
            self.sensor_instance.get_description(),
        )

    async def async_toggle(self, **kwargs):  # pylint: disable=unused-argument
        """Toggle the siren."""
        await self.sensor_instance.async_toggle()
        # save the new state to the state machine (otherwise will be reset by HA
        # and set to the correct value only upon the next update)
        self.async_write_ha_state()
        _LOGGER.debug(
            "[%s] Toggled",
            self.device.get_name(),
        )
