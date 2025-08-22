"""Tests for the Imou Life Camera platform."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.imou_life.camera import ImouLifeCamera
from tests.fixtures.const import MOCK_CONFIG_ENTRY


class TestImouLifeCamera:
    """Test the Imou Life Camera."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock coordinator."""
        coordinator = MagicMock()
        coordinator.data = {
            "device_info": {
                "device_id": "test_device_123",
                "device_name": "Test Camera",
                "device_type": "camera"
            }
        }
        return coordinator

    @pytest.fixture
    def camera(self, mock_coordinator):
        """Create a camera instance."""
        return ImouLifeCamera(mock_coordinator, MOCK_CONFIG_ENTRY)

    def test_camera_name(self, camera):
        """Test camera name property."""
        assert camera.name == "Test Camera"

    def test_camera_unique_id(self, camera):
        """Test camera unique ID."""
        assert camera.unique_id == "test_device_123"

    def test_camera_should_poll(self, camera):
        """Test camera should_poll property."""
        assert camera.should_poll is False

    @pytest.mark.asyncio
    async def test_camera_image(self, camera):
        """Test camera image property."""
        # Mock the image data
        mock_image_data = b"fake_image_data"
        with patch.object(camera, '_get_image', return_value=mock_image_data):
            image = await camera.async_camera_image()
            assert image == mock_image_data

    @pytest.mark.asyncio
    async def test_camera_image_error(self, camera):
        """Test camera image error handling."""
        with patch.object(camera, '_get_image', side_effect=Exception("Test error")):
            image = await camera.async_camera_image()
            assert image is None

    def test_camera_state(self, camera):
        """Test camera state property."""
        assert camera.state == "idle"

    @pytest.mark.asyncio
    async def test_get_image_success(self, camera):
        """Test successful image retrieval."""
        mock_response = MagicMock()
        mock_response.content = b"test_image_data"
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            result = await camera._get_image()
            assert result == b"test_image_data"

    @pytest.mark.asyncio
    async def test_get_image_failure(self, camera):
        """Test image retrieval failure."""
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = await camera._get_image()
            assert result is None

    def test_camera_icon(self, camera):
        """Test camera icon property."""
        assert camera.icon == "mdi:camera"

    def test_camera_available(self, camera):
        """Test camera available property."""
        assert camera.available is True

    @pytest.mark.asyncio
    async def test_camera_snapshot(self, camera):
        """Test camera snapshot functionality."""
        mock_image_data = b"snapshot_data"
        with patch.object(camera, '_get_image', return_value=mock_image_data):
            snapshot = await camera.async_camera_image()
            assert snapshot == mock_image_data
