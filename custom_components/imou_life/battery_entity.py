"""Base entity class for battery optimization features."""

import logging
import re

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


def _camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case for translation keys."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class ImouBatteryEntity(CoordinatorEntity):
    """Base class for Imou battery optimization entities."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        entity_type: str,
        description: str,
        unique_id_suffix: str,
    ) -> None:
        """Initialize the battery entity."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._entity_type = entity_type
        self._description = description
        self._unique_id_suffix = unique_id_suffix

        # Set translation key for dynamic icons
        self._attr_translation_key = _camel_to_snake(unique_id_suffix)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=self.coordinator.device.get_name(),
            manufacturer="Imou",
            model=(
                self.coordinator.device.get_model()
                if hasattr(self.coordinator.device, "get_model")
                else "Unknown"
            ),
        )

        # Add software version if available
        if hasattr(self.coordinator.device, "get_firmware"):
            device_info["sw_version"] = self.coordinator.device.get_firmware()

        # Add hardware version (device ID) if available
        if hasattr(self.coordinator.device, "get_device_id"):
            device_info["hw_version"] = self.coordinator.device.get_device_id()

        return device_info

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        device_name = self.coordinator.device.get_name()
        return f"{device_name} {self._description}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.config_entry.entry_id}_{self._unique_id_suffix}"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.device.get_status()
        )

    @property
    def sensor_type(self) -> str:
        """Return the sensor type (for binary_sensor entities)."""
        return self._unique_id_suffix

    @property
    def button_type(self) -> str:
        """Return the button type (for button entities)."""
        return self._unique_id_suffix

    @property
    def select_type(self) -> str:
        """Return the select type (for select entities)."""
        return self._unique_id_suffix

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        _LOGGER.debug("%s added to Home Assistant", self.name)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug("%s removed from Home Assistant", self.name)
