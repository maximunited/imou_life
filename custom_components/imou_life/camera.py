"""Camera platform for Imou."""

import logging
from collections.abc import Callable

import imouapi
from homeassistant.components.camera import (
    ENTITY_ID_FORMAT,
    Camera,
    CameraEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from imouapi.exceptions import ImouException

from .const import DOMAIN, ENABLED_CAMERAS
from .coordinator import ImouConfigEntry
from .helpers import camel_to_snake

_LOGGER: logging.Logger = logging.getLogger(__package__)


# Serialize entity updates to prevent API rate limiting
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: ImouConfigEntry, async_add_devices: Callable
):
    """Configure platform.

    PTZ entity services are registered in the integration's async_setup via
    service.async_register_platform_entity_service (not here).
    """
    coordinator = entry.runtime_data
    device = coordinator.device
    sensors = []
    for sensor_instance in device.get_sensors_by_platform("camera"):
        sensor = ImouCamera(coordinator, entry, sensor_instance, ENTITY_ID_FORMAT)
        sensors.append(sensor)
        coordinator.entities.append(sensor)
        _LOGGER.debug(
            "[%s] Adding %s", device.get_name(), sensor_instance.get_description()
        )
    async_add_devices(sensors)


class ImouCamera(Camera):
    """imou camera class using composition to avoid metaclass conflicts."""

    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, coordinator, config_entry, sensor_instance, entity_format):
        """Initialize."""
        super().__init__()

        # Store the coordinator and other attributes
        self._coordinator = coordinator
        self._config_entry = config_entry
        self._device = coordinator.device
        self._sensor_instance = sensor_instance

        # Generate entity ID
        from homeassistant.helpers.entity import async_generate_entity_id

        self._entity_id = async_generate_entity_id(
            entity_format,
            f"{self._device.get_name()}_{self._sensor_instance.get_name()}",
            hass=coordinator.hass,
        )

        # Entity availability tracking
        self._entity_available = None

        # Set translation key for dynamic icons
        self._attr_translation_key = camel_to_snake(self._sensor_instance.get_name())

    @property
    def entity_registry_enabled_default(self) -> bool:
        """If the entity is enabled by default."""
        return self._sensor_instance.get_name() in ENABLED_CAMERAS

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self._config_entry.entry_id + "_" + self._sensor_instance.get_name()

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": self._device.get_name(),
            "model": self._device.get_model(),
            "manufacturer": self._device.get_manufacturer(),
            "sw_version": self._device.get_firmware(),
            "hw_version": self._device.get_device_id(),
        }

    @property
    def available(self) -> bool:
        """Entity available."""
        # if the availability of the sensor is set, return it
        if self._entity_available is not None:
            return self._entity_available
        # otherwise return the availability of the device
        return self._coordinator.device.get_status()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._device.get_name()} {self._sensor_instance.get_description()}"

    @property
    def extra_state_attributes(self):
        """State attributes."""
        return self._sensor_instance.get_attributes()

    async def async_camera_image(self, width=None, height=None) -> bytes:
        """Return bytes of camera image."""
        _LOGGER.debug(
            "[%s] requested camera image",
            self._device.get_name(),
        )
        return await self._sensor_instance.async_get_image()

    async def stream_source(self) -> str:
        """Return the source of the stream."""
        stream_url = await self._sensor_instance.async_get_stream_url()
        _LOGGER.debug("Successfully got stream URL: %s", stream_url)
        return stream_url

    async def async_added_to_hass(self):
        """Entity added to HA (at startup or when re-enabled)."""
        await super().async_added_to_hass()
        _LOGGER.debug("%s added to HA", self.name)
        self._sensor_instance.set_enabled(True)
        # request an update of this sensor
        try:
            await self._sensor_instance.async_update()
        except imouapi.exceptions.ImouException as exception:
            _LOGGER.error("Imou exception: %s", str(exception))

    async def async_will_remove_from_hass(self):
        """Entity removed from HA (when disabled)."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug("%s removed from HA", self.name)
        self._sensor_instance.set_enabled(False)

    async def async_service_ptz_location(self, horizontal, vertical, zoom):
        """Perform PTZ location action."""
        _LOGGER.debug(
            "[%s] invoked PTZ location action horizontal:%f, vertical:%f, zoom:%f",
            self._device.get_name(),
            horizontal,
            vertical,
            zoom,
        )
        try:
            await self._sensor_instance.async_service_ptz_location(
                horizontal,
                vertical,
                zoom,
            )
        except ImouException as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="camera_move_location_failed",
                translation_placeholders={"error": str(err)},
            ) from err

    async def async_service_ptz_move(self, operation, duration):
        """Perform PTZ move action."""
        _LOGGER.debug(
            "[%s] invoked PTZ move action operation:%s, duration:%i",
            self._device.get_name(),
            operation,
            duration,
        )
        try:
            await self._sensor_instance.async_service_ptz_move(
                operation,
                duration,
            )
        except ImouException as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="camera_move_failed",
                translation_placeholders={"error": str(err)},
            ) from err
