"""The imou_life integration."""

# https://github.com/maximunited/imou_life

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntry
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
    DEFAULT_ENABLE_DISCOVERY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    OPTION_API_TIMEOUT,
    OPTION_API_URL,
    OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD,
    OPTION_ENABLE_DISCOVERY,
    OPTION_SCAN_INTERVAL,
    OPTION_SETUP_TIMEOUT,
    OPTION_WAIT_AFTER_WAKE_UP,
    PLATFORMS,
)
from .coordinator import ImouDataUpdateCoordinator, ImouDiscoveryCoordinator

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
    # Initialize API client and device
    api_client, device = await _setup_api_client_and_device(hass, entry)

    # Initialize device with timeout protection
    await _initialize_device(device, entry)

    # Create and configure coordinator
    coordinator = await _setup_coordinator(hass, device, entry)

    # Store coordinator in runtime_data (modern HA pattern)
    entry.runtime_data = coordinator

    # Set up stale device detection handler
    async def handle_stale_device(event):
        """Handle stale device detection."""
        if event.data.get("entry_id") == entry.entry_id:
            await _create_stale_device_repair_issue(hass, entry, coordinator)

    entry.async_on_unload(
        hass.bus.async_listen(
            f"{DOMAIN}_stale_device_detected",
            handle_stale_device,
        )
    )

    # Initialize discovery coordinator on first entry only
    if _is_first_entry(hass, entry):
        discovery_coordinator = await _setup_discovery_coordinator(
            hass, api_client, entry
        )
        # Store discovery coordinator separately
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN]["discovery"] = discovery_coordinator

        # Handle first entry removal - transfer discovery to next entry
        async def cleanup_discovery(event):
            """Clean up discovery coordinator."""
            if event.data.get("entry_id") == entry.entry_id:
                await _transfer_discovery_to_next_entry(hass, entry)

        entry.async_on_unload(
            hass.bus.async_listen(
                f"{DOMAIN}_entry_unload_{entry.entry_id}",
                cleanup_discovery,
            )
        )

    await _setup_platforms(hass, entry, coordinator)

    # Check for rate limiting and notify user if detected
    _check_rate_limit_status(hass, entry, coordinator)

    _LOGGER.debug("Integration setup completed successfully")
    return True


async def _setup_api_client_and_device(hass: HomeAssistant, entry: ConfigEntry):
    """Set up API client and device instance."""
    session = async_get_clientsession(hass)

    # Extract configuration parameters
    config_data = entry.data
    device_config = {
        "name": config_data.get(CONF_DEVICE_NAME),
        "api_url": config_data.get(CONF_API_URL),
        "app_id": config_data.get(CONF_APP_ID),
        "app_secret": config_data.get(CONF_APP_SECRET),
        "device_id": config_data.get(CONF_DEVICE_ID),
    }

    _LOGGER.debug(
        "Setting up device %s (%s)", device_config["name"], device_config["device_id"]
    )

    # Create and configure components
    api_client = _create_api_client(device_config, session, entry)
    device = _create_device_instance(api_client, device_config, entry)

    return api_client, device


def _create_api_client(device_config: dict, session, entry: ConfigEntry):
    """Create and configure the API client."""
    api_client = ImouAPIClient(
        device_config["app_id"], device_config["app_secret"], session
    )
    api_client.set_base_url(device_config["api_url"])

    # Configure timeout if specified
    timeout = _parse_timeout_option(entry.options.get(OPTION_API_TIMEOUT, None))
    if timeout is not None:
        _LOGGER.debug("Setting API timeout to %d", timeout)
        api_client.set_timeout(timeout)

    return api_client


def _parse_timeout_option(timeout_value):
    """Parse timeout option value safely."""
    if isinstance(timeout_value, str):
        if timeout_value == "":
            return None
        try:
            return int(timeout_value)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid timeout value: %s, using default", timeout_value)
            return None
    return timeout_value


def _create_device_instance(api_client, device_config: dict, entry: ConfigEntry):
    """Create and configure the device instance."""
    device = ImouDevice(api_client, device_config["device_id"])

    if device_config["name"] is not None:
        device.set_name(device_config["name"])

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
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN, translation_key="device_init_timeout"
        )
    except ImouException as exception:
        error_msg = str(exception)
        # Handle API rate limit errors (OP1013) by requesting retry
        if "OP1013" in error_msg or "exceed limit" in error_msg.lower():
            _LOGGER.warning(
                "Imou API rate limit exceeded during initialization. "
                "Home Assistant will automatically retry. "
                "Error: %s",
                error_msg,
            )
            raise ConfigEntryNotReady(
                translation_domain=DOMAIN,
                translation_key="rate_limit_retry",
                translation_placeholders={"error": error_msg},
            )
        _LOGGER.error("Imou exception: %s", error_msg)
        raise

    # Disable all sensors initially (will be enabled individually by
    # async_added_to_hass())
    for sensor_instance in device.get_all_sensors():
        sensor_instance.set_enabled(False)


