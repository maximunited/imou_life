"""Test rate limit manager."""

from datetime import timedelta
from unittest.mock import Mock

import pytest
from homeassistant.util import dt as dt_util

from custom_components.imou_life.const import (
    RATE_LIMIT_BACKOFF_SECONDS,
    RATE_LIMIT_RESET_ESTIMATE_HOURS,
)
from custom_components.imou_life.rate_limit_manager import RateLimitManager


@pytest.fixture
def mock_hass() -> Mock:
    """Create a mock HomeAssistant instance."""
    hass = Mock()
    hass.data = {}
    return hass


@pytest.fixture
def rate_limit_mgr(mock_hass: Mock) -> RateLimitManager:
    """Create a rate limit manager instance."""
    return RateLimitManager(mock_hass)


def test_initialization(rate_limit_mgr: RateLimitManager, mock_hass: Mock) -> None:
    """Test manager initializes storage correctly."""
    from custom_components.imou_life.const import DOMAIN, RATE_LIMIT_CACHE_KEY

    assert DOMAIN in mock_hass.data
    assert RATE_LIMIT_CACHE_KEY in mock_hass.data[DOMAIN]
    assert isinstance(mock_hass.data[DOMAIN][RATE_LIMIT_CACHE_KEY], dict)


def test_no_rate_limit_initially(rate_limit_mgr: RateLimitManager) -> None:
    """Test that new credentials are not rate limited."""
    is_limited, data = rate_limit_mgr.is_rate_limited("test_app_id", "test_secret")

    assert is_limited is False
    assert data is None


def test_record_rate_limit(rate_limit_mgr: RateLimitManager) -> None:
    """Test recording a rate limit error."""
    app_id = "test_app_id"
    app_secret = "test_secret"
    error_msg = "OP1013: Call interface times exceed limit"

    rate_limit_mgr.record_rate_limit(app_id, app_secret, error_msg)

    # Should now be rate limited
    is_limited, data = rate_limit_mgr.is_rate_limited(app_id, app_secret)
    assert is_limited is True
    assert data is not None
    assert "backoff_seconds" in data
    assert "reset_time" in data
    assert "error" in data


def test_rate_limit_state_tracking(rate_limit_mgr: RateLimitManager) -> None:
    """Test that rate limit state is tracked correctly."""
    app_id = "test_app_id"
    app_secret = "test_secret"
    error_msg = "OP1013: exceed limit"

    rate_limit_mgr.record_rate_limit(app_id, app_secret, error_msg)
    state = rate_limit_mgr.get_state(app_id, app_secret)

    assert state is not None
    assert state.app_id == app_id
    assert state.error_message == error_msg
    assert state.hit_count == 1
    assert state.estimated_reset_time > dt_util.utcnow()


def test_multiple_rate_limit_hits(rate_limit_mgr: RateLimitManager) -> None:
    """Test that multiple rate limit hits are counted."""
    app_id = "test_app_id"
    app_secret = "test_secret"

    # Record first hit
    rate_limit_mgr.record_rate_limit(app_id, app_secret, "Error 1")
    state1 = rate_limit_mgr.get_state(app_id, app_secret)
    assert state1.hit_count == 1

    # Record second hit
    rate_limit_mgr.record_rate_limit(app_id, app_secret, "Error 2")
    state2 = rate_limit_mgr.get_state(app_id, app_secret)
    assert state2.hit_count == 2
    assert state2.error_message == "Error 2"  # Updated to latest


def test_backoff_period_enforcement(rate_limit_mgr: RateLimitManager) -> None:
    """Test that backoff period is enforced."""
    app_id = "test_app_id"
    app_secret = "test_secret"

    # Record rate limit
    rate_limit_mgr.record_rate_limit(app_id, app_secret, "OP1013")

    # Immediately check - should be limited
    is_limited, _ = rate_limit_mgr.is_rate_limited(app_id, app_secret)
    assert is_limited is True

    # Manually set the rate limit time to the past (simulate time passing)
    state = rate_limit_mgr.get_state(app_id, app_secret)
    state.last_rate_limit_time = dt_util.utcnow() - timedelta(
        seconds=RATE_LIMIT_BACKOFF_SECONDS / 2
    )

    # Still within backoff period
    is_limited, _ = rate_limit_mgr.is_rate_limited(app_id, app_secret)
    assert is_limited is True

    # Set time past backoff period
    state.last_rate_limit_time = dt_util.utcnow() - timedelta(
        seconds=RATE_LIMIT_BACKOFF_SECONDS + 1
    )
    is_limited, _ = rate_limit_mgr.is_rate_limited(app_id, app_secret)
    assert is_limited is False  # Allows retry attempt


