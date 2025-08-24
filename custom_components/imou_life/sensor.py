"""Sensor platform for Imou."""

from homeassistant.components.sensor import ENTITY_ID_FORMAT

from .entity import ImouEntity
from .entity_mixins import DeviceClassMixin
from .platform_setup import setup_platform


async def async_setup_entry(hass, entry, async_add_devices):
    """Configure platform."""
    await setup_platform(
        hass, entry, "sensor", ImouSensor, ENTITY_ID_FORMAT, async_add_devices
    )


class ImouSensor(ImouEntity, DeviceClassMixin):
    """imou sensor class."""

    # Device class mapping
    DEVICE_CLASS_MAPPING = {
        "lastAlarm": "timestamp",
        "battery": "battery",
        "batteryLevel": "battery",
        "batteryVoltage": "voltage",
        "powerConsumption": "power",
    }

    # Unit of measurement mapping
    UNIT_MAPPING = {
        "storageUsed": "%",
        "battery": "%",
        "batteryLevel": "%",
        "batteryVoltage": "V",
        "powerConsumption": "W",
        "sleepMode": "",
        "powerSavingStatus": "",
    }

    @property
    def device_class(self) -> str:
        """Device device class."""
        return self._get_device_class_by_name(
            self.sensor_instance.get_name(), self.DEVICE_CLASS_MAPPING
        )

    @property
    def unit_of_measurement(self) -> str:
        """Provide unit of measurement."""
        return self.UNIT_MAPPING.get(self.sensor_instance.get_name())

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.sensor_instance.get_state() is None:
            self.entity_available = False
        return self.sensor_instance.get_state()
