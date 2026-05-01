"""Tests for API Status diagnostic sensor."""

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from homeassistant.const import EntityCategory
from homeassistant.util import dt as dt_util

from custom_components.imou_life.const import DOMAIN
from custom_components.imou_life.sensor import ImouAPIStatusSensor
from tests.fixtures.mocks import MockConfigEntry


class TestImouAPIStatusSensor:
    """Test the API Status diagnostic sensor."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.device.get_model.return_value = "IPC-TestModel"

        # Rate limit tracking attributes
        coordinator.is_rate_limited = False
        coordinator.rate_limit_count = 0
        coordinator.last_error_type = None
        coordinator.last_error_message = None
        coordinator.last_successful_update = None
        coordinator.rate_limit_start_time = None
        coordinator.rate_limit_estimated_reset = None
        coordinator._is_interval_adjusted = False
        coordinator.update_interval = timedelta(seconds=900)  # 15 minutes

        # Mock hass
        coordinator.hass = MagicMock()
        coordinator.hass.data = {"core": MagicMock()}
        coordinator.hass.data["core"].now.return_value = dt_util.utcnow()

        return coordinator

    @pytest.fixture
    def config_entry(self):
        """Create a mock config entry."""
        return MockConfigEntry(
            domain=DOMAIN,
            data={"device_id": "test_device_123", "device_name": "Test Camera"},
            entry_id="test_entry",
            version=3,
        )

    def test_sensor_initialization(self, mock_coordinator, config_entry):
        """Test sensor initialization."""
        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)

        assert sensor._attr_entity_category == EntityCategory.DIAGNOSTIC
        assert sensor._attr_icon == "mdi:api"
        assert sensor._attr_has_entity_name is True
        assert sensor._attr_translation_key == "api_status"
        assert sensor._attr_unique_id == "test_entry_api_status"

    def test_sensor_device_info(self, mock_coordinator, config_entry):
        """Test sensor device info."""
        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)
        device_info = sensor.device_info

        assert device_info["identifiers"] == {(DOMAIN, "test_entry")}
        assert device_info["name"] == "Test Camera"
        assert device_info["manufacturer"] == "Imou"
        assert device_info["model"] == "IPC-TestModel"

    def test_sensor_state_ok(self, mock_coordinator, config_entry):
        """Test sensor state when API is healthy."""
        mock_coordinator.last_successful_update = dt_util.utcnow()
        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)

        assert sensor.state == "ok"

    def test_sensor_state_rate_limited(self, mock_coordinator, config_entry):
        """Test sensor state when rate limited."""
        mock_coordinator.is_rate_limited = True
        mock_coordinator.rate_limit_count = 3
        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)

        assert sensor.state == "rate_limited"

    def test_sensor_state_error(self, mock_coordinator, config_entry):
        """Test sensor state when error occurs."""
        mock_coordinator.last_error_type = "api_error"
        mock_coordinator.last_error_message = "Connection timeout"
        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)

        assert sensor.state == "error"

    def test_sensor_state_unknown(self, mock_coordinator, config_entry):
        """Test sensor state when unknown."""
        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)

        assert sensor.state == "unknown"

    def test_sensor_attributes_basic(self, mock_coordinator, config_entry):
        """Test basic sensor attributes."""
        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)
        attrs = sensor.extra_state_attributes

        assert attrs["rate_limited"] is False
        assert attrs["rate_limit_count"] == 0
        assert attrs["scan_interval"] == 900
        assert attrs["scan_interval_adjusted"] is False

    def test_sensor_attributes_rate_limited(self, mock_coordinator, config_entry):
        """Test sensor attributes when rate limited."""
        now = dt_util.utcnow()
        mock_coordinator.is_rate_limited = True
        mock_coordinator.rate_limit_count = 5
        mock_coordinator.last_error_type = "rate_limit"
        mock_coordinator.last_error_message = (
            "OP1013: Call interface times exceed limit"
        )
        mock_coordinator.rate_limit_start_time = now
        mock_coordinator.rate_limit_estimated_reset = now + timedelta(hours=1)
        mock_coordinator._is_interval_adjusted = True
        mock_coordinator.update_interval = timedelta(seconds=1800)  # 30 minutes

        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)
        attrs = sensor.extra_state_attributes

        assert attrs["rate_limited"] is True
        assert attrs["rate_limit_count"] == 5
        assert attrs["scan_interval"] == 1800
        assert attrs["scan_interval_adjusted"] is True
        assert attrs["last_error_type"] == "rate_limit"
        assert "OP1013" in attrs["last_error_message"]
        assert "rate_limit_started_at" in attrs
        assert "rate_limit_estimated_reset" in attrs
        assert "rate_limit_reset_in_seconds" in attrs
        assert attrs["rate_limit_reset_in_seconds"] > 0

    def test_sensor_attributes_after_recovery(self, mock_coordinator, config_entry):
        """Test sensor attributes after recovering from rate limit."""
        now = dt_util.utcnow()
        mock_coordinator.is_rate_limited = False
        mock_coordinator.rate_limit_count = 3  # Count persists
        mock_coordinator.last_successful_update = now
        mock_coordinator._is_interval_adjusted = False
        mock_coordinator.update_interval = timedelta(seconds=900)  # Restored

        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)
        attrs = sensor.extra_state_attributes

        assert attrs["rate_limited"] is False
        assert attrs["rate_limit_count"] == 3  # Historical count
        assert attrs["scan_interval"] == 900
        assert attrs["scan_interval_adjusted"] is False
        assert "last_successful_update" in attrs

    def test_sensor_attributes_with_error(self, mock_coordinator, config_entry):
        """Test sensor attributes with API error."""
        mock_coordinator.last_error_type = "api_error"
        mock_coordinator.last_error_message = "SN1003: Signature parameter error"

        sensor = ImouAPIStatusSensor(mock_coordinator, config_entry)
        attrs = sensor.extra_state_attributes

        assert attrs["last_error_type"] == "api_error"
        assert "SN1003" in attrs["last_error_message"]
