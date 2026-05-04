"""Mock implementations for testing without pytest_homeassistant_custom_component."""

from unittest.mock import AsyncMock, MagicMock

from homeassistant.config_entries import ConfigEntry


class MockConfigEntry(ConfigEntry):
    """Mock ConfigEntry for testing."""

    def __init__(self, domain, data, entry_id="test", version=1, **kwargs):
        """Initialize mock config entry."""
        # Try different parameter combinations for different Home Assistant versions
        try:
            # Try with all parameters (newer versions)
            params = {
                "entry_id": entry_id,
                "domain": domain,
                "data": data,
                "version": version,
                "discovery_keys": kwargs.get("discovery_keys", []),
                "minor_version": kwargs.get("minor_version", 1),
                "options": kwargs.get("options", {}),
                "source": kwargs.get("source", "user"),
                "subentries_data": kwargs.get("subentries_data", {}),
                "title": kwargs.get("title", "Test Entry"),
                "unique_id": kwargs.get("unique_id", "test_unique_id"),
            }
            super().__init__(**params)
        except TypeError:
            try:
                # Try with required parameters for Python 3.12+
                params = {
                    "entry_id": entry_id,
                    "domain": domain,
                    "data": data,
                    "version": version,
                    "discovery_keys": kwargs.get("discovery_keys", []),
                    "options": kwargs.get("options", {}),
                    "unique_id": kwargs.get("unique_id", "test_unique_id"),
                    "minor_version": kwargs.get("minor_version", 1),
                    "title": kwargs.get("title", "Test Entry"),
                    "source": kwargs.get("source", "user"),
                }
                super().__init__(**params)
            except TypeError:
                try:
                    # Try without discovery_keys (older versions)
                    params = {
                        "entry_id": entry_id,
                        "domain": domain,
                        "data": data,
                        "version": version,
                        "minor_version": kwargs.get("minor_version", 1),
                        "options": kwargs.get("options", {}),
                        "source": kwargs.get("source", "user"),
                        "subentries_data": kwargs.get("subentries_data", {}),
                        "title": kwargs.get("title", "Test Entry"),
                        "unique_id": kwargs.get("unique_id", "test_unique_id"),
                    }
                    super().__init__(**params)
                except TypeError:
                    # Try with minimal parameters (Python 3.11 and older)
                    params = {
                        "entry_id": entry_id,
                        "domain": domain,
                        "data": data,
                        "version": version,
                        "minor_version": kwargs.get("minor_version", 1),
                        "title": kwargs.get("title", "Test Entry"),
                        "source": kwargs.get("source", "user"),
                    }
                    super().__init__(**params)

        self._hass = None
        self._options = kwargs.get("options", {})
        self.runtime_data = None  # Initialize runtime_data attribute

    def add_to_hass(self, hass):
        """Add this config entry to hass."""
        self._hass = hass
        # Register this entry in config_entries for mock_async_setup
        if hasattr(hass.config_entries, "_entries"):
            hass.config_entries._entries[self.entry_id] = self
        return self

    @property
    def hass(self):
        """Return the hass instance."""
        return self._hass

    @property
    def options(self):
        """Return the options."""
        return self._options

    @options.setter
    def options(self, value):
        """Set the options."""
        self._options = value


