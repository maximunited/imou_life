"""Camera platform for Imou."""

import logging
from collections.abc import Callable

import imouapi
import voluptuous as vol
from homeassistant.components.camera import (
    ENTITY_ID_FORMAT,
    Camera,
    CameraEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from imouapi.const import PTZ_OPERATIONS

from .const import (
    ATTR_PTZ_DURATION,
    ATTR_PTZ_HORIZONTAL,
    ATTR_PTZ_OPERATION,
    ATTR_PTZ_VERTICAL,
    ATTR_PTZ_ZOOM,
    DOMAIN,
    ENABLED_CAMERAS,
    SERVIZE_PTZ_LOCATION,
    SERVIZE_PTZ_MOVE,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


# async def async_setup_entry(hass, entry, async_add_devices):
async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_devices: Callable
):
    """Configure platform."""
    platform = entity_platform.async_get_current_platform()

    # Create PTZ location service
    platform.async_register_entity_service(
        SERVIZE_PTZ_LOCATION,
        {
            vol.Required(ATTR_PTZ_HORIZONTAL, default=0): vol.Range(min=-1, max=1),
            vol.Required(ATTR_PTZ_VERTICAL, default=0): vol.Range(min=-1, max=1),
            vol.Required(ATTR_PTZ_ZOOM, default=0): vol.Range(min=0, max=1),
        },
        "async_service_ptz_location",
    )

    # Create PTZ move service
    platform.async_register_entity_service(
        SERVIZE_PTZ_MOVE,
        {
            vol.Required(ATTR_PTZ_OPERATION, default=0): vol.In(list(PTZ_OPERATIONS)),
            vol.Required(ATTR_PTZ_DURATION, default=1000): vol.Range(
                min=100, max=10000
            ),
        },
        "async_service_ptz_move",
    )

    coordinator = hass.data[DOMAIN][entry.entry_id]
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
    def icon(self):
        """Return the icon of this sensor."""
        from .const import SENSOR_ICONS

        if self._sensor_instance.get_name() in SENSOR_ICONS:
            return SENSOR_ICONS[self._sensor_instance.get_name()]
        return SENSOR_ICONS["__default__"]

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
        try:
            stream_url = await self._sensor_instance.async_get_stream_url()
            _LOGGER.debug("Successfully got stream URL: %s", stream_url)
            return stream_url
        except imouapi.exceptions.APIError as e:
            _LOGGER.warning("API stream failed, falling back to local RTSP: %s", str(e))
            return (
                "rtsp://admin:yourpassword@192.168.1.100:554/cam/realmonitor"
                "?channel=1&subtype=0"
            )

    async def async_added_to_hass(self):
        """Entity added to HA (at startup or when re-enabled)."""
        await super().async_added_to_hass()
        _LOGGER.debug("%s added to HA", self.name)
        self._sensor_instance.set_enabled(True)
        # request an update of this sensor
        try:
            await self._sensor_instance.async_update()
        except imouapi.exceptions.ImouException as exception:
            _LOGGER.error(exception.to_string())

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
        await self._sensor_instance.async_service_ptz_location(
            horizontal,
            vertical,
            zoom,
        )

    async def async_service_ptz_move(self, operation, duration):
        """Perform PTZ move action."""
        _LOGGER.debug(
            "[%s] invoked PTZ move action operation:%s, duration:%i",
            self._device.get_name(),
            operation,
            duration,
        )
        await self._sensor_instance.async_service_ptz_move(
            operation,
            duration,
        )
