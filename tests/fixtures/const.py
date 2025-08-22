"""Constants for imou_life tests."""

from unittest.mock import MagicMock

from custom_components.imou_life.const import (
    CONF_API_URL,
    CONF_APP_ID,
    CONF_APP_SECRET,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DISCOVERED_DEVICE,
    CONF_ENABLE_DISCOVER,
)

# Create a mock ConfigEntry object with the required attributes
mock_config_entry = MagicMock()
mock_config_entry.entry_id = "test_entry_id"
mock_config_entry.data = {
    CONF_API_URL: "http://api.url",
    CONF_APP_ID: "app_id",
    CONF_APP_SECRET: "app_secret",
    CONF_DEVICE_NAME: "device_name",
    CONF_DEVICE_ID: "device_id",
}

MOCK_CONFIG_ENTRY = mock_config_entry


MOCK_LOGIN_WITH_DISCOVER = {
    CONF_API_URL: "http://api.url",
    CONF_APP_ID: "app_id",
    CONF_APP_SECRET: "app_secret",
    CONF_ENABLE_DISCOVER: True,
}

MOCK_LOGIN_WITHOUT_DISCOVER = {
    CONF_API_URL: "http://api.url",
    CONF_APP_ID: "app_id",
    CONF_APP_SECRET: "app_secret",
    CONF_ENABLE_DISCOVER: False,
}

MOCK_CREATE_ENTRY_FROM_DISCOVER = {
    CONF_DEVICE_NAME: "device_name",
    CONF_DISCOVERED_DEVICE: "device_id",
}

MOCK_CREATE_ENTRY_FROM_MANUAL = {
    CONF_DEVICE_ID: "device_id",
    CONF_DEVICE_NAME: "device_name",
}
