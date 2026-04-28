"""Battery optimization button platform for Imou."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .battery_entity import ImouBatteryEntity
from .const import (
    DEFAULT_AUTO_SLEEP,
    DEFAULT_BATTERY_THRESHOLD,
    DEFAULT_LED_INDICATORS,
    DEFAULT_MOTION_SENSITIVITY,
    DEFAULT_POWER_SAVING_MODE,
    DEFAULT_RECORDING_QUALITY,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Imou battery optimization button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Enter Sleep Mode Button
    enter_sleep_button = ImouBatteryButton(
        coordinator,
        entry,
        "enterSleepMode",
        "Enter Sleep Mode",
        "mdi:power-sleep",
        "enter_sleep_mode",
    )
    entities.append(enter_sleep_button)

    # Exit Sleep Mode Button
    exit_sleep_button = ImouBatteryButton(
        coordinator,
        entry,
        "exitSleepMode",
        "Exit Sleep Mode",
        "mdi:power-sleep",
        "exit_sleep_mode",
    )
    entities.append(exit_sleep_button)

    # Optimize Battery Button
    optimize_battery_button = ImouBatteryButton(
        coordinator,
        entry,
        "optimizeBattery",
        "Optimize Battery",
        "mdi:battery-settings",
        "optimize_battery",
    )
    entities.append(optimize_battery_button)

    # Reset Power Settings Button
    reset_power_button = ImouBatteryButton(
        coordinator,
        entry,
        "resetPowerSettings",
        "Reset Power Settings",
        "mdi:refresh-circle",
        "reset_power_settings",
    )
    entities.append(reset_power_button)

    if entities:
        async_add_entities(entities)
        _LOGGER.debug("Added %d battery optimization button entities", len(entities))


class ImouBatteryButton(ImouBatteryEntity, ButtonEntity):
    """Imou battery optimization button entity."""

    def __init__(
        self,
        coordinator,
        config_entry,
        button_type: str,
        description: str,
        icon: str,
        action_name: str,
    ):
        """Initialize the battery optimization button entity."""
        super().__init__(
            coordinator,
            config_entry,
            "button",
            description,
            icon,
            button_type,
        )
        self._action_name = action_name

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            if self._action_name == "enter_sleep_mode":
                if hasattr(self.coordinator, "enter_sleep_mode"):
                    await self.coordinator.enter_sleep_mode()
                else:
                    _LOGGER.warning("Coordinator does not support enter_sleep_mode")
                    return

            elif self._action_name == "exit_sleep_mode":
                if hasattr(self.coordinator, "exit_sleep_mode"):
                    await self.coordinator.exit_sleep_mode()
                else:
                    _LOGGER.warning("Coordinator does not support exit_sleep_mode")
                    return

            elif self._action_name == "optimize_battery":
                if hasattr(self.coordinator, "optimize_battery"):
                    await self.coordinator.optimize_battery()
                else:
                    _LOGGER.warning("Coordinator does not support optimize_battery")
                    return

            elif self._action_name == "reset_power_settings":
                if hasattr(self.coordinator, "reset_power_settings") and callable(
                    getattr(self.coordinator, "reset_power_settings")
                ):
                    try:
                        await self.coordinator.reset_power_settings()
                    except TypeError:
                        # Method exists but is not awaitable, use local implementation
                        await self._reset_power_settings()
                else:
                    await self._reset_power_settings()

            _LOGGER.info(
                "Executed %s action for device %s",
                self._description,
                self.coordinator.device.get_name(),
            )

        except Exception as exception:
            _LOGGER.error(
                "Error executing %s action: %s", self._description, str(exception)
            )

    async def _reset_power_settings(self):
        """Reset power settings to defaults."""
        try:
            # Reset config entry options to defaults
            options = dict(self.config_entry.options)
            options.update(
                {
                    "power_mode": DEFAULT_POWER_SAVING_MODE,
                    "motion_sensitivity": DEFAULT_MOTION_SENSITIVITY,
                    "recording_quality": DEFAULT_RECORDING_QUALITY,
                    "led_indicators": DEFAULT_LED_INDICATORS,
                    "auto_sleep": DEFAULT_AUTO_SLEEP,
                    "battery_threshold": DEFAULT_BATTERY_THRESHOLD,
                    "sleep_schedule": "never",
                }
            )

            self.coordinator.hass.config_entries.async_update_entry(
                self.config_entry, options=options
            )

            _LOGGER.info("Power settings reset to defaults")

        except Exception as exception:
            _LOGGER.error("Error resetting power settings: %s", str(exception))
            raise