class MockHomeAssistant:
    """Mock Home Assistant instance for testing."""

    def __init__(self):
        """Initialize mock hass."""
        self.data = {}
        self.services = MagicMock()
        self.config_entries = MagicMock()
        self.async_block_till_done = AsyncMock()

        # Track flow state for different responses
        self._flow_step = 0
        self._flow_mode = "discover"  # "discover" or "manual"
        self._flow_error = None  # Error to return
        self._discovery_data = None  # Store discovery data for configure step
        self._configured_unique_ids = set()  # Track configured unique IDs
        self._created_entries = []  # Track created config entries
        self._flow_data = {}  # Store flow data (credentials, etc.)
        self._discovered_devices = {}  # Store discovered devices

        # Set up mocks
        self._setup_config_entries_mocks()
        self._setup_services_mocks()
        self._setup_network_mocks()

    def _setup_config_entries_mocks(self):
        """Set up config entries mocks."""
        # Mock config_entries.flow functionality
        self.config_entries.flow = MagicMock()

        # Set up flow mocks
        self._setup_flow_mocks()
        self._setup_entry_setup_mocks()
        self._setup_options_flow_mocks()

    def _setup_flow_mocks(self):
        """Set up flow-related mocks."""
        from homeassistant import data_entry_flow

        def mock_flow_init(*args, **kwargs):
            self._flow_step = 0
            mock_response = MagicMock()

            # Check if this is a discovery flow
            context = kwargs.get("context", {})
            data = kwargs.get("data", {})

            if context.get("source") == "discovery":
                device_id = data.get("device_id", "unknown")

                # Check if this unique_id is already configured
                if device_id in self._configured_unique_ids:
                    # Return abort result
                    mock_response.__getitem__ = MagicMock(
                        side_effect=lambda key: {
                            "type": data_entry_flow.FlowResultType.ABORT,
                            "flow_id": "test_flow_id",
                            "reason": "already_configured",
                        }.get(key)
                    )
                else:
                    # Store discovery data for configure step
                    self._discovery_data = data

                    # Discovery flow - return discovery_confirm step with placeholders
                    device_name = "Unknown"
                    device = data.get("device")
                    if device and hasattr(device, "get_name"):
                        try:
                            device_name = device.get_name()
                        except Exception:
                            pass

                    mock_response.__getitem__ = MagicMock(
                        side_effect=lambda key: {
                            "type": data_entry_flow.FlowResultType.FORM,
                            "step_id": "discovery_confirm",
                            "flow_id": "test_flow_id",
                            "errors": {},
                            "data_schema": None,
                            "description_placeholders": {
                                "device_name": device_name,
                                "device_id": device_id,
                            },
                        }.get(key)
                    )
            else:
                # Regular user flow - return login step
                self._discovery_data = None
                mock_response.__getitem__ = MagicMock(
                    side_effect=lambda key: {
                        "type": data_entry_flow.FlowResultType.FORM,
                        "step_id": "login",
                        "flow_id": "test_flow_id",
                        "errors": {},
                        "data_schema": None,
                    }.get(key)
                )
            return mock_response

        def mock_flow_configure(*args, **kwargs):
            self._flow_step += 1
            mock_response = MagicMock()
            user_input = kwargs.get("user_input", {})

            # Check if this is a discovery flow being confirmed
            if self._discovery_data is not None:
                # Discovery flow - create entry immediately with discovery data
                device_name = user_input.get("device_name", "Unknown")
                if not device_name:
                    device = self._discovery_data.get("device")
                    if device and hasattr(device, "get_name"):
                        try:
                            device_name = device.get_name()
                        except Exception:
                            device_name = f"Imou Device {self._discovery_data.get('device_id', 'unknown')[:8]}"

                api_creds = self._discovery_data.get("api_credentials", {})
                entry_data = {
                    "device_id": self._discovery_data.get("device_id"),
                    "device_name": device_name,
                    "app_id": api_creds.get("app_id"),
                    "app_secret": api_creds.get("app_secret"),
                    "api_url": api_creds.get("api_url"),
                }

                # Track this entry as created
                from custom_components.imou_life.const import DOMAIN

                entry = MockConfigEntry(
                    domain=DOMAIN,
                    data=entry_data,
                    unique_id=self._discovery_data.get("device_id"),
                    title=device_name,
                )
                entry.add_to_hass(self)
                self._created_entries.append(entry)
                self._configured_unique_ids.add(self._discovery_data.get("device_id"))

                mock_response.__getitem__ = MagicMock(
                    side_effect=lambda key: {
                        "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                        "flow_id": "test_flow_id",
                        "data": entry_data,
                        "title": device_name,
                        "result": True,
                    }.get(key)
                )
            elif self._flow_step == 1:
                # First configure call - store credentials and show next form
                # Store flow data (credentials) for later use
                self._flow_data = user_input.copy()

                # Check if discovery is enabled
                if user_input.get("enable_discover", False):
                    self._flow_mode = "discover"
                else:
                    self._flow_mode = "manual"

                if self._flow_error:
                    # Return error response
                    mock_response.__getitem__ = MagicMock(
                        side_effect=lambda key: {
                            "type": data_entry_flow.FlowResultType.FORM,
                            "step_id": "login",
                            "flow_id": "test_flow_id",
                            "errors": {"base": self._flow_error},
                            "data_schema": None,
                        }.get(key)
                    )
                else:
                    # Determine step_id based on flow mode
                    if self._flow_mode == "discover":
                        step_id = "discover"
                    else:
                        step_id = "manual"

                    mock_response.__getitem__ = MagicMock(
                        side_effect=lambda key: {
                            "type": data_entry_flow.FlowResultType.FORM,
                            "step_id": step_id,
                            "flow_id": "test_flow_id",
                            "errors": {},
                            "data_schema": None,
                        }.get(key)
                    )
            else:
                # Second configure call - create entry
                # Extract device info from user_input and discovered devices
                from custom_components.imou_life.const import (
                    CONF_DEVICE_ID,
                    CONF_DEVICE_NAME,
                    CONF_DISCOVERED_DEVICE,
                )

                device_name = user_input.get(CONF_DEVICE_NAME, "Unknown Device")
                # Check both discovered_device (for discovery flow) and device_id (for manual flow)
                device_id = user_input.get(CONF_DISCOVERED_DEVICE) or user_input.get(
                    CONF_DEVICE_ID, "device_id"
                )

                # Try to get device from discovered devices
                if (
                    hasattr(self, "_discovered_devices")
                    and device_id in self._discovered_devices
                ):
                    device = self._discovered_devices[device_id]
                    if hasattr(device, "get_device_id"):
                        device_id = device.get_device_id()
                    if not device_name or device_name == "Unknown Device":
                        if hasattr(device, "get_name"):
                            try:
                                device_name = device.get_name()
                            except Exception:
                                pass

                # Validate required flow data was collected
                required = ("api_url", "app_id", "app_secret")
                missing = [key for key in required if key not in self._flow_data]
                if missing:
                    raise AssertionError(
                        f"Missing flow data before entry creation: {missing}"
                    )

                entry_data = {
                    "api_url": self._flow_data["api_url"],
                    "app_id": self._flow_data["app_id"],
                    "app_secret": self._flow_data["app_secret"],
                    "device_id": device_id,
                    "device_name": device_name,
                }

                # Create the config entry
                from custom_components.imou_life.const import DOMAIN

                entry = MockConfigEntry(
                    domain=DOMAIN,
                    data=entry_data,
                    unique_id=device_id,
                    title=device_name,
                )
                entry.add_to_hass(self)
                self._created_entries.append(entry)
                self._configured_unique_ids.add(device_id)

                mock_response.__getitem__ = MagicMock(
                    side_effect=lambda key: {
                        "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                        "flow_id": "test_flow_id",
                        "data": entry_data,
                        "title": device_name,
                        "result": entry,
                    }.get(key)
                )

            return mock_response

        mock_flow_progress = MagicMock()
        mock_flow_progress.return_value = [
            {"flow_id": "test_flow_id", "step_id": "discover"}
        ]

        self.config_entries.flow.async_init = AsyncMock(side_effect=mock_flow_init)
        self.config_entries.flow.async_configure = AsyncMock(
            side_effect=mock_flow_configure
        )
        self.config_entries.flow.async_progress = mock_flow_progress

    def _setup_entry_setup_mocks(self):
        """Set up entry setup mocks."""

        # Make async_entries return the created entries
        def mock_async_entries(domain):
            return [e for e in self._created_entries if e.domain == domain]

        self.config_entries.async_entries = mock_async_entries

        def mock_async_setup(entry_id):
            # Create a mock coordinator that can pass isinstance checks
            from custom_components.imou_life.const import DOMAIN
            from custom_components.imou_life.coordinator import (
                ImouDataUpdateCoordinator,
            )

            mock_coordinator = MagicMock(spec=ImouDataUpdateCoordinator)
            # Make it pass isinstance checks
            mock_coordinator.__class__ = ImouDataUpdateCoordinator
            # Add required attributes
            mock_coordinator.platforms = []
            mock_coordinator.entities = []
            mock_coordinator.data = {
                "battery_level": 85,
                "online": True,
                "motion_detected": False,
            }  # Add realistic data structure

            # Try to use patched ImouDevice if available, otherwise create a mock
            try:
                from imouapi.device import ImouDevice

                # This will use the patched ImouDevice if the test patched it
                mock_device = ImouDevice(None, None)
            except (ImportError, TypeError):
                # Fallback to MagicMock only for import/constructor issues
                mock_device = MagicMock()
                mock_device.get_sensors_by_platform.return_value = [MagicMock()]
                mock_device.get_name.return_value = "device_name"
                mock_device.async_get_data = AsyncMock(
                    return_value={
                        "battery_level": 85,
                        "online": True,
                        "motion_detected": False,
                    }
                )
            mock_coordinator.device = mock_device

            # Make async_refresh actually update data from device
            async def mock_async_refresh():
                """Mock refresh that updates data from device."""
                if hasattr(mock_coordinator.device, "async_get_data"):
                    try:
                        from imouapi.exceptions import ImouException

                        mock_coordinator.data = (
                            await mock_coordinator.device.async_get_data()
                        )
                    except ImouException:
                        # Keep old data on API errors, like real DataUpdateCoordinator
                        # Unexpected errors will surface during tests
                        pass

            mock_coordinator.async_refresh = AsyncMock(side_effect=mock_async_refresh)

            # Find the config entry and set runtime_data
            for entry in self.config_entries._entries.values():
                if entry.entry_id == entry_id:
                    entry.runtime_data = mock_coordinator
                    break

            # Set up platforms
            from custom_components.imou_life.const import PLATFORMS

            for platform in PLATFORMS:
                mock_coordinator.platforms.append(platform)

            # Initialize hass.data[DOMAIN] if this is the first entry
            if DOMAIN not in self.data:
                self.data[DOMAIN] = {}

            # Set up discovery coordinator for first entry
            # Check _entries (includes manually added) not just _created_entries (from flow)
            existing_entries = [
                e for e in self.config_entries._entries.values() if e.domain == DOMAIN
            ]
            if len(existing_entries) == 1:  # This is the first entry
                # Get the entry being set up
                setup_entry = None
                for e in self.config_entries._entries.values():
                    if e.entry_id == entry_id:
                        setup_entry = e
                        break

                # Check if discovery is enabled in options
                from custom_components.imou_life.const import (
                    DEFAULT_DISCOVERY_INTERVAL,
                    DEFAULT_ENABLE_DISCOVERY,
                    OPTION_DISCOVERY_INTERVAL,
                    OPTION_ENABLE_DISCOVERY,
                )

                discovery_enabled = setup_entry.options.get(
                    OPTION_ENABLE_DISCOVERY, DEFAULT_ENABLE_DISCOVERY
                )

                if discovery_enabled:
                    # Create mock discovery coordinator with proper attributes
                    from datetime import timedelta

                    mock_discovery = MagicMock()
                    mock_discovery.async_refresh = AsyncMock()
                    mock_discovery._async_update_data = AsyncMock(return_value={})

                    # Set update_interval from options
                    discovery_interval = setup_entry.options.get(
                        OPTION_DISCOVERY_INTERVAL, DEFAULT_DISCOVERY_INTERVAL
                    )
                    mock_discovery.update_interval = timedelta(
                        seconds=discovery_interval
                    )

                    self.data[DOMAIN]["discovery"] = mock_discovery
                else:
                    self.data[DOMAIN]["discovery"] = None

            return True

        self.config_entries.async_setup = AsyncMock(side_effect=mock_async_setup)
        self.config_entries._entries = {}

        # Mock async_remove
        async def mock_async_remove(entry_id):
            """Mock remove config entry."""
            from custom_components.imou_life.const import DOMAIN

            if entry_id in self.config_entries._entries:
                del self.config_entries._entries[entry_id]

            # Clean up discovery if this is the last entry
            if DOMAIN in self.data and "discovery" in self.data[DOMAIN]:
                remaining_entries = [
                    e
                    for e in self.config_entries._entries.values()
                    if e.domain == DOMAIN
                ]
                if len(remaining_entries) == 0:
                    self.data[DOMAIN]["discovery"] = None

            return True

        self.config_entries.async_remove = AsyncMock(side_effect=mock_async_remove)

        # Mock async_forward_entry_setups
        def mock_async_forward_entry_setups(entry, platforms):
            # Actually call the platform setup for testing
            if "switch" in platforms:
                # Create a mock switch entity
                from custom_components.imou_life.switch import ImouSwitch

                mock_switch = MagicMock(spec=ImouSwitch)
                mock_switch.__class__ = ImouSwitch
                mock_switch.entity_id = "switch.device_name_motiondetect"
                mock_switch.async_turn_on = AsyncMock()
                mock_switch.async_turn_off = AsyncMock()

                # Add to coordinator entities (use runtime_data)
                if hasattr(entry, "runtime_data") and entry.runtime_data:
                    entry.runtime_data.entities.append(mock_switch)

            return True

        self.config_entries.async_forward_entry_setups = AsyncMock(
            side_effect=mock_async_forward_entry_setups
        )

        # Mock async_unload_entry_setups
        self.config_entries.async_unload_entry_setups = AsyncMock()

        # Mock async_forward_entry_unload
        self.config_entries.async_forward_entry_unload = AsyncMock(return_value=True)

    def _setup_options_flow_mocks(self):
        """Set up options flow mocks."""
        from homeassistant import data_entry_flow

        # Mock options flow
        self.config_entries.options = MagicMock()
        mock_options_response = MagicMock()
        mock_options_response.__getitem__ = MagicMock(
            side_effect=lambda key: {
                "type": data_entry_flow.FlowResultType.FORM,
                "step_id": "init",
                "flow_id": "test_options_flow_id",
                "errors": {},
                "data_schema": None,
            }.get(key)
        )
        self.config_entries.options.async_init = AsyncMock(
            return_value=mock_options_response
        )

        # Mock options flow configure
        def mock_options_configure(*args, **kwargs):
            # Get the user input from kwargs
            user_input = kwargs.get("user_input", {})

            mock_response = MagicMock()
            mock_response.__getitem__ = MagicMock(
                side_effect=lambda key: {
                    "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                    "flow_id": "test_options_flow_id",
                    "data": user_input,
                }.get(key)
            )
            return mock_response

        self.config_entries.options.async_configure = AsyncMock(
            side_effect=mock_options_configure
        )

    def _setup_services_mocks(self):
        """Set up services mocks."""
        # Mock services
        self.services.async_call = AsyncMock()

    def _setup_network_mocks(self):
        """Set up network component mocks."""
        # Mock network component
        self.data["network"] = MagicMock()
        self.data["network"].adapters = []

    def set_flow_mode(self, mode):
        """Set the flow mode for testing different scenarios."""
        self._flow_mode = mode

    def set_flow_error(self, error):
        """Set the flow error for testing error scenarios."""
        self._flow_error = error

    def __getattr__(self, name):
        """Handle attribute access."""
        if name not in self.__dict__:
            return MagicMock()
        return self.__dict__[name]


def create_mock_hass():
    """Create a mock Home Assistant instance."""
    return MockHomeAssistant()
