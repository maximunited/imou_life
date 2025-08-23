"""The imou_life integration."""

# https://github.com/maximunited/imou_life

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from imouapi.api import ImouAPIClient
from imouapi.device import ImouDevice
from imouapi.exceptions import ImouException

from .const import (
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    DEFAULT_API_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    OPTION_API_TIMEOUT,
    OPTION_API_URL,
    OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD,
    OPTION_SCAN_INTERVAL,
    OPTION_SETUP_TIMEOUT,
    OPTION_WAIT_AFTER_WAKE_UP,
    PLATFORMS,
)
from .coordinator import ImouDataUpdateCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Configuration schema - this integration only supports config entries
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# Setup timeout in seconds
SETUP_TIMEOUT = 30


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    # Initialize API client and device
    api_client, device = await _setup_api_client_and_device(hass, entry)

    # Initialize device with timeout protection
    await _initialize_device(device, entry)

    # Create and configure coordinator
    coordinator = await _setup_coordinator(hass, device, entry)

    # Store coordinator and setup platforms
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await _setup_platforms(hass, entry, coordinator)

    _LOGGER.debug("Integration setup completed successfully")
    return True


async def _setup_api_client_and_device(hass: HomeAssistant, entry: ConfigEntry):
    """Set up API client and device instance."""
    session = async_get_clientsession(hass)

    # Extract configuration parameters
    config_data = entry.data
    name = config_data.get(CONF_DEVICE_NAME)
    api_url = config_data.get(CONF_API_URL)
    app_id = config_data.get(CONF_APP_ID)
    app_secret = config_data.get(CONF_APP_SECRET)
    device_id = config_data.get(CONF_DEVICE_ID)

    _LOGGER.debug("Setting up device %s (%s)", name, device_id)

    # Create and configure API client
    api_client = _create_api_client(app_id, app_secret, session, api_url, entry)

    # Create and configure device instance
    device = _create_device_instance(api_client, device_id, name, entry)

    return api_client, device


def _create_api_client(
    app_id: str, app_secret: str, session, api_url: str, entry: ConfigEntry
):
    """Create and configure the API client."""
    api_client = ImouAPIClient(app_id, app_secret, session)
    api_client.set_base_url(api_url)

    # Configure timeout if specified
    timeout = _parse_timeout_option(entry.options.get(OPTION_API_TIMEOUT, None))
    if timeout is not None:
        _LOGGER.debug("Setting API timeout to %d", timeout)
        api_client.set_timeout(timeout)

    return api_client


def _parse_timeout_option(timeout_value):
    """Parse timeout option value safely."""
    if isinstance(timeout_value, str):
        return None if timeout_value == "" else int(timeout_value)
    return timeout_value


def _create_device_instance(api_client, device_id: str, name: str, entry: ConfigEntry):
    """Create and configure the device instance."""
    device = ImouDevice(api_client, device_id)

    if name is not None:
        device.set_name(name)

    # Configure device options
    _configure_device_options(device, entry)

    return device


def _configure_device_options(device: ImouDevice, entry: ConfigEntry):
    """Configure device-specific options."""
    camera_wait_before_download = entry.options.get(
        OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD, None
    )
    if camera_wait_before_download is not None:
        _LOGGER.debug(
            "Setting camera wait before download to %f", camera_wait_before_download
        )
        device.set_camera_wait_before_download(camera_wait_before_download)

    wait_after_wakeup = entry.options.get(OPTION_WAIT_AFTER_WAKE_UP, None)
    if wait_after_wakeup is not None:
        _LOGGER.debug("Setting wait after wakeup to %f", wait_after_wakeup)
        device.set_wait_after_wakeup(wait_after_wakeup)


async def _initialize_device(device: ImouDevice, entry: ConfigEntry):
    """Initialize device with timeout protection."""
    setup_timeout = entry.options.get(OPTION_SETUP_TIMEOUT, SETUP_TIMEOUT)

    try:
        _LOGGER.debug("Initializing device with timeout %d seconds...", setup_timeout)
        await asyncio.wait_for(device.async_initialize(), timeout=setup_timeout)
        _LOGGER.debug("Device initialization completed")
    except asyncio.TimeoutError:
        _LOGGER.error("Device initialization timed out after %d seconds", setup_timeout)
        raise ConfigEntryNotReady("Device initialization timed out")
    except ImouException as exception:
        _LOGGER.error(exception.to_string())
        raise ImouException() from exception

    # Disable all sensors initially (will be enabled individually by
    # async_added_to_hass())
    for sensor_instance in device.get_all_sensors():
        sensor_instance.set_enabled(False)


async def _setup_coordinator(
    hass: HomeAssistant, device: ImouDevice, entry: ConfigEntry
):
    """Set up and initialize coordinator."""
    coordinator = ImouDataUpdateCoordinator(
        hass, device, entry.options.get(OPTION_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    # Fetch initial data with timeout protection
    setup_timeout = entry.options.get(OPTION_SETUP_TIMEOUT, SETUP_TIMEOUT)
    try:
        _LOGGER.debug("Fetching initial data with timeout %d seconds...", setup_timeout)
        await asyncio.wait_for(coordinator.async_refresh(), timeout=setup_timeout)
        _LOGGER.debug("Initial data fetch completed")
    except asyncio.TimeoutError:
        _LOGGER.error("Initial data fetch timed out after %d seconds", setup_timeout)
        raise ConfigEntryNotReady("Initial data fetch timed out")

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    return coordinator


async def _setup_platforms(hass: HomeAssistant, entry: ConfigEntry, coordinator):
    """Set up all platforms."""
    # Add platforms to coordinator
    for platform in PLATFORMS:
        coordinator.platforms.append(platform)

    _LOGGER.debug("Setting up platforms: %s", PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.add_update_listener(async_reload_entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.debug("Unloading entry %s", entry.entry_id)
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_migrate_entry(hass, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)
    data = {**config_entry.data}
    options = {**config_entry.options}
    unique_id = data[CONF_DEVICE_ID]

    if config_entry.version == 1:
        # add the api url. If in option, use it, otherwise use the default one
        option_api_url = config_entry.options.get(OPTION_API_URL, None)
        api_url = DEFAULT_API_URL if option_api_url is None else option_api_url
        data[CONF_API_URL] = api_url
        config_entry.version = 2

    if config_entry.version == 2:
        # if api_url is empty, copy over the one in options
        if data[CONF_API_URL] == "":
            data[CONF_API_URL] = DEFAULT_API_URL
        if OPTION_API_URL in options:
            del options[OPTION_API_URL]
        config_entry.version = 3

    # update the config entry
    hass.config_entries.async_update_entry(
        config_entry, data=data, options=options, unique_id=unique_id
    )
    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True
