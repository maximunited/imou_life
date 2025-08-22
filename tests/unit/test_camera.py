"""Tests for the Imou Life Camera platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.imou_life.camera import ImouCamera
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouCamera:
    """Test the Imou Life Camera."""

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
        # Use AsyncMock for async methods
        sensor.async_service_ptz_location = AsyncMock()
        sensor.async_service_ptz_move = AsyncMock()
        return sensor

    @pytest.fixture
    def camera(self, mock_coordinator, mock_sensor_instance):
        """Create a camera instance."""
        return ImouCamera(
            mock_coordinator, MOCK_CONFIG_ENTRY, mock_sensor_instance, "camera.{}"
        )

    def test_camera_name(self, camera):
        """Test camera name property."""
        assert camera.name == "Test Camera Camera"

    def test_camera_unique_id(self, camera):
        """Test camera unique ID."""
        assert camera.unique_id == f"{MOCK_CONFIG_ENTRY.entry_id}_camera"

    def test_camera_should_poll(self, camera):
        """Test camera should_poll property."""
        assert camera.should_poll is False

    @pytest.mark.asyncio
    async def test_camera_image(self, camera):
        """Test camera image property."""
        image = await camera.async_camera_image()
        assert image == b"fake_image_data"

    @pytest.mark.asyncio
    async def test_camera_stream_source(self, camera):
        """Test camera stream source."""
        stream_url = await camera.stream_source()
        assert stream_url == "rtsp://test.com/stream"

    def test_camera_icon(self, camera):
        """Test camera icon property."""
        assert camera.icon == "mdi:video"

    def test_camera_available(self, camera):
        """Test camera available property."""
        assert camera.available is True

    def test_camera_device_info(self, camera):
        """Test camera device info."""
        device_info = camera.device_info
        assert device_info["identifiers"] == {("imou_life", MOCK_CONFIG_ENTRY.entry_id)}
        assert device_info["name"] == "Test Camera"
        assert device_info["manufacturer"] == "Imou"

    def test_camera_extra_state_attributes(self, camera):
        """Test camera extra state attributes."""
        attrs = camera.extra_state_attributes
        assert "last_update" in attrs
        assert attrs["last_update"] == "2023-01-01T00:00:00Z"

    @pytest.mark.asyncio
    async def test_camera_ptz_location_service(self, camera):
        """Test camera PTZ location service."""
        await camera.async_service_ptz_location(0.5, -0.3, 0.8)
        camera._sensor_instance.async_service_ptz_location.assert_called_once_with(
            0.5, -0.3, 0.8
        )

    @pytest.mark.asyncio
    async def test_camera_ptz_move_service(self, camera):
        """Test camera PTZ move service."""
        await camera.async_service_ptz_move("up", 2000)
        camera._sensor_instance.async_service_ptz_move.assert_called_once_with(
            "up", 2000
        )