def test_estimated_reset_time(rate_limit_mgr: RateLimitManager) -> None:
    """Test that estimated reset time works correctly."""
    app_id = "test_app_id"
    app_secret = "test_secret"

    start_time = dt_util.utcnow()
    rate_limit_mgr.record_rate_limit(app_id, app_secret, "OP1013")

    state = rate_limit_mgr.get_state(app_id, app_secret)
    expected_reset = start_time + timedelta(hours=RATE_LIMIT_RESET_ESTIMATE_HOURS)

    # Check reset time is approximately correct (within 2 seconds to account for execution time)
    time_diff = abs((state.estimated_reset_time - expected_reset).total_seconds())
    assert time_diff < 2


def test_clear_rate_limit(rate_limit_mgr: RateLimitManager) -> None:
    """Test clearing rate limit state."""
    app_id = "test_app_id"
    app_secret = "test_secret"

    # Record rate limit
    rate_limit_mgr.record_rate_limit(app_id, app_secret, "OP1013")
    assert rate_limit_mgr.get_state(app_id, app_secret) is not None

    # Clear it
    rate_limit_mgr.clear_rate_limit(app_id, app_secret)
    assert rate_limit_mgr.get_state(app_id, app_secret) is None

    # Should no longer be limited
    is_limited, _ = rate_limit_mgr.is_rate_limited(app_id, app_secret)
    assert is_limited is False


def test_different_credentials_isolated(rate_limit_mgr: RateLimitManager) -> None:
    """Test that different credentials are tracked separately."""
    app_id_1 = "app_id_1"
    app_id_2 = "app_id_2"
    app_secret = "secret"

    # Rate limit first credential
    rate_limit_mgr.record_rate_limit(app_id_1, app_secret, "OP1013")

    # First should be limited
    is_limited_1, _ = rate_limit_mgr.is_rate_limited(app_id_1, app_secret)
    assert is_limited_1 is True

    # Second should not be limited
    is_limited_2, _ = rate_limit_mgr.is_rate_limited(app_id_2, app_secret)
    assert is_limited_2 is False


def test_reset_after_estimated_time(rate_limit_mgr: RateLimitManager) -> None:
    """Test that rate limit allows retry after estimated reset time."""
    app_id = "test_app_id"
    app_secret = "test_secret"

    rate_limit_mgr.record_rate_limit(app_id, app_secret, "OP1013")

    # Should be limited initially
    is_limited, _ = rate_limit_mgr.is_rate_limited(app_id, app_secret)
    assert is_limited is True

    # Manually set estimated reset time to the past (simulate time passing)
    state = rate_limit_mgr.get_state(app_id, app_secret)
    state.estimated_reset_time = dt_util.utcnow() - timedelta(minutes=1)

    # Should no longer be limited (allows retry)
    is_limited, _ = rate_limit_mgr.is_rate_limited(app_id, app_secret)
    assert is_limited is False


def test_message_content(rate_limit_mgr: RateLimitManager) -> None:
    """Test that rate limit data contains useful information."""
    app_id = "test_app_id"
    app_secret = "test_secret"
    error_msg = "OP1013: Call interface times exceed limit (total)"

    rate_limit_mgr.record_rate_limit(app_id, app_secret, error_msg)
    is_limited, data = rate_limit_mgr.is_rate_limited(app_id, app_secret)

    assert is_limited is True
    assert data is not None
    assert "backoff_seconds" in data
    assert "reset_time" in data  # Should show reset time
    assert "error" in data
    assert data["error"] == error_msg