async def _setup_coordinator(
    hass: HomeAssistant, device: ImouDevice, entry: ConfigEntry
):
    """Set up and initialize coordinator."""
    coordinator = ImouDataUpdateCoordinator(
        hass,
        device,
        entry.options.get(OPTION_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        entry,
    )

    # Fetch initial data with timeout protection
    setup_timeout = entry.options.get(OPTION_SETUP_TIMEOUT, SETUP_TIMEOUT)
    try:
        _LOGGER.debug("Fetching initial data with timeout %d seconds...", setup_timeout)
        await asyncio.wait_for(coordinator.async_refresh(), timeout=setup_timeout)
        _LOGGER.debug("Initial data fetch completed")
    except asyncio.TimeoutError:
        _LOGGER.error("Initial data fetch timed out after %d seconds", setup_timeout)
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN, translation_key="initial_fetch_timeout"
        )

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


def _check_rate_limit_status(hass: HomeAssistant, entry: ConfigEntry, coordinator):
    """Check for rate limiting and notify user if detected."""
    if coordinator.is_rate_limited:
        device_name = coordinator.device.get_name()
        notification_id = f"{DOMAIN}_{entry.entry_id}_rate_limit"

        message = (
            f"The Imou API is currently rate limiting requests for {device_name}. "
            f"The integration will continue to retry automatically. "
            f"Check the 'API Status' diagnostic sensor for details.\n\n"
            f"Rate limit count: {coordinator.rate_limit_count}\n"
            f"Error: {coordinator.last_error_message}"
        )

        hass.components.persistent_notification.async_create(
            message,
            title="Imou API Rate Limit Detected",
            notification_id=notification_id,
        )

        _LOGGER.warning(
            "Rate limiting detected for %s during setup. Notification created.",
            device_name,
        )


async def _create_stale_device_repair_issue(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: ImouDataUpdateCoordinator,
) -> None:
    """Create a repair issue for stale device."""
    device_name = coordinator.device.get_name()
    device_id = coordinator.device.get_device_id()

    # Create repair flow
    await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "repair_stale_device"},
        data={
            "entry_id": entry.entry_id,
            "device_name": device_name,
            "device_id": device_id,
            "error_message": coordinator.stale_device_last_error,
        },
    )


def _is_first_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Check if this is the first config entry."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return True
    return entries[0].entry_id == entry.entry_id


async def _setup_discovery_coordinator(
    hass: HomeAssistant, api_client, entry: ConfigEntry
):
    """Set up discovery coordinator."""
    # Check if discovery is enabled
    if not entry.options.get(OPTION_ENABLE_DISCOVERY, DEFAULT_ENABLE_DISCOVERY):
        _LOGGER.debug("Discovery is disabled in options, skipping setup")
        return None

    _LOGGER.debug("Setting up discovery coordinator for first entry")
    coordinator = ImouDiscoveryCoordinator(hass, api_client, entry)
    await coordinator.async_config_entry_first_refresh()
    return coordinator


async def _transfer_discovery_to_next_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Transfer discovery coordinator to next entry when first entry is removed."""
    entries = hass.config_entries.async_entries(DOMAIN)
    remaining_entries = [e for e in entries if e.entry_id != entry.entry_id]

    if remaining_entries and DOMAIN in hass.data:
        _LOGGER.debug(
            "First entry removed, transferring discovery to next entry: %s",
            remaining_entries[0].entry_id,
        )

        # Stop current discovery
        if "discovery" in hass.data[DOMAIN]:
            hass.data[DOMAIN]["discovery"] = None

        # Reload next entry to initialize discovery
        await hass.config_entries.async_reload(remaining_entries[0].entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    _LOGGER.debug("Unloading entry %s", entry.entry_id)

    # Fire event for discovery cleanup
    hass.bus.async_fire(
        f"{DOMAIN}_entry_unload_{entry.entry_id}",
        {"entry_id": entry.entry_id},
    )

    # Clean up discovery if this is the last entry
    if DOMAIN in hass.data and "discovery" in hass.data[DOMAIN]:
        entries = hass.config_entries.async_entries(DOMAIN)
        if len(entries) <= 1:  # Last entry being removed
            hass.data[DOMAIN]["discovery"] = None
            _LOGGER.debug("Last entry removed, stopping discovery coordinator")

    coordinator = entry.runtime_data
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    return unloaded


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a device from the integration.

    Called when the user clicks the delete button on a device.
    Returns True if the device can be removed, False otherwise.

    Since each config entry corresponds to exactly one device in our integration,
    we allow removal of the device. This will also remove the config entry if
    it's the only one associated with this device.
    """
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_name = config_entry.data.get(CONF_DEVICE_NAME, "Unknown")

    _LOGGER.info(
        "User requested deletion of device '%s' (ID: %s) from config entry %s",
        device_name,
        device_id,
        config_entry.entry_id,
    )

    # Check if this device belongs to this config entry by comparing identifiers
    # Note: Entities use config_entry.entry_id as the device identifier, not device_id
    for identifier in device_entry.identifiers:
        if identifier[0] == DOMAIN and identifier[1] == config_entry.entry_id:
            _LOGGER.debug(
                "Device '%s' belongs to this config entry, allowing removal",
                device_name,
            )
            return True

    # If the device doesn't match this config entry, don't allow removal
    _LOGGER.debug(
        "Device does not belong to config entry %s, preventing removal",
        config_entry.entry_id,
    )
    return False


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
