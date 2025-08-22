"""Tests for the Imou Life Constants."""
import pytest

from custom_components.imou_life.const import (
    DOMAIN,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_ACCESS_TOKEN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL
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

    def test_conf_access_token_constant(self):
        """Test CONF_ACCESS_TOKEN constant."""
        assert CONF_ACCESS_TOKEN == "access_token"

    def test_default_name_constant(self):
        """Test DEFAULT_NAME constant."""
        assert DEFAULT_NAME == "Imou Life"

    def test_default_scan_interval_constant(self):
        """Test DEFAULT_SCAN_INTERVAL constant."""
        assert DEFAULT_SCAN_INTERVAL == 30

    def test_constants_are_strings(self):
        """Test that string constants are actually strings."""
        assert isinstance(DOMAIN, str)
        assert isinstance(CONF_APP_ID, str)
        assert isinstance(CONF_APP_SECRET, str)
        assert isinstance(CONF_ACCESS_TOKEN, str)
        assert isinstance(DEFAULT_NAME, str)

    def test_constants_are_integers(self):
        """Test that numeric constants are actually integers."""
        assert isinstance(DEFAULT_SCAN_INTERVAL, int)
