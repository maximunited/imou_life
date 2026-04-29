"""Tests for coordinator rate limit handling."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from imouapi.exceptions import ImouException

from custom_components.imou_life.coordinator import ImouDataUpdateCoordinator


class TestCoordinatorRateLimitHandling:
    """Test coordinator rate limit detection and handling."""

    @pytest.fixture
    def hass(self):
        """Create a mock Home Assistant instance."""
        hass = MagicMock()
        hass.data = {}
        return hass

    @pytest.fixture
    def mock_device(self):
        """Create a mock ImouDevice."""
        device = MagicMock()
        device.async_get_data = AsyncMock()
        return device

    @pytest.fixture
    def coordinator(self, hass, mock_device):
        """Create a coordinator instance."""
        return ImouDataUpdateCoordinator(hass, mock_device, scan_interval=900)

    @pytest.mark.asyncio
    async def test_successful_update_clears_rate_limit(self, coordinator, mock_device):
        """Test that successful update clears rate limit status."""
        # Set up rate limited state
        coordinator.is_rate_limited = True
        coordinator.rate_limit_count = 3
        coordinator._is_interval_adjusted = True
        coordinator.update_interval = timedelta(seconds=1800)

        # Mock successful data fetch
        mock_device.async_get_data.return_value = {"battery_level": 85}

        # Perform update
        data = await coordinator._async_update_data()

        # Verify rate limit cleared
        assert coordinator.is_rate_limited is False
        assert coordinator.last_error_type is None
        assert coordinator.last_error_message is None
        assert coordinator.last_successful_update is not None
        assert data == {"battery_level": 85}

        # Verify scan interval restored
        assert coordinator._is_interval_adjusted is False
        assert coordinator.update_interval.total_seconds() == 900

    @pytest.mark.asyncio
    async def test_rate_limit_detection(self, coordinator, mock_device):
        """Test that OP1013 error is detected as rate limit."""
        # Mock rate limit error
        mock_device.async_get_data.side_effect = ImouException(
            "OP1013: Call interface times exceed limit (total)."
        )

        # Attempt update
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        # Verify rate limit detected
        assert coordinator.is_rate_limited is True
        assert coordinator.rate_limit_count == 1
        assert coordinator.last_error_type == "rate_limit"
        assert "OP1013" in coordinator.last_error_message

    @pytest.mark.asyncio
    async def test_scan_interval_adjustment_on_rate_limit(
        self, coordinator, mock_device
    ):
        """Test that scan interval doubles when rate limited."""
        original_interval = coordinator.update_interval.total_seconds()

        # Mock rate limit error
        mock_device.async_get_data.side_effect = ImouException(
            "OP1013: Call interface times exceed limit"
        )

        # Attempt update
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        # Verify interval doubled
        assert coordinator._is_interval_adjusted is True
        assert coordinator.update_interval.total_seconds() == original_interval * 2

    @pytest.mark.asyncio
    async def test_rate_limit_tracking(self, coordinator, mock_device):
        """Test rate limit start time and estimated reset."""
        # Mock rate limit error
        mock_device.async_get_data.side_effect = ImouException("OP1013: exceed limit")

        # First rate limit
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        # Verify tracking started
        assert coordinator.rate_limit_start_time is not None
        assert coordinator.rate_limit_estimated_reset is not None

        # Verify estimated reset is about 1 hour from start
        time_diff = (
            coordinator.rate_limit_estimated_reset - coordinator.rate_limit_start_time
        )
        assert 3500 <= time_diff.total_seconds() <= 3700  # ~1 hour

    @pytest.mark.asyncio
    async def test_rate_limit_count_increments(self, coordinator, mock_device):
        """Test that rate limit count increments on each occurrence."""
        mock_device.async_get_data.side_effect = ImouException("OP1013")

        # Multiple rate limit errors
        for expected_count in range(1, 6):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

            assert coordinator.rate_limit_count == expected_count

    @pytest.mark.asyncio
    async def test_non_rate_limit_error_handling(self, coordinator, mock_device):
        """Test that other API errors are not treated as rate limits."""
        # Mock different API error
        mock_device.async_get_data.side_effect = ImouException(
            "SN1003: Signature parameter error"
        )

        # Attempt update
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        # Verify not treated as rate limit
        assert coordinator.is_rate_limited is False
        assert coordinator.last_error_type == "api_error"
        assert "SN1003" in coordinator.last_error_message
        assert coordinator._is_interval_adjusted is False

    @pytest.mark.asyncio
    async def test_interval_only_adjusted_once(self, coordinator, mock_device):
        """Test that scan interval is only adjusted once."""
        original_interval = coordinator.update_interval.total_seconds()
        mock_device.async_get_data.side_effect = ImouException("OP1013")

        # First rate limit - interval should double
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        first_adjusted = coordinator.update_interval.total_seconds()
        assert first_adjusted == original_interval * 2

        # Second rate limit - interval should stay the same
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        assert coordinator.update_interval.total_seconds() == first_adjusted

    @pytest.mark.asyncio
    async def test_recovery_workflow(self, coordinator, mock_device):
        """Test complete rate limit and recovery workflow."""
        # Step 1: Rate limited
        mock_device.async_get_data.side_effect = ImouException("OP1013")

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        assert coordinator.is_rate_limited is True
        assert coordinator._is_interval_adjusted is True
        adjusted_interval = coordinator.update_interval.total_seconds()

        # Step 2: Still rate limited
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        assert coordinator.rate_limit_count == 2

        # Step 3: Recovery
        mock_device.async_get_data.side_effect = None
        mock_device.async_get_data.return_value = {"battery_level": 90}

        await coordinator._async_update_data()

        # Verify fully recovered
        assert coordinator.is_rate_limited is False
        assert coordinator._is_interval_adjusted is False
        assert coordinator.update_interval.total_seconds() < adjusted_interval
        assert coordinator.last_successful_update is not None
        assert coordinator.rate_limit_count == 2  # Count persists as history
