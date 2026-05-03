"""Tests for platform setup utilities."""

from unittest.mock import MagicMock

import pytest

from custom_components.imou_life.entity import ImouEntity
from custom_components.imou_life.platform_setup import setup_platform


class TestPlatformSetup:
    """Test platform setup utility function."""

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

    @pytest.fixture
    def mock_entity_class(self):
        """Create a mock entity class."""

        class MockEntity(ImouEntity):
            """Mock entity class for testing."""

            def __init__(self, coordinator, entry, sensor_instance, entity_id_format):
                """Initialize mock entity."""
                super().__init__(coordinator, entry, sensor_instance, entity_id_format)
                self._sensor_instance = sensor_instance

        return MockEntity

    @pytest.mark.asyncio
    async def test_setup_platform_no_sensors(
        self, mock_config_entry, mock_coordinator, mock_entity_class
    ):
        """Test platform setup with no sensors."""
        async_add_devices = MagicMock()

        await setup_platform(
            MagicMock(),
            mock_config_entry,
            "sensor",
            mock_entity_class,
            "sensor.{}",
            async_add_devices,
        )

        # Should call async_add_devices with empty list
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 0
        assert len(mock_coordinator.entities) == 0

    @pytest.mark.asyncio
    async def test_setup_platform_with_sensors(
        self, mock_config_entry, mock_coordinator, mock_entity_class
    ):
        """Test platform setup with multiple sensors."""
        # Create mock sensor instances
        sensor1 = MagicMock()
        sensor1.get_name.return_value = "sensor1"
        sensor1.get_description.return_value = "Sensor 1"

        sensor2 = MagicMock()
        sensor2.get_name.return_value = "sensor2"
        sensor2.get_description.return_value = "Sensor 2"

        sensor3 = MagicMock()
        sensor3.get_name.return_value = "sensor3"
        sensor3.get_description.return_value = "Sensor 3"

        mock_coordinator.device.get_sensors_by_platform.return_value = [
            sensor1,
            sensor2,
            sensor3,
        ]

        async_add_devices = MagicMock()

        await setup_platform(
            MagicMock(),
            mock_config_entry,
            "sensor",
            mock_entity_class,
            "sensor.{}",
            async_add_devices,
        )

        # Should add 3 entities
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 3
        assert len(mock_coordinator.entities) == 3

        # Verify entities are instances of the correct class
        for entity in added_devices:
            assert isinstance(entity, mock_entity_class)

    @pytest.mark.asyncio
    async def test_setup_platform_correct_platform_name(
        self, mock_config_entry, mock_coordinator, mock_entity_class
    ):
        """Test that platform name is correctly passed to get_sensors_by_platform."""
        async_add_devices = MagicMock()

        await setup_platform(
            MagicMock(),
            mock_config_entry,
            "binary_sensor",
            mock_entity_class,
            "binary_sensor.{}",
            async_add_devices,
        )

        # Verify get_sensors_by_platform was called with correct platform name
        mock_coordinator.device.get_sensors_by_platform.assert_called_once_with(
            "binary_sensor"
        )

    @pytest.mark.asyncio
    async def test_setup_platform_entity_id_format(
        self, mock_config_entry, mock_coordinator, mock_entity_class
    ):
        """Test that entity_id_format is passed to entity constructor."""
        sensor1 = MagicMock()
        sensor1.get_name.return_value = "testSensor"
        sensor1.get_description.return_value = "Test Sensor"

        mock_coordinator.device.get_sensors_by_platform.return_value = [sensor1]

        async_add_devices = MagicMock()

        await setup_platform(
            MagicMock(),
            mock_config_entry,
            "sensor",
            mock_entity_class,
            "sensor.test_{}",
            async_add_devices,
        )

        # The entity should be created with the provided entity_id_format
        async_add_devices.assert_called_once()
        added_devices = async_add_devices.call_args[0][0]
        assert len(added_devices) == 1

    @pytest.mark.asyncio
    async def test_setup_platform_coordinator_entities_list(
        self, mock_config_entry, mock_coordinator, mock_entity_class
    ):
        """Test that entities are added to coordinator.entities list."""
        sensor1 = MagicMock()
        sensor1.get_name.return_value = "sensor1"
        sensor1.get_description.return_value = "Sensor 1"

        sensor2 = MagicMock()
        sensor2.get_name.return_value = "sensor2"
        sensor2.get_description.return_value = "Sensor 2"

        mock_coordinator.device.get_sensors_by_platform.return_value = [
            sensor1,
            sensor2,
        ]

        async_add_devices = MagicMock()

        # Verify coordinator.entities starts empty
        assert len(mock_coordinator.entities) == 0

        await setup_platform(
            MagicMock(),
            mock_config_entry,
            "sensor",
            mock_entity_class,
            "sensor.{}",
            async_add_devices,
        )

        # Verify both entities were added to coordinator.entities
        assert len(mock_coordinator.entities) == 2
