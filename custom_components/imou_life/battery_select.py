"""Battery optimization select platform for Imou."""

import logging
from typing import Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .battery_entity import ImouBatteryEntity
from .const import (
    DOMAIN,
    MOTION_SENSITIVITY_LEVELS,
    POWER_MODES,
    RECORDING_QUALITY_OPTIONS,
    SLEEP_SCHEDULE_OPTIONS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Imou battery optimization select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Power Mode Select
    power_mode_select = ImouBatterySelect(
        coordinator,
        entry,
        "powerMode",
        "Power Mode",
        POWER_MODES,
        "mdi:battery-settings",
        "power_mode",
    )
    entities.append(power_mode_select)

    # Motion Sensitivity Select
    motion_sensitivity_select = ImouBatterySelect(
        coordinator,
        entry,
        "motionSensitivityLevel",
        "Motion Sensitivity",
        MOTION_SENSITIVITY_LEVELS,
        "mdi:tune-vertical",
        "motion_sensitivity",
    )
    entities.append(motion_sensitivity_select)

    # Recording Quality Select
    recording_quality_select = ImouBatterySelect(
        coordinator,
        entry,
        "recordingQuality",
        "Recording Quality",
        RECORDING_QUALITY_OPTIONS,
        "mdi:video-quality",
        "recording_quality",
    )
    entities.append(recording_quality_select)

    # Sleep Schedule Select
    sleep_schedule_select = ImouBatterySelect(
        coordinator,
        entry,
        "sleepSchedule",
        "Sleep Schedule",
        SLEEP_SCHEDULE_OPTIONS,
        "mdi:clock-outline",
        "sleep_schedule",
    )
    entities.append(sleep_schedule_select)

    if entities:
        async_add_entities(entities)
        _LOGGER.debug("Added %d battery optimization select entities", len(entities))


class ImouBatterySelect(ImouBatteryEntity, SelectEntity):
    """Imou battery optimization select entity."""

    def __init__(
        self,
        coordinator,
        config_entry,
        select_type: str,
        description: str,
        options: list,
        icon: str,
        attribute_name: str,
    ):
        """Initialize the battery optimization select entity."""
        super().__init__(
            coordinator,
            config_entry,
            "select",
            description,
            icon,
            select_type,
        )
        self._options = options
        self._attribute_name = attribute_name

    @property
    def options(self) -> list[str]:
        """Return a list of options."""
        return self._options

    @property
    def current_option(self) -> Optional[str]:
        """Return the current selected option."""
        try:
            # Try to get current value from coordinator
            if hasattr(self.coordinator, "get_battery_optimization_status"):
                status = self.coordinator.get_battery_optimization_status()
                current = status.get(self._attribute_name)

                # Validate option is in allowed list
                if current and current in self._options:
                    return current

        except (AttributeError, KeyError, TypeError) as exception:
            _LOGGER.debug(
                "Failed to get current option from coordinator: %s", exception
            )

        # Fallback to config entry options
        try:
            config_option = self.config_entry.options.get(self._attribute_name)
            if config_option and config_option in self._options:
                return config_option
        except (AttributeError, KeyError, TypeError) as exception:
            _LOGGER.debug("Failed to get current option from config: %s", exception)

        # Return None if no valid option found
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._options:
            _LOGGER.error("Invalid option %s for %s", option, self.unique_id)
            return

        # Try to update the coordinator
        try:
            if self._attribute_name == "power_mode":
                if hasattr(self.coordinator, "set_power_mode"):
                    await self.coordinator.set_power_mode(option)
            elif self._attribute_name == "motion_sensitivity":
                if hasattr(self.coordinator, "set_motion_sensitivity"):
                    await self.coordinator.set_motion_sensitivity(option)
            elif self._attribute_name == "recording_quality":
                if hasattr(self.coordinator, "set_recording_quality"):
                    await self.coordinator.set_recording_quality(option)
            elif self._attribute_name == "sleep_schedule":
                if hasattr(self.coordinator, "set_sleep_schedule"):
                    await self.coordinator.set_sleep_schedule(option)
        except Exception as exception:
            _LOGGER.error(
                "Error setting %s to %s: %s", self._description, option, str(exception)
            )

        # Always update config entry options
        try:
            options = dict(self.config_entry.options)
            options[self._attribute_name] = option
            self.coordinator.hass.config_entries.async_update_entry(
                self.config_entry, options=options
            )

            _LOGGER.info(
                "Set %s to %s for device %s",
                self._description,
                option,
                self.coordinator.device.get_name(),
            )
        except Exception as exception:
            _LOGGER.error(
                "Error updating config for %s: %s", self._description, str(exception)
            )
