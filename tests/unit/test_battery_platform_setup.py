"""Tests for battery platform setup functions."""

from unittest.mock import MagicMock

import pytest


class TestBatteryBinarySensorSetup:
    """Test battery binary sensor platform setup."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock battery coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Battery Camera"
        return coordinator

    @pytest.fixture
    def mock_config_entry(self, mock_coordinator):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_battery_entry_123"
        config_entry.runtime_data = mock_coordinator
        return config_entry

    @pytest.mark.asyncio
    async def test_async_setup_entry_creates_all_sensors(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup creates all battery binary sensors."""
        from custom_components.imou_life.battery_binary_sensor import (
            async_setup_entry,
        )

        async_add_entities = MagicMock()

        await async_setup_entry(MagicMock(), mock_config_entry, async_add_entities)

        # Should add 4 binary sensors (low_battery, charging, power_saving, sleep_mode)
        async_add_entities.assert_called_once()
        added_entities = async_add_entities.call_args[0][0]
        assert len(added_entities) == 4

        # Verify sensor types
        sensor_names = [entity.sensor_type for entity in added_entities]
        assert "lowBattery" in sensor_names
        assert "charging" in sensor_names
        assert "powerSavingActive" in sensor_names
        assert "sleepModeActive" in sensor_names


class TestBatteryButtonSetup:
    """Test battery button platform setup."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock battery coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Battery Camera"
        return coordinator

    @pytest.fixture
    def mock_config_entry(self, mock_coordinator):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_battery_entry_123"
        config_entry.runtime_data = mock_coordinator
        return config_entry

    @pytest.mark.asyncio
    async def test_async_setup_entry_creates_all_buttons(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup creates all battery buttons."""
        from custom_components.imou_life.battery_button import async_setup_entry

        async_add_entities = MagicMock()

        await async_setup_entry(MagicMock(), mock_config_entry, async_add_entities)

        # Should add 4 buttons (enter_sleep, exit_sleep, optimize, reset_power)
        async_add_entities.assert_called_once()
        added_entities = async_add_entities.call_args[0][0]
        assert len(added_entities) == 4

        # Verify button types
        button_types = [entity.button_type for entity in added_entities]
        assert "enterSleepMode" in button_types
        assert "exitSleepMode" in button_types
        assert "optimizeBattery" in button_types
        assert "resetPowerSettings" in button_types


class TestBatterySelectSetup:
    """Test battery select platform setup."""

    @pytest.fixture
    def mock_coordinator(self):
        """Create a mock battery coordinator."""
        coordinator = MagicMock()
        coordinator.device = MagicMock()
        coordinator.device.get_name.return_value = "Test Battery Camera"
        return coordinator

    @pytest.fixture
    def mock_config_entry(self, mock_coordinator):
        """Create a mock config entry."""
        config_entry = MagicMock()
        config_entry.entry_id = "test_battery_entry_123"
        config_entry.runtime_data = mock_coordinator
        return config_entry

    @pytest.mark.asyncio
    async def test_async_setup_entry_creates_all_selects(
        self, mock_config_entry, mock_coordinator
    ):
        """Test platform setup creates all battery select entities."""
        from custom_components.imou_life.battery_select import async_setup_entry

        async_add_entities = MagicMock()

        await async_setup_entry(MagicMock(), mock_config_entry, async_add_entities)

        # Should add 4 select entities (power_mode, motion_sensitivity, recording_quality, sleep_schedule)
        async_add_entities.assert_called_once()
        added_entities = async_add_entities.call_args[0][0]
        assert len(added_entities) == 4

        # Verify select types
        select_types = [entity.select_type for entity in added_entities]
        assert "powerMode" in select_types
        assert "motionSensitivityLevel" in select_types
        assert "recordingQuality" in select_types
        assert "sleepSchedule" in select_types
