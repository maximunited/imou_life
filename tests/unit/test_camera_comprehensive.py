"""Comprehensive tests for the Imou Life Camera platform."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.exceptions import HomeAssistantError
from imouapi.exceptions import ImouException

from custom_components.imou_life.camera import ImouCamera
from custom_components.imou_life.const import ENABLED_CAMERAS
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestCameraSetup:
    """Test camera platform setup."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.device.get_sensors_by_platform.return_value = []
        coordinator.entities = []
        return coordinator

    @pytest.fixture
    def mock_config_entry(self, mock_coordinator):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_entry_123"
        config_entry.runtime_data = mock_coordinator
        return config_entry

    @pytest.mark.asyncio
    async def test_async_setup_entry_no_cameras(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup with no camera sensors."""
        from custom_components.imou_life.camera import async_setup_entry

        async_add_devices = MagicMock()
        mock_platform = MagicMock()

        with patch(
            "custom_components.imou_life.camera.entity_platform.async_get_current_platform",
            return_value=mock_platform,
        ):
            await async_setup_entry(MagicMock(), mock_config_entry, async_add_devices)

        # Should register PTZ services
        assert mock_platform.async_register_entity_service.call_count == 2

        # Should call async_add_devices with empty list
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 0

    @pytest.mark.asyncio
    async def test_async_setup_entry_with_cameras(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup with camera sensors."""
        from custom_components.imou_life.camera import async_setup_entry

        # Create mock sensor instances
        sensor1 = MagicMock()
        sensor1.get_name.return_value = "camera"
        sensor1.get_description.return_value = "Camera"
        sensor1.get_attributes.return_value = {}

        sensor2 = MagicMock()
        sensor2.get_name.return_value = "camera2"
        sensor2.get_description.return_value = "Camera 2"
        sensor2.get_attributes.return_value = {}

        mock_coordinator.device.get_sensors_by_platform.return_value = [
            sensor1,
            sensor2,
        ]

        async_add_devices = MagicMock()
        mock_platform = MagicMock()

        with patch(
            "custom_components.imou_life.camera.entity_platform.async_get_current_platform",
            return_value=mock_platform,
        ):
            await async_setup_entry(MagicMock(), mock_config_entry, async_add_devices)

        # Should add 2 camera entities
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 2
        assert len(mock_coordinator.entities) == 2


class TestCameraEntity:
    """Test camera entity functionality."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Camera"
        coordinator.device.get_model.return_value = "Test Model"
        coordinator.device.get_manufacturer.return_value = "Imou"
        coordinator.device.get_firmware.return_value = "1.0.0"
        coordinator.device.get_device_id.return_value = "test_camera_123"
        coordinator.device.get_status.return_value = True
        coordinator.hass = MagicMock()
        return coordinator

    @pytest.fixture
    def mock_sensor_instance(self):
        """Create a mock sensor instance."""
        sensor = MagicMock()
        sensor.get_name.return_value = "camera"
        sensor.get_description.return_value = "Camera"
        sensor.get_attributes.return_value = {"last_update": "2023-01-01T00:00:00Z"}
        sensor.async_get_image = AsyncMock(return_value=b"fake_image_data")
        sensor.async_get_stream_url = AsyncMock(return_value="rtsp://test.com/stream")
        sensor.set_enabled = MagicMock()
        sensor.async_update = AsyncMock()
        sensor.async_service_ptz_location = AsyncMock()
        sensor.async_service_ptz_move = AsyncMock()
        return sensor

    @pytest.fixture
    def camera(self, mock_coordinator, mock_sensor_instance):
        """Create a camera instance."""
        return ImouCamera(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "camera.{}"
        )

    def test_entity_registry_enabled_default_true(
        self, mock_coordinator, mock_sensor_instance
    ):
        """Test camera enabled by default when in ENABLED_CAMERAS."""
        # Use a camera name that's in ENABLED_CAMERAS
        mock_sensor_instance.get_name.return_value = next(iter(ENABLED_CAMERAS))
        camera = ImouCamera(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "camera.{}"
        )
        assert camera.entity_registry_enabled_default is True

    def test_entity_registry_enabled_default_false(
        self, mock_coordinator, mock_sensor_instance
    ):
        """Test camera disabled by default when not in ENABLED_CAMERAS."""
        mock_sensor_instance.get_name.return_value = "unknown_camera"
        camera = ImouCamera(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "camera.{}"
        )
        assert camera.entity_registry_enabled_default is False

    def test_available_with_entity_available_set(self, camera):
        """Test available property when _entity_available is explicitly set."""
        camera._entity_available = False
        assert camera.available is False

        camera._entity_available = True
        assert camera.available is True

    def test_available_with_entity_available_none(self, camera, mock_coordinator):
        """Test available property falls back to device status when _entity_available is None."""
        camera._entity_available = None
        mock_coordinator.device.get_status.return_value = True
        assert camera.available is True

        mock_coordinator.device.get_status.return_value = False
        assert camera.available is False

    def test_icon_default_fallback(self, mock_coordinator, mock_sensor_instance):
        """Test icon translation key is set based on sensor name."""
        mock_sensor_instance.get_name.return_value = "unknownSensor"
        # Re-create camera with the updated sensor name so constructor runs
        camera = ImouCamera(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "camera.{}"
        )
        # Translation key should be snake_case version of sensor name
        assert camera._attr_translation_key == "unknown_sensor"

    @pytest.mark.asyncio
    async def test_async_added_to_hass_success(self, camera, mock_sensor_instance):
        """Test async_added_to_hass lifecycle hook."""
        await camera.async_added_to_hass()

        # Should enable the sensor and request update
        mock_sensor_instance.set_enabled.assert_called_once_with(True)
        mock_sensor_instance.async_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_added_to_hass_with_exception(
        self, camera, mock_sensor_instance
    ):
        """Test async_added_to_hass handles exceptions during update."""
        mock_sensor_instance.async_update = AsyncMock(
            side_effect=ImouException("Update failed")
        )

        # Should not raise exception, just log it
        await camera.async_added_to_hass()

        # Should still enable the sensor
        mock_sensor_instance.set_enabled.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_async_will_remove_from_hass(self, camera, mock_sensor_instance):
        """Test async_will_remove_from_hass lifecycle hook."""
        await camera.async_will_remove_from_hass()

        # Should disable the sensor
        mock_sensor_instance.set_enabled.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_ptz_location_service_error(self, camera, mock_sensor_instance):
        """Test PTZ location service raises HomeAssistantError on failure."""
        mock_sensor_instance.async_service_ptz_location = AsyncMock(
            side_effect=ImouException("PTZ control failed")
        )

        with pytest.raises(HomeAssistantError):
            await camera.async_service_ptz_location(0.5, -0.3, 0.8)

    @pytest.mark.asyncio
    async def test_ptz_move_service_error(self, camera, mock_sensor_instance):
        """Test PTZ move service raises HomeAssistantError on failure."""
        mock_sensor_instance.async_service_ptz_move = AsyncMock(
            side_effect=ImouException("PTZ control failed")
        )

        with pytest.raises(HomeAssistantError):
            await camera.async_service_ptz_move("up", 2000)
