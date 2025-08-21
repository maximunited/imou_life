"""Mock implementations for testing without pytest_homeassistant_custom_component."""

from unittest.mock import MagicMock

from homeassistant.config_entries import ConfigEntry


class MockConfigEntry(ConfigEntry):
    """Mock ConfigEntry for testing."""

    def __init__(self, domain, data, entry_id="test", version=1, **kwargs):
        """Initialize mock config entry."""
        super().__init__(
            entry_id=entry_id, domain=domain, data=data, version=version, **kwargs
        )
        self._hass = None

    def add_to_hass(self, hass):
        """Add this config entry to hass."""
        self._hass = hass
        return self

    @property
    def hass(self):
        """Return the hass instance."""
        return self._hass


class MockHomeAssistant:
    """Mock Home Assistant instance for testing."""

    def __init__(self):
        """Initialize mock hass."""
        self.data = {}
        self.services = MagicMock()
        self.config_entries = MagicMock()
        self.async_block_till_done = MagicMock()

        # Mock config_entries.flow functionality
        self.config_entries.flow = MagicMock()
        self.config_entries.flow.async_init = MagicMock()
        self.config_entries.flow.async_configure = MagicMock()
        self.config_entries.flow.async_progress = MagicMock()

    def __getattr__(self, name):
        """Handle attribute access."""
        if name not in self.__dict__:
            return MagicMock()
        return self.__dict__[name]


def create_mock_hass():
    """Create a mock Home Assistant instance."""
    return MockHomeAssistant()
