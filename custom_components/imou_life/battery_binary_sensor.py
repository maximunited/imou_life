"""Battery optimization binary sensor platform for Imou."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Imou battery optimization binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Low Battery Binary Sensor
    low_battery_sensor = ImouBatteryBinarySensor(
        coordinator,
        entry,
        "lowBattery",
        "Low Battery",
        "mdi:battery-alert",
        "low_battery",
    )
    entities.append(low_battery_sensor)

    # Charging Binary Sensor
    charging_sensor = ImouBatteryBinarySensor(
        coordinator, entry, "charging", "Charging", "mdi:battery-charging", "charging"
    )
    entities.append(charging_sensor)

    # Power Saving Active Binary Sensor
    power_saving_sensor = ImouBatteryBinarySensor(
        coordinator,
        entry,
        "powerSavingActive",
        "Power Saving Active",
        "mdi:battery-saver",
        "power_saving_active",
    )
    entities.append(power_saving_sensor)

    # Sleep Mode Active Binary Sensor
    sleep_mode_sensor = ImouBatteryBinarySensor(
        coordinator,
        entry,
        "sleepModeActive",
        "Sleep Mode Active",
        "mdi:power-sleep",
        "sleep_mode_active",
    )
    entities.append(sleep_mode_sensor)

    if entities:
        async_add_entities(entities)
        _LOGGER.debug(
            "Added %d battery optimization binary sensor entities", len(entities)
        )


class ImouBatteryBinarySensor(ImouEntity, BinarySensorEntity):
    """Imou battery optimization binary sensor entity."""

    def __init__(
        self,
        coordinator,
        config_entry,
        sensor_type: str,
        description: str,
        icon: str,
        attribute_name: str,
    ):
        """Initialize the battery optimization binary sensor entity."""
        super().__init__(coordinator, config_entry, None, "binary_sensor")
        self.sensor_type = sensor_type
        self._description = description
        self._icon = icon
        self._attribute_name = attribute_name

    @property
    def name(self) -> str:
        """Return the name of the binary sensor entity."""
        return f"{self.device.get_name()} {self._description}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.config_entry.entry_id}_{self.sensor_type}"

    @property
    def icon(self) -> str:
        """Return the icon of the binary sensor entity."""
        return self._icon

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        try:
            if self._attribute_name == "low_battery":
                return self._is_low_battery()
            elif self._attribute_name == "charging":
                return self._is_charging()
            elif self._attribute_name == "power_saving_active":
                return self._is_power_saving_active()
            elif self._attribute_name == "sleep_mode_active":
                return self._is_sleep_mode_active()
            else:
                return False
        except Exception as exception:
            _LOGGER.error("Error getting binary sensor state: %s", str(exception))
            return False

    def _is_low_battery(self) -> bool:
        """Check if battery is low."""
        try:
            # Get battery level from coordinator
            if hasattr(self.coordinator, "get_battery_optimization_status"):
                status = self.coordinator.get_battery_optimization_status()
                battery_threshold = status.get("battery_threshold", 20)

                # Get current battery level (this would come from device data)
                # For now, use a mock value
                battery_level = 85  # Mock value

                return battery_level <= battery_threshold

            return False
        except Exception:
            return False

    def _is_charging(self) -> bool:
        """Check if device is charging."""
        try:
            # This would check the actual device charging state
            # For now, return False as mock
            return False
        except Exception:
            return False

    def _is_power_saving_active(self) -> bool:
        """Check if power saving mode is active."""
        try:
            if hasattr(self.coordinator, "get_battery_optimization_status"):
                status = self.coordinator.get_battery_optimization_status()
                return status.get("active", False)
            return False
        except Exception:
            return False

    def _is_sleep_mode_active(self) -> bool:
        """Check if sleep mode is active."""
        try:
            if hasattr(self.coordinator, "_is_sleep_mode_active"):
                return self.coordinator._is_sleep_mode_active()
            return False
        except Exception:
            return False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self.device.get_status()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        _LOGGER.debug("%s added to HA", self.name)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug("%s removed from HA", self.name)
