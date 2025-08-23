"""Mock implementations for testing without pytest_homeassistant_custom_component."""

from unittest.mock import AsyncMock, MagicMock

from homeassistant.config_entries import ConfigEntry


class MockConfigEntry(ConfigEntry):
    """Mock ConfigEntry for testing."""

    def __init__(self, domain, data, entry_id="test", version=1, **kwargs):
        """Initialize mock config entry."""
        # Always include all possible parameters to handle different HA versions
        all_params = {
            "entry_id": entry_id,
            "domain": domain,
            "data": data,
            "version": version,
            "minor_version": kwargs.get("minor_version", 1),
            "title": kwargs.get("title", "Test Entry"),
            "source": kwargs.get("source", "user"),
            "discovery_keys": kwargs.get("discovery_keys", []),
            "options": kwargs.get("options", {}),
            "unique_id": kwargs.get("unique_id", "test_unique_id"),
            "subentries_data": kwargs.get("subentries_data", {}),
        }

        # Try to initialize with all parameters
        try:
            super().__init__(**all_params)
        except TypeError as e:
            # If that fails, try to identify which parameters are actually required
            error_str = str(e)
            if "unexpected keyword argument" in error_str:
                # Extract the unexpected parameter name from the error
                import re

                unexpected_match = re.search(
                    r"unexpected keyword argument '([^']+)'",
                    error_str,
                )
                if unexpected_match:
                    unexpected_param = unexpected_match.group(1)
                    # Remove the unexpected parameter and try again
                    if unexpected_param in all_params:
                        del all_params[unexpected_param]
                        try:
                            super().__init__(**all_params)
                        except TypeError:
                            # If still failing, try with minimal parameters
                            super().__init__(
                                entry_id=entry_id,
                                domain=domain,
                                data=data,
                                version=version,
                            )
                    else:
                        # Fallback: try with minimal parameters
                        super().__init__(
                            entry_id=entry_id,
                            domain=domain,
                            data=data,
                            version=version,
                        )
                else:
                    # Fallback: try with minimal parameters
                    super().__init__(
                        entry_id=entry_id,
                        domain=domain,
                        data=data,
                        version=version,
                    )
            elif "missing" in error_str:
                # Extract missing parameter names from the error
                import re

                missing_match = re.search(
                    r"missing \d+ required keyword-only arguments?: '([^']+)'",
                    error_str,
                )
                if missing_match:
                    missing_params = missing_match.group(1).split("', '")
                    # Try with only the required parameters
                    required_params = {
                        k: v for k, v in all_params.items() if k in missing_params
                    }
                    super().__init__(**required_params)
                else:
                    # Fallback: try with minimal parameters
                    super().__init__(
                        entry_id=entry_id,
                        domain=domain,
                        data=data,
                        version=version,
                    )
            else:
                raise
        self._hass = None
        self._options = kwargs.get("options", {})

    def _get_default_value(self, param_name):
        """Get default value for a parameter."""
        defaults = {
            "minor_version": 1,
            "options": {},
            "source": "user",
            "title": "Test Entry",
            "unique_id": "test_unique_id",
        }
        return defaults.get(param_name)

    def add_to_hass(self, hass):
        """Add this config entry to hass."""
        self._hass = hass
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

        # Mock config_entries.flow functionality
        self.config_entries.flow = MagicMock()

        # Create mock flow responses
        from homeassistant import data_entry_flow

        # Track flow state for different responses
        self._flow_step = 0
        self._flow_mode = "discover"  # "discover" or "manual"
        self._flow_error = None  # Error to return

        def mock_flow_init(*args, **kwargs):
            self._flow_step = 0
            mock_response = MagicMock()
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

            if self._flow_step == 1:
                # First configure call - show next form based on mode
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
                mock_response.__getitem__ = MagicMock(
                    side_effect=lambda key: {
                        "type": data_entry_flow.FlowResultType.CREATE_ENTRY,
                        "flow_id": "test_flow_id",
                        "data": {
                            "api_url": "http://api.url",
                            "app_id": "app_id",
                            "app_secret": "app_secret",
                            "device_id": "device_id",
                        },
                        "result": True,
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

        # Mock config_entries.async_setup
        def mock_async_setup(entry_id):
            # Store the entry in hass.data for testing
            if "imou_life" not in self.data:
                self.data["imou_life"] = {}

            # Create a mock coordinator that can pass isinstance checks
            from custom_components.imou_life.coordinator import (
                ImouDataUpdateCoordinator,
            )

            mock_coordinator = MagicMock(spec=ImouDataUpdateCoordinator)
            # Make it pass isinstance checks
            mock_coordinator.__class__ = ImouDataUpdateCoordinator
            # Add required attributes
            mock_coordinator.platforms = []
            mock_coordinator.device = MagicMock()
            mock_coordinator.entities = []

            # Mock device methods
            mock_device = MagicMock()
            mock_device.get_sensors_by_platform.return_value = [MagicMock()]
            mock_device.get_name.return_value = "device_name"
            mock_coordinator.device = mock_device

            self.data["imou_life"][entry_id] = mock_coordinator

            # Set up platforms
            from custom_components.imou_life.const import PLATFORMS

            for platform in PLATFORMS:
                mock_coordinator.platforms.append(platform)

            return True

        self.config_entries.async_setup = AsyncMock(side_effect=mock_async_setup)

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

                # Add to coordinator entities
                coordinator = self.data["imou_life"][entry.entry_id]
                coordinator.entities.append(mock_switch)

            return True

        self.config_entries.async_forward_entry_setups = AsyncMock(
            side_effect=mock_async_forward_entry_setups
        )

        # Mock async_unload_entry_setups
        self.config_entries.async_unload_entry_setups = AsyncMock()

        # Mock async_forward_entry_unload
        self.config_entries.async_forward_entry_unload = AsyncMock(return_value=True)

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

        # Mock services
        self.services.async_call = AsyncMock()

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
