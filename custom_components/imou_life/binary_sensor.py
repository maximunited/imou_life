"""Binary sensor platform for Imou."""

from homeassistant.components.binary_sensor import ENTITY_ID_FORMAT, BinarySensorEntity

from .entity import ImouEntity
from .entity_mixins import DeviceClassMixin
from .platform_setup import setup_platform


async def async_setup_entry(hass, entry, async_add_devices):
    """Configure platform."""
    await setup_platform(
        hass,
        entry,
        "binary_sensor",
        ImouBinarySensor,
        ENTITY_ID_FORMAT,
        async_add_devices,
    )


class ImouBinarySensor(ImouEntity, BinarySensorEntity, DeviceClassMixin):
    """imou binary sensor class."""

    # Device class mapping
    DEVICE_CLASS_MAPPING = {"motionAlarm": "motion"}

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self.sensor_instance.is_on()

    @property
    def device_class(self) -> str:
        """Device device class."""
        return self._get_device_class_by_name(
            self.sensor_instance.get_name(), self.DEVICE_CLASS_MAPPING
        )
