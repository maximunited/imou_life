"""Tests for the Imou Life Constants."""

from custom_components.imou_life.const import (
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    DEFAULT_API_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)


class TestConstants:
    """Test the constants module."""

    def test_domain_constant(self):
        """Test DOMAIN constant."""
        assert DOMAIN == "imou_life"

    def test_conf_app_id_constant(self):
        """Test CONF_APP_ID constant."""
        assert CONF_APP_ID == "app_id"

    def test_conf_app_secret_constant(self):
        """Test CONF_APP_SECRET constant."""
        assert CONF_APP_SECRET == "app_secret"

    def test_conf_device_name_constant(self):
        """Test CONF_DEVICE_NAME constant."""
        assert CONF_DEVICE_NAME == "device_name"

    def test_conf_device_id_constant(self):
        """Test CONF_DEVICE_ID constant."""
        assert CONF_DEVICE_ID == "device_id"

    def test_default_scan_interval_constant(self):
        """Test DEFAULT_SCAN_INTERVAL constant."""
        assert DEFAULT_SCAN_INTERVAL == 15 * 60

    def test_default_api_url_constant(self):
        """Test DEFAULT_API_URL constant."""
        assert DEFAULT_API_URL == "https://openapi.easy4ip.com/openapi"

    def test_platforms_constant(self):
        """Test PLATFORMS constant."""
        expected_platforms = [
            "switch",
            "sensor",
            "binary_sensor",
            "select",
            "button",
            "siren",
            "camera",
        ]
        assert PLATFORMS == expected_platforms

    def test_constants_are_strings(self):
        """Test that string constants are actually strings."""
        assert isinstance(DOMAIN, str)
        assert isinstance(CONF_APP_ID, str)
        assert isinstance(CONF_APP_SECRET, str)
        assert isinstance(CONF_DEVICE_NAME, str)
        assert isinstance(CONF_DEVICE_ID, str)
        assert isinstance(DEFAULT_API_URL, str)

    def test_constants_are_integers(self):
        """Test that numeric constants are actually integers."""
        assert isinstance(DEFAULT_SCAN_INTERVAL, int)

    def test_platforms_is_list(self):
        """Test that PLATFORMS is a list."""
        assert isinstance(PLATFORMS, list)
