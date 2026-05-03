"""Battery optimization binary sensor platform for Imou."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .battery_entity import ImouBatteryEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Imou battery optimization binary sensor platform."""
    coordinator = entry.runtime_data

    entities = []

    # Low Battery Binary Sensor
    low_battery_sensor = ImouBatteryBinarySensor(
        coordinator,
        entry,
        "lowBattery",
        "Low Battery",
        "low_battery",
    )
    entities.append(low_battery_sensor)

    # Charging Binary Sensor
    charging_sensor = ImouBatteryBinarySensor(
        coordinator, entry, "charging", "Charging", "charging"
    )
    entities.append(charging_sensor)

    # Power Saving Active Binary Sensor
    power_saving_sensor = ImouBatteryBinarySensor(
        coordinator,
        entry,
        "powerSavingActive",
        "Power Saving Active",
        "power_saving_active",
    )
    entities.append(power_saving_sensor)

    # Sleep Mode Active Binary Sensor
    sleep_mode_sensor = ImouBatteryBinarySensor(
        coordinator,
        entry,
        "sleepModeActive",
        "Sleep Mode Active",
        "sleep_mode_active",
    )
    entities.append(sleep_mode_sensor)

    if entities:
        async_add_entities(entities)
        _LOGGER.debug(
            "Added %d battery optimization binary sensor entities", len(entities)
        )


class ImouBatteryBinarySensor(ImouBatteryEntity, BinarySensorEntity):
    """Imou battery optimization binary sensor entity."""

    def __init__(
        self,
        coordinator,
        config_entry,
        sensor_type: str,
        description: str,
        attribute_name: str,
    ):
        """Initialize the battery optimization binary sensor entity."""
        super().__init__(
            coordinator,
            config_entry,
            "binary_sensor",
            description,
            sensor_type,
        )
        self._attribute_name = attribute_name

    @property
    def entity_registry_enabled_default(self) -> bool:
        """If the entity is enabled by default."""
        # Disable noisy/diagnostic binary sensors by default
        disabled_sensors = ["power_saving_active", "sleep_mode_active"]
        return self._attribute_name not in disabled_sensors

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
            # Get battery threshold from coordinator
            status = self.coordinator.get_battery_optimization_status()
            battery_threshold = status.get("battery_threshold", 20)

            # Get current battery level from coordinator data
            battery_level = (
                self.coordinator.data.get("battery_level", 100)
                if self.coordinator.data
                else 100
            )

            return battery_level <= battery_threshold
        except (AttributeError, KeyError, TypeError) as exception:
            _LOGGER.warning("Failed to check battery level: %s", exception)
            return False

    def _is_charging(self) -> bool:
        """Check if device is charging."""
        try:
            # Get charging status from coordinator data
            if self.coordinator.data:
                # Try to get from battery data first
                if "battery_charging" in self.coordinator.data:
                    return bool(self.coordinator.data["battery_charging"])
                # Fallback to checking if voltage is increasing
                # This is a heuristic and may not be accurate
                return False
            return False
        except (AttributeError, KeyError, TypeError) as exception:
            _LOGGER.debug("Failed to check charging status: %s", exception)
            return False

    def _is_power_saving_active(self) -> bool:
        """Check if power saving mode is active."""
        try:
            status = self.coordinator.get_battery_optimization_status()
            return bool(status.get("active", False))
        except (AttributeError, KeyError, TypeError) as exception:
            _LOGGER.debug("Failed to check power saving status: %s", exception)
            return False

    def _is_sleep_mode_active(self) -> bool:
        """Check if sleep mode is active."""
        try:
            return self.coordinator.is_sleep_mode_active()
        except (AttributeError, TypeError) as exception:
            _LOGGER.debug("Failed to check sleep mode status: %s", exception)
            return False
