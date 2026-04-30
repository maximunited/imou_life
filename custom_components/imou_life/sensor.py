"""Sensor platform for Imou."""

from homeassistant.components.sensor import ENTITY_ID_FORMAT, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .entity import ImouEntity
from .entity_mixins import DeviceClassMixin
from .platform_setup import setup_platform


async def async_setup_entry(hass, entry, async_add_devices):
    """Configure platform."""
    # Set up regular device sensors
    await setup_platform(
        hass, entry, "sensor", ImouSensor, ENTITY_ID_FORMAT, async_add_devices
    )

    # Add API status diagnostic sensor
    coordinator = entry.runtime_data
    async_add_devices([ImouAPIStatusSensor(coordinator, entry)], True)


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


class ImouAPIStatusSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor showing API connection and rate limit status."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:api"
    _attr_has_entity_name = True
    _attr_translation_key = "api_status"

    def __init__(self, coordinator, config_entry):
        """Initialize the API status sensor."""
        super().__init__(coordinator)
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_api_status"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device.get_device_id())},
            "name": self.coordinator.device.get_name(),
            "manufacturer": "Imou",
            "model": self.coordinator.device.get_model(),
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.is_rate_limited:
            return "rate_limited"
        elif self.coordinator.last_error_type:
            return "error"
        elif self.coordinator.last_successful_update:
            return "ok"
        else:
            return "unknown"

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        attrs = {
            "rate_limited": self.coordinator.is_rate_limited,
            "rate_limit_count": self.coordinator.rate_limit_count,
            "scan_interval": int(self.coordinator.update_interval.total_seconds()),
            "scan_interval_adjusted": self.coordinator._is_interval_adjusted,
        }

        if self.coordinator.last_error_type:
            attrs["last_error_type"] = self.coordinator.last_error_type

        if self.coordinator.last_error_message:
            attrs["last_error_message"] = self.coordinator.last_error_message

        if self.coordinator.last_successful_update:
            attrs["last_successful_update"] = (
                self.coordinator.last_successful_update.isoformat()
            )

        if self.coordinator.rate_limit_start_time:
            attrs["rate_limit_started_at"] = (
                self.coordinator.rate_limit_start_time.isoformat()
            )

        if self.coordinator.rate_limit_estimated_reset:
            attrs["rate_limit_estimated_reset"] = (
                self.coordinator.rate_limit_estimated_reset.isoformat()
            )
            # Calculate time remaining
            now = self.coordinator.hass.data["core"].now()
            remaining = self.coordinator.rate_limit_estimated_reset - now
            attrs["rate_limit_reset_in_seconds"] = max(
                0, int(remaining.total_seconds())
            )

        return attrs
