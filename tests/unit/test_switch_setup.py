"""Tests for switch platform setup."""

from unittest.mock import MagicMock, patch

import pytest


class TestSwitchSetup:
    """Test switch platform setup."""

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
    async def test_async_setup_entry_no_switches(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup with no switch sensors."""
        from custom_components.imou_life.switch import async_setup_entry

        async_add_devices = MagicMock()

        await async_setup_entry(MagicMock(), mock_config_entry, async_add_devices)

        # Should not add any devices
        async_add_devices.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_setup_entry_with_switches(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup with switch sensors."""
        from custom_components.imou_life.switch import async_setup_entry

        # Create mock sensor instances
        sensor1 = MagicMock()
        sensor1.get_name.return_value = "motionDetect"
        sensor1.get_description.return_value = "Motion Detection"

        sensor2 = MagicMock()
        sensor2.get_name.return_value = "pushNotifications"
        sensor2.get_description.return_value = "Push Notifications"

        mock_coordinator.device.get_sensors_by_platform.return_value = [
            sensor1,
            sensor2,
        ]

        async_add_devices = MagicMock()

        await async_setup_entry(MagicMock(), mock_config_entry, async_add_devices)

        # Should add 2 switch entities
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 2
        assert len(mock_coordinator.entities) == 2

    @pytest.mark.asyncio
    async def test_async_setup_entry_sensor_creation_error(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup continues when sensor creation fails."""
        from custom_components.imou_life.switch import async_setup_entry

        # Create mock sensor that will fail
        sensor_good = MagicMock()
        sensor_good.get_name.return_value = "motionDetect"
        sensor_good.get_description.return_value = "Motion Detection"

        sensor_bad = MagicMock()
        sensor_bad.get_name.return_value = "badSensor"
        sensor_bad.get_description.return_value = "Bad Sensor"

        mock_coordinator.device.get_sensors_by_platform.return_value = [
            sensor_good,
            sensor_bad,
        ]

        async_add_devices = MagicMock()

        # Make ImouSwitch constructor fail for the bad sensor
        with patch(
            "custom_components.imou_life.switch.ImouSwitch",
            side_effect=[
                MagicMock(name="Motion Detection"),
                Exception("Sensor creation failed"),
            ],
        ):
            await async_setup_entry(MagicMock(), mock_config_entry, async_add_devices)

        # Should add only the good sensor
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 1

    @pytest.mark.asyncio
    async def test_async_setup_entry_setup_error(self, mock_config_entry):
        """Test platform setup raises error on critical failure."""
        from custom_components.imou_life.switch import async_setup_entry

        # Make runtime_data raise an error
        broken_entry = MagicMock()
        broken_entry.runtime_data = None  # This will cause AttributeError

        async_add_devices = MagicMock()

        with pytest.raises(AttributeError):
            await async_setup_entry(MagicMock(), broken_entry, async_add_devices)
