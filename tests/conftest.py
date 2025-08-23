"""Global fixtures for imou_life integration."""

# Mock turbojpeg before any other imports to prevent import errors
import sys
from unittest.mock import MagicMock

# Create a mock turbojpeg module
mock_turbojpeg = MagicMock()
sys.modules["turbojpeg"] = mock_turbojpeg

# Mock camera img_util to prevent import issues
mock_img_util = MagicMock()
sys.modules["homeassistant.components.camera.img_util"] = mock_img_util

# flake8: noqa: E402
from unittest.mock import MagicMock, patch

import pytest
from imouapi.device import ImouDevice
from imouapi.device_entity import ImouBinarySensor, ImouSensor, ImouSwitch
from imouapi.exceptions import ImouException

# pytest_plugins = "pytest_homeassistant_custom_component"
# Removed due to Windows compatibility issues


# This fixture is used to prevent HomeAssistant from attempting to create
# and dismiss persistent
# notifications. These calls would fail without this fixture since the
# persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


def mock_get_sensors_by_platform(platform):
    """Provide mock sensors by platform."""
    if platform == "switch":
        return [ImouSwitch(None, "device_id", "device_name", "motionDetect")]
    elif platform == "sensor":
        return [ImouSensor(None, "device_id", "device_name", "lastAlarm")]
    elif platform == "binary_sensor":
        return [ImouBinarySensor(None, "device_id", "device_name", "online")]


@pytest.fixture(name="api_ok")
def bypass_get_data_fixture():
    """Ensure all the calls to the underlying APIs are working fine."""
    with (
        patch("imouapi.device.ImouDevice.async_initialize"),
        patch("imouapi.device.ImouDevice.async_get_data"),
        patch("imouapi.api.ImouAPIClient.async_connect"),
        patch(
            "imouapi.device.ImouDiscoverService.async_discover_devices",
            return_value={"device_id": ImouDevice(None, None)},
        ),
        patch(
            "imouapi.device.ImouDevice.get_name",
            return_value="device_name",
        ),
        patch(
            "imouapi.device.ImouDevice.get_device_id",
            return_value="device_id",
        ),
        patch(
            "imouapi.device.ImouDevice.get_sensors_by_platform",
            side_effect=mock_get_sensors_by_platform,
        ),
    ):
        yield


@pytest.fixture(name="api_invalid_app_id")
def error_invalid_app_id_fixture():
    """Simulate error when retrieving data from API."""
    with (
        patch(
            "imouapi.exceptions.ImouException.get_title",
            return_value="invalid_configuration",
        ),
        patch("imouapi.api.ImouAPIClient.async_connect", side_effect=ImouException()),
    ):
        yield


@pytest.fixture(name="api_invalid_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with (
        patch("imouapi.device.ImouDevice.async_initialize"),
        patch("imouapi.api.ImouAPIClient.async_connect"),
        patch("imouapi.device.ImouDevice.async_get_data", side_effect=Exception()),
    ):
        yield


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations():
    """Auto enable custom integration otherwise will result in
    IntegrationNotFound exception."""
    yield


@pytest.fixture
def hass():
    """Create a mock Home Assistant instance."""
    from tests.fixtures.mocks import create_mock_hass

    return create_mock_hass()


# Mock Home Assistant components that are not available in tests
@pytest.fixture(autouse=True)
def mock_hass_components():
    """Mock Home Assistant components that are not available in tests."""
    with (
        patch("homeassistant.helpers.aiohttp_client.async_get_clientsession"),
        patch("homeassistant.helpers.frame.report_usage"),
        patch("homeassistant.helpers.frame.report_non_thread_safe_operation"),
        patch("homeassistant.helpers.entity_platform.async_get_current_platform"),
        patch("homeassistant.components.zeroconf.HaZeroconf"),
        patch("homeassistant.components.zeroconf.usage.report_usage"),
        patch("homeassistant.helpers.frame.report_usage"),
    ):
        yield
