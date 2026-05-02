"""Config flow for Imou."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from imouapi.api import ImouAPIClient
from imouapi.device import ImouDevice, ImouDiscoverService
from imouapi.exceptions import ImouException

from .const import (
    API_SERVER_LABELS,
    API_SERVER_OPTIONS,
    CONF_API_SERVER,
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DISCOVERED_DEVICE,
    CONF_ENABLE_DISCOVER,
    DEFAULT_API_SERVER,
    DEFAULT_AUTO_SLEEP,
    DEFAULT_BATTERY_OPTIMIZATION,
    DEFAULT_BATTERY_THRESHOLD,
    DEFAULT_LED_INDICATORS,
    DEFAULT_MOTION_SENSITIVITY,
    DEFAULT_POWER_SAVING_MODE,
    DEFAULT_RECORDING_QUALITY,
    DEFAULT_SCAN_INTERVAL,
    MOTION_SENSITIVITY_OPTIONS,
    OPTION_API_TIMEOUT,
    OPTION_AUTO_SLEEP,
    OPTION_BATTERY_OPTIMIZATION,
    OPTION_BATTERY_THRESHOLD,
    OPTION_CALLBACK_URL,
    OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD,
    OPTION_LED_INDICATORS,
    OPTION_MOTION_SENSITIVITY,
    OPTION_POWER_SAVING_MODE,
    OPTION_RECORDING_QUALITY,
    OPTION_SCAN_INTERVAL,
    OPTION_WAIT_AFTER_WAKE_UP,
    RECORDING_QUALITY_DISPLAY,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ImouFlowHandler(config_entries.ConfigFlow, domain="imou_life"):
    """Config flow for imou."""

    VERSION = 3

    def __init__(self):
        """Initialize."""
        self._api_url = None
        self._app_id = None
        self._app_secret = None
        self._api_client = None
        self._discover_service = None
        self._session = None
        self._discovered_devices = {}
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._session = async_create_clientsession(self.hass)
        return await self.async_step_login()

    # Step: login
    async def async_step_login(self, user_input=None):
        """Ask and validate app id and app secret."""
        self._errors = {}
        if user_input is not None:
            # Resolve API URL from server selection
            selected_server = user_input.get(CONF_API_SERVER, DEFAULT_API_SERVER)
            if selected_server == "custom":
                api_url = user_input.get(CONF_API_URL, "").strip()
                if not api_url:
                    self._errors["api_url"] = "custom_url_required"
            else:
                api_url = API_SERVER_OPTIONS[selected_server]

            # Only proceed if no errors
            if not self._errors:
                # create an imou discovery service
                self._api_client = ImouAPIClient(
                    user_input[CONF_APP_ID], user_input[CONF_APP_SECRET], self._session
                )
                self._api_client.set_base_url(api_url)
                self._discover_service = ImouDiscoverService(self._api_client)
                valid = False
                # check if the provided credentials are working
                try:
                    await self._api_client.async_connect()
                    valid = True
                except ImouException as exception:
                    self._errors["base"] = exception.get_title()
                    _LOGGER.error("Imou exception: %s", str(exception))
                # valid credentials provided
                if valid:
                    # store app id, secret, and resolved URL for later steps
                    self._api_url = api_url
                    self._app_id = user_input[CONF_APP_ID]
                    self._app_secret = user_input[CONF_APP_SECRET]
                    # if discover is requested run the discover step,
                    # otherwise the manual step
                    if user_input[CONF_ENABLE_DISCOVER]:
                        return await self.async_step_discover()
                    else:
                        return await self.async_step_manual()

        # by default show up the form
        return self.async_show_form(
            step_id="login",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_SERVER, default=DEFAULT_API_SERVER): vol.In(
                        API_SERVER_LABELS
                    ),
                    vol.Optional(CONF_API_URL, default=""): str,
                    vol.Required(CONF_APP_ID): str,
                    vol.Required(CONF_APP_SECRET): str,
                    vol.Required(CONF_ENABLE_DISCOVER, default=True): bool,
                }
            ),
            errors=self._errors,
        )

    # Step: discover

    async def async_step_discover(self, user_input=None):
        """Discover devices and ask the user to select one."""
        self._errors = {}
        if user_input is not None:
            # get the device instance from the selected input
            device = self._discovered_devices[user_input[CONF_DISCOVERED_DEVICE]]
            if device is not None:
                # create the entry using common method
                return await self._create_entry_from_device(device, user_input)

        # discover registered devices
        try:
            self._discovered_devices = (
                await self._discover_service.async_discover_devices()
            )
        except ImouException as exception:
            error_msg = str(exception)
            # Check if this is a rate limit error
            if "OP1013" in error_msg or "exceed limit" in error_msg.lower():
                self._errors["base"] = "rate_limit_discovery"
                _LOGGER.warning(
                    "API rate limit exceeded during device discovery. "
                    "Disable discovery and enter device ID manually to continue. "
                    "Error: %s",
                    error_msg,
                )
            else:
                self._errors["base"] = exception.get_title()
                _LOGGER.error("Imou exception: %s", str(exception))

        # If discovery succeeded, show device selection
        if self._discovered_devices:
            return self.async_show_form(
                step_id="discover",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DISCOVERED_DEVICE): vol.In(
                            self._discovered_devices.keys()
                        ),
                        vol.Optional(CONF_DEVICE_NAME): str,
                    }
                ),
                errors=self._errors,
            )
        else:
            # No devices discovered or error occurred, go to manual entry
            return await self.async_step_manual()

    # Step: manual configuration

    async def async_step_manual(self, user_input=None):
        """Manually add a device by its device id."""
        self._errors = {}
        if user_input is not None:
            # create an imou device instance
            device = ImouDevice(self._api_client, user_input[CONF_DEVICE_ID])
            valid = False
            rate_limited = False
            # check if the provided credentials are working
            try:
                await device.async_initialize()
                valid = True
            except ImouException as exception:
                error_msg = str(exception)
                # Check if this is a rate limit error
                if "OP1013" in error_msg or "exceed limit" in error_msg.lower():
                    rate_limited = True
                    _LOGGER.warning(
                        "API rate limit exceeded during device validation. "
                        "Creating entry anyway - device will initialize when rate limit clears. "
                        "Error: %s",
                        error_msg,
                    )
                else:
                    self._errors["base"] = exception.get_title()
                    _LOGGER.error("Imou exception: %s", str(exception))

            # valid credentials provided OR rate limited, create the entry
            if valid or rate_limited:
                # create the entry using common method
                return await self._create_entry_from_device(device, user_input)

        # by default show up the form
        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ID): str,
                    vol.Optional(CONF_DEVICE_NAME): str,
                }
            ),
            errors=self._errors,
        )

    async def _create_entry_from_device(self, device, user_input):
        """Create configuration entry from device instance."""
        # set the name
        name = (
            f"{user_input[CONF_DEVICE_NAME]}"
            if CONF_DEVICE_NAME in user_input and user_input[CONF_DEVICE_NAME] != ""
            else device.get_name()
        )
        # create the entry
        data = {
            CONF_API_URL: self._api_url,
            CONF_DEVICE_NAME: name,
            CONF_APP_ID: self._app_id,
            CONF_APP_SECRET: self._app_secret,
            CONF_DEVICE_ID: device.get_device_id(),
        }
        await self.async_set_unique_id(device.get_device_id())
        return self.async_create_entry(title=name, data=data)

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Handle reauthentication."""
        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm reauthentication."""
        errors = {}

        if user_input is not None:
            try:
                # Create API client with new credentials
                # Use existing API URL from config entry
                existing_api_url = self.entry.data.get(CONF_API_URL)
                if existing_api_url is None:
                    # Fallback: determine from server selection or use global default
                    existing_server = self.entry.data.get(
                        CONF_API_SERVER, DEFAULT_API_SERVER
                    )
                    existing_api_url = API_SERVER_OPTIONS.get(
                        existing_server, API_SERVER_OPTIONS[DEFAULT_API_SERVER]
                    )

                api_client = ImouAPIClient(
                    user_input[CONF_APP_ID],
                    user_input[CONF_APP_SECRET],
                    async_create_clientsession(self.hass),
                )
                api_client.set_base_url(existing_api_url)

                # Validate credentials
                await api_client.async_connect()

                # Verify device access
                device_id = self.entry.data.get(CONF_DEVICE_ID)
                if device_id:
                    device = ImouDevice(api_client, device_id)
                    await device.async_initialize()

                # Update config entry with new credentials
                new_data = {
                    **self.entry.data,
                    CONF_APP_ID: user_input[CONF_APP_ID],
                    CONF_APP_SECRET: user_input[CONF_APP_SECRET],
                }

                self.hass.config_entries.async_update_entry(self.entry, data=new_data)

                # Reload the integration
                await self.hass.config_entries.async_reload(self.entry.entry_id)

                return self.async_abort(reason="reauth_successful")

            except ImouException as exception:
                error_str = str(exception)
                error_str_lower = error_str.lower()

                # Map common exceptions to translation keys
                # Check rate limiting first
                if "op1013" in error_str_lower or "exceed limit" in error_str_lower:
                    errors["base"] = "rate_limit_exceeded"
                # Check authentication/authorization errors
                elif any(
                    pattern in error_str_lower
                    for pattern in [
                        "authentication failed",
                        "invalid credentials",
                        "invalid app",
                        "token expired",
                        "unauthorized",
                        "not_authorized",
                        "invalid device",
                        "op1002",
                    ]
                ):
                    errors["base"] = "not_authorized"
                # Check connection errors
                elif "connection" in error_str_lower:
                    errors["base"] = "connection_failed"
                # Generic API error fallback
                else:
                    errors["base"] = "api_error"
                _LOGGER.error("Reauth failed: %s", error_str)

        # Show reauth form
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_APP_ID): str,
                    vol.Required(CONF_APP_SECRET): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "device_name": self.entry.data.get(CONF_DEVICE_NAME) or self.entry.title
            },
        )

    async def async_step_repair_stale_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle stale device repair."""
        if not isinstance(self.init_data, dict):
            return self.async_abort(reason="invalid_data")

        entry_id = self.init_data.get("entry_id")
        entry = self.hass.config_entries.async_get_entry(entry_id)

        if not entry:
            return self.async_abort(reason="entry_not_found")

        device_name = self.init_data.get("device_name", "Unknown")
        device_id = self.init_data.get("device_id", "Unknown")
        error_message = self.init_data.get("error_message", "")

        if user_input is not None:
            action = user_input.get("action")

            if action == "remove":
                # Remove the config entry
                await self.hass.config_entries.async_remove(entry_id)
                return self.async_abort(reason="device_removed")

            elif action == "retry":
                # Reset counter and reload the entry
                coordinator = entry.runtime_data
                coordinator.stale_device_failure_count = 0
                coordinator.stale_device_suspected = False
                await self.hass.config_entries.async_reload(entry_id)
                return self.async_abort(reason="retrying")

            elif action == "ignore":
                # Reset all stale tracking state but don't reload
                coordinator = entry.runtime_data
                coordinator.stale_device_failure_count = 0
                coordinator.stale_device_suspected = False
                coordinator.stale_device_last_error = None
                return self.async_abort(reason="ignored")

        return self.async_show_form(
            step_id="repair_stale_device",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            "remove": "Remove device from Home Assistant",
                            "retry": "Retry connection (device may be temporarily unavailable)",
                            "ignore": "Ignore warning and continue",
                        }
                    )
                }
            ),
            description_placeholders={
                "device_name": device_name,
                "device_id": device_id,
                "error_message": error_message,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return Option Handler."""
        return ImouOptionsFlowHandler()


class ImouOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for imou."""

    @property
    def config_entry(self):
        """Return the config entry."""
        return self.hass.config_entries.async_get_entry(self.handler)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        self.options = dict(self.config_entry.options)
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        OPTION_SCAN_INTERVAL,
                        default=self.options.get(
                            OPTION_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): int,
                    vol.Optional(
                        OPTION_API_TIMEOUT,
                        default=(
                            str(self.options.get(OPTION_API_TIMEOUT))
                            if self.options.get(OPTION_API_TIMEOUT) not in (None, "")
                            else ""
                        ),
                    ): str,
                    vol.Optional(
                        OPTION_CALLBACK_URL,
                        default=self.options.get(OPTION_CALLBACK_URL) or "",
                    ): str,
                    vol.Optional(
                        OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD,
                        default=(
                            str(self.options.get(OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD))
                            if self.options.get(OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD)
                            not in (None, "")
                            else ""
                        ),
                    ): str,
                    vol.Optional(
                        OPTION_WAIT_AFTER_WAKE_UP,
                        default=(
                            str(self.options.get(OPTION_WAIT_AFTER_WAKE_UP))
                            if self.options.get(OPTION_WAIT_AFTER_WAKE_UP)
                            not in (None, "")
                            else ""
                        ),
                    ): str,
                    vol.Optional(
                        OPTION_BATTERY_OPTIMIZATION,
                        default=self.options.get(
                            OPTION_BATTERY_OPTIMIZATION, DEFAULT_BATTERY_OPTIMIZATION
                        ),
                    ): bool,
                    vol.Optional(
                        OPTION_POWER_SAVING_MODE,
                        default=self.options.get(
                            OPTION_POWER_SAVING_MODE, DEFAULT_POWER_SAVING_MODE
                        ),
                    ): bool,
                    vol.Optional(
                        OPTION_MOTION_SENSITIVITY,
                        default=self.options.get(
                            OPTION_MOTION_SENSITIVITY, DEFAULT_MOTION_SENSITIVITY
                        ),
                    ): vol.In(MOTION_SENSITIVITY_OPTIONS),
                    vol.Optional(
                        OPTION_RECORDING_QUALITY,
                        default=self.options.get(
                            OPTION_RECORDING_QUALITY, DEFAULT_RECORDING_QUALITY
                        ),
                    ): vol.In(RECORDING_QUALITY_DISPLAY),
                    vol.Optional(
                        OPTION_LED_INDICATORS,
                        default=self.options.get(
                            OPTION_LED_INDICATORS, DEFAULT_LED_INDICATORS
                        ),
                    ): bool,
                    vol.Optional(
                        OPTION_AUTO_SLEEP,
                        default=self.options.get(OPTION_AUTO_SLEEP, DEFAULT_AUTO_SLEEP),
                    ): bool,
                    vol.Optional(
                        OPTION_BATTERY_THRESHOLD,
                        default=self.options.get(
                            OPTION_BATTERY_THRESHOLD, DEFAULT_BATTERY_THRESHOLD
                        ),
                    ): vol.Range(min=5, max=50),
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        # Clean up empty string values for optional numeric fields
        if (
            OPTION_API_TIMEOUT in self.options
            and self.options[OPTION_API_TIMEOUT] == ""
        ):
            self.options[OPTION_API_TIMEOUT] = None
        elif OPTION_API_TIMEOUT in self.options and self.options[OPTION_API_TIMEOUT]:
            try:
                self.options[OPTION_API_TIMEOUT] = int(self.options[OPTION_API_TIMEOUT])
            except (ValueError, TypeError):
                self.options[OPTION_API_TIMEOUT] = None

        if (
            OPTION_CALLBACK_URL in self.options
            and self.options[OPTION_CALLBACK_URL] == ""
        ):
            self.options[OPTION_CALLBACK_URL] = None

        if (
            OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD in self.options
            and self.options[OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD] == ""
        ):
            self.options[OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD] = None
        elif (
            OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD in self.options
            and self.options[OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD]
        ):
            try:
                self.options[OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD] = float(
                    self.options[OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD]
                )
            except (ValueError, TypeError):
                self.options[OPTION_CAMERA_WAIT_BEFORE_DOWNLOAD] = None

        if (
            OPTION_WAIT_AFTER_WAKE_UP in self.options
            and self.options[OPTION_WAIT_AFTER_WAKE_UP] == ""
        ):
            self.options[OPTION_WAIT_AFTER_WAKE_UP] = None
        elif (
            OPTION_WAIT_AFTER_WAKE_UP in self.options
            and self.options[OPTION_WAIT_AFTER_WAKE_UP]
        ):
            try:
                self.options[OPTION_WAIT_AFTER_WAKE_UP] = float(
                    self.options[OPTION_WAIT_AFTER_WAKE_UP]
                )
            except (ValueError, TypeError):
                self.options[OPTION_WAIT_AFTER_WAKE_UP] = None

        # Remove None values to keep options clean
        self.options = {k: v for k, v in self.options.items() if v is not None}

        return self.async_create_entry(title="", data=self.options)
