"""Switch platform for Imou."""

import logging
from collections.abc import Callable

from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENABLED_SWITCHES, OPTION_CALLBACK_URL
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


# async def async_setup_entry(hass, entry, async_add_devices):
async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: Callable
):
    """Configure platform."""
    _LOGGER.debug("Setting up switch platform for entry %s", entry.entry_id)

    try:
        coordinator = hass.data[DOMAIN][entry.entry_id]
        device = coordinator.device
        sensors = []

        _LOGGER.debug("Getting switch sensors for device %s", device.get_name())
        switch_sensors = device.get_sensors_by_platform("switch")
        _LOGGER.debug("Found %d switch sensors", len(switch_sensors))

        for sensor_instance in switch_sensors:
            try:
                sensor = ImouSwitch(
                    coordinator, entry, sensor_instance, ENTITY_ID_FORMAT
                )
                sensors.append(sensor)
                coordinator.entities.append(sensor)
                _LOGGER.debug(
                    "[%s] Adding %s",
                    device.get_name(),
                    sensor_instance.get_description(),
                )
            except Exception as e:
                _LOGGER.error(
                    "Failed to create switch for sensor %s: %s",
                    sensor_instance.get_description(),
                    str(e),
                )
                continue

        if sensors:
            _LOGGER.debug("Adding %d switch entities", len(sensors))
            async_add_devices(sensors)
        else:
            _LOGGER.warning("No switch entities to add")

        _LOGGER.debug("Switch platform setup completed successfully")

    except Exception as e:
        _LOGGER.error("Failed to setup switch platform: %s", str(e))
        raise


class ImouSwitch(ImouEntity, SwitchEntity):
    """imou switch class."""

    @property
    def entity_registry_enabled_default(self) -> bool:
        """If the entity is enabled by default."""
        return self.sensor_instance.get_name() in ENABLED_SWITCHES

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self.sensor_instance.is_on()

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        # pushNotifications switch
        if self.sensor_instance.get_name() == "pushNotifications":
            callback_url = None
            # if a callback url is provided as an option, use it as is
            if (
                OPTION_CALLBACK_URL in self.config_entry.options
                and self.config_entry.options[OPTION_CALLBACK_URL] != ""
            ):
                callback_url = self.config_entry.options[OPTION_CALLBACK_URL]
            if callback_url is None:
                raise Exception("No callback url provided")
            _LOGGER.debug("Callback URL: %s", callback_url)
            await self.sensor_instance.async_turn_on(url=callback_url)
        # control all other switches
        else:
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
        """Turn off the switch."""
        # control the switch
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
        """Toggle the switch."""
        await self.sensor_instance.async_toggle()
        # save the new state to the state machine (otherwise will be reset by HA
        # and set to the correct value only upon the next update)
        self.async_write_ha_state()
        _LOGGER.debug(
            "[%s] Toggled",
            self.device.get_name(),
        )
