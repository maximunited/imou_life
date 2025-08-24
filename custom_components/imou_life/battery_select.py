"""Battery optimization select platform for Imou."""

import logging
from typing import Optional
from unittest.mock import MagicMock

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MOTION_SENSITIVITY_LEVELS,
    POWER_MODES,
    RECORDING_QUALITY_OPTIONS,
    SLEEP_SCHEDULE_OPTIONS,
)
from .entity import ImouEntity

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


class ImouBatterySelect(ImouEntity, SelectEntity):
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
        # Create a mock sensor instance for the parent class
        sensor_instance = MagicMock()
        sensor_instance.get_name.return_value = select_type
        sensor_instance.get_description.return_value = description
        sensor_instance.get_state.return_value = None
        sensor_instance.get_attributes.return_value = {}

        super().__init__(coordinator, config_entry, sensor_instance, "select")
        self.select_type = select_type
        self._description = description
        self._options = options
        self._icon = icon
        self._attribute_name = attribute_name
        self._current_option = None

    @property
    def name(self) -> str:
        """Return the name of the select entity."""
        return f"{self.device.get_name()} {self._description}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.config_entry.entry_id}_{self.select_type}"

    @property
    def icon(self) -> str:
        """Return the icon of the select entity."""
        return self._icon

    @property
    def options(self) -> list[str]:
        """Return a list of options."""
        return self._options

    @property
    def current_option(self) -> Optional[str]:
        """Return the current selected option."""
        # Get current value from coordinator or config
        if hasattr(self.coordinator, "get_battery_optimization_status"):
            status = self.coordinator.get_battery_optimization_status()
            return status.get(self._attribute_name)

        # Fallback to config entry options
        return self.config_entry.options.get(self._attribute_name)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in self._options:
            _LOGGER.error("Invalid option %s for %s", option, self.select_type)
            return

        try:
            # Update the coordinator
            if (
                hasattr(self.coordinator, "set_power_mode")
                and self._attribute_name == "power_mode"
            ):
                await self.coordinator.set_power_mode(option)
            elif (
                hasattr(self.coordinator, "set_motion_sensitivity")
                and self._attribute_name == "motion_sensitivity"
            ):
                await self.coordinator.set_motion_sensitivity(option)
            elif (
                hasattr(self.coordinator, "set_recording_quality")
                and self._attribute_name == "recording_quality"
            ):
                await self.coordinator.set_recording_quality(option)
            elif (
                hasattr(self.coordinator, "set_sleep_schedule")
                and self._attribute_name == "sleep_schedule"
            ):
                await self.coordinator.set_sleep_schedule(option)

            # Update config entry options
            options = dict(self.config_entry.options)
            options[self._attribute_name] = option
            self.coordinator.hass.config_entries.async_update_entry(
                self.config_entry, options=options
            )

            _LOGGER.info(
                "Set %s to %s for device %s",
                self._description,
                option,
                self.device.get_name(),
            )

        except Exception as exception:
            _LOGGER.error(
                "Error setting %s to %s: %s", self._description, option, str(exception)
            )

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
