"""Common entity mixins to reduce code duplication."""

import logging
from typing import Optional

_LOGGER: logging.Logger = logging.getLogger(__package__)


class DeviceClassMixin:
    """Mixin for common device class logic."""

    def _get_device_class_by_name(
        self, sensor_name: str, class_mapping: dict
    ) -> Optional[str]:
        """Get device class based on sensor name using a mapping.

        Args:
            sensor_name: Name of the sensor
            class_mapping: Dictionary mapping sensor names to device classes

        Returns:
            Device class string or None if not found
        """
        return class_mapping.get(sensor_name)


class StateUpdateMixin:
    """Mixin for common state update logic."""

    def _update_ha_state(self):
        """Update Home Assistant state and log the action."""
        self.async_write_ha_state()
        _LOGGER.debug(
            "[%s] Updated state for %s",
            self.device.get_name(),
            self.sensor_instance.get_description(),
        )
