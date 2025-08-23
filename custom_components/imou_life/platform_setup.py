"""Common platform setup utilities for Imou integration."""

import logging
from collections.abc import Callable
from typing import Type

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .entity import ImouEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def setup_platform(
    hass: HomeAssistant,
    entry: ConfigEntry,
    platform_name: str,
    entity_class: Type[ImouEntity],
    entity_id_format: str,
    async_add_devices: Callable,
) -> None:
    """Common platform setup function to eliminate code duplication.

    Args:
        hass: Home Assistant instance
        entry: Configuration entry
        platform_name: Name of the platform (e.g., "binary_sensor", "sensor")
        entity_class: The entity class to instantiate
        entity_id_format: Format string for entity ID
        async_add_devices: Function to add devices to HA
    """
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device = coordinator.device
    entities = []

    for sensor_instance in device.get_sensors_by_platform(platform_name):
        entity = entity_class(coordinator, entry, sensor_instance, entity_id_format)
        entities.append(entity)
        coordinator.entities.append(entity)
        _LOGGER.debug(
            "[%s] Adding %s", device.get_name(), sensor_instance.get_description()
        )

    async_add_devices(entities)
