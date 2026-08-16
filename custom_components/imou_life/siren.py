"""Siren platform for Imou."""

import logging

from homeassistant.components.siren import SirenEntity, SirenEntityFeature
from homeassistant.exceptions import HomeAssistantError
from imouapi.exceptions import ImouException

from .const import DOMAIN
from .entity import ImouEntity
from .helpers import exception_message
from .platform_setup import setup_platform

ENTITY_ID_FORMAT = "siren" + ".{}"
_LOGGER: logging.Logger = logging.getLogger(__package__)

# Serialize entity updates to prevent API rate limiting
PARALLEL_UPDATES = 1


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
        try:
            await self.sensor_instance.async_turn_on()
        except ImouException as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="siren_action_failed",
                translation_placeholders={
                    "action": "turn on",
                    "entity": self.sensor_instance.get_description(),
                    "error": exception_message(exception),
                },
            ) from exception
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
        try:
            await self.sensor_instance.async_turn_off()
        except ImouException as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="siren_action_failed",
                translation_placeholders={
                    "action": "turn off",
                    "entity": self.sensor_instance.get_description(),
                    "error": exception_message(exception),
                },
            ) from exception
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
        try:
            await self.sensor_instance.async_toggle()
        except ImouException as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="siren_action_failed",
                translation_placeholders={
                    "action": "toggle",
                    "entity": self.sensor_instance.get_description(),
                    "error": exception_message(exception),
                },
            ) from exception
        # save the new state to the state machine (otherwise will be reset by HA
        # and set to the correct value only upon the next update)
        self.async_write_ha_state()
        _LOGGER.debug(
            "[%s] Toggled",
            self.device.get_name(),
        )
