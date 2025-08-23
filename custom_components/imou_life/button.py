"""Button platform for Imou."""

import logging

from homeassistant.components.button import ENTITY_ID_FORMAT, ButtonEntity

from .entity import ImouEntity
from .entity_mixins import DeviceClassMixin
from .platform_setup import setup_platform

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Configure platform."""
    await setup_platform(
        hass, entry, "button", ImouButton, ENTITY_ID_FORMAT, async_add_devices
    )


class ImouButton(ImouEntity, ButtonEntity, DeviceClassMixin):
    """imou button class."""

    # Device class mapping
    DEVICE_CLASS_MAPPING = {"restartDevice": "restart"}

    async def async_press(self) -> None:
        """Handle the button press."""
        # press the button
        await self.sensor_instance.async_press()
        _LOGGER.debug(
            "[%s] Pressed %s",
            self.device.get_name(),
            self.sensor_instance.get_description(),
        )
        # ask the coordinator to refresh data to all the sensors
        if self.sensor_instance.get_name() == "refreshData":
            await self.coordinator.async_request_refresh()
        # refresh the motionAlarm sensor
        if self.sensor_instance.get_name() == "refreshAlarm":
            # update the motionAlarm sensor
            await self.coordinator.device.get_sensor_by_name(
                "motionAlarm"
            ).async_update()
            # ask HA to update its state based on the new value
            for entity in self.coordinator.entities:
                if entity.sensor_instance.get_name() in "motionAlarm":
                    await entity.async_update_ha_state()

    @property
    def device_class(self) -> str:
        """Device device class."""
        return self._get_device_class_by_name(
            self.sensor_instance.get_name(), self.DEVICE_CLASS_MAPPING
        )
