"""Rate limit state manager for Imou API.

Manages global rate limit state across all devices sharing the same API credentials.
This prevents multiple devices from hammering the API after one hits a rate limit.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    RATE_LIMIT_BACKOFF_SECONDS,
    RATE_LIMIT_CACHE_KEY,
    RATE_LIMIT_MAX_PROBE_RETRIES,
    RATE_LIMIT_RESET_ESTIMATE_HOURS,
)

_LOGGER = logging.getLogger(__package__)


@dataclass
class RateLimitState:
    """Rate limit state for a specific API credential pair."""

    app_id: str
    last_rate_limit_time: datetime
    estimated_reset_time: datetime
    error_message: str
    hit_count: int = 1


class RateLimitManager:
    """Manage rate limit state for Imou API credentials."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the rate limit manager."""
        self.hass = hass
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Ensure storage exists in hass.data."""
        if DOMAIN not in self.hass.data:
            self.hass.data[DOMAIN] = {}
        if RATE_LIMIT_CACHE_KEY not in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][RATE_LIMIT_CACHE_KEY] = {}

    def _get_storage(self) -> dict[str, RateLimitState]:
        """Get rate limit storage dict."""
        return self.hass.data[DOMAIN][RATE_LIMIT_CACHE_KEY]

    def _get_credential_key(self, app_id: str, _app_secret: str) -> str:
        """Generate a key for API credentials.

        We only use app_id as the key since it uniquely identifies the account.
        app_secret is not used to avoid storing sensitive data in the key.

        Args:
            app_id: The Imou API App ID
            _app_secret: Not used, kept for API consistency

        """
        return app_id

    def record_rate_limit(
        self, app_id: str, _app_secret: str, error_message: str
    ) -> None:
        """Record a rate limit error for API credentials.

        Args:
            app_id: The Imou API App ID
            _app_secret: Not currently used, kept for API consistency
            error_message: The error message from the API

        """
        key = self._get_credential_key(app_id, _app_secret)
        storage = self._get_storage()
        now = dt_util.utcnow()

        if key in storage:
            state = storage[key]
            if now >= state.estimated_reset_time:
                # Previous wait expired but API is still limited — fresh cycle
                state.estimated_reset_time = now + timedelta(
                    hours=RATE_LIMIT_RESET_ESTIMATE_HOURS
                )
                state.hit_count = 1
            else:
                state.hit_count += 1
            state.last_rate_limit_time = now
            state.error_message = error_message
        else:
            # Create new state
            storage[key] = RateLimitState(
                app_id=app_id,
                last_rate_limit_time=now,
                estimated_reset_time=now
                + timedelta(hours=RATE_LIMIT_RESET_ESTIMATE_HOURS),
                error_message=error_message,
                hit_count=1,
            )

        _LOGGER.debug(
            "Recorded rate limit for app_id %s (hit #%d, reset estimated at %s)",
            app_id,
            storage[key].hit_count,
            storage[key].estimated_reset_time.isoformat(),
        )

    def is_rate_limited(
        self, app_id: str, _app_secret: str
    ) -> tuple[bool, dict[str, str | int] | None]:
        """Check if API credentials are currently rate limited.

        Args:
            app_id: The Imou API App ID
            _app_secret: Not currently used, kept for API consistency

        Returns:
            Tuple of (is_limited, data):
            - is_limited: True if currently rate limited
            - data: Dict with backoff_seconds, reset_time, and error, or None

        """
        key = self._get_credential_key(app_id, _app_secret)
        storage = self._get_storage()

        if key not in storage:
            return False, None

        state = storage[key]
        now = dt_util.utcnow()

        # Check if we're past the estimated reset time
        if now >= state.estimated_reset_time:
            # Rate limit should have cleared by now
            _LOGGER.debug(
                "Rate limit for app_id %s has expired (reset time passed)", app_id
            )
            # Don't delete the state - let a successful API call clear it
            return False, None

        # Scale backoff with hit count to avoid repeated retries
        scaled_backoff = RATE_LIMIT_BACKOFF_SECONDS * state.hit_count
        time_since_last_error = (now - state.last_rate_limit_time).total_seconds()
        if time_since_last_error < scaled_backoff:
            backoff_remaining = scaled_backoff - int(time_since_last_error)
            data = {
                "backoff_seconds": backoff_remaining,
                "reset_time": state.estimated_reset_time.strftime("%H:%M:%S"),
                "error": state.error_message,
            }
            _LOGGER.debug(
                "Rate limit active for app_id %s: %d seconds remaining in backoff",
                app_id,
                backoff_remaining,
            )
            return True, data

        # Past backoff but before estimated reset
        if state.hit_count >= RATE_LIMIT_MAX_PROBE_RETRIES:
            # Too many consecutive failures — wait for estimated reset
            remaining = int((state.estimated_reset_time - now).total_seconds())
            data = {
                "backoff_seconds": remaining,
                "reset_time": state.estimated_reset_time.strftime("%H:%M:%S"),
                "error": state.error_message,
            }
            _LOGGER.debug(
                "Rate limit for app_id %s: %d consecutive hits, "
                "waiting for reset at %s (%ds remaining)",
                app_id,
                state.hit_count,
                state.estimated_reset_time.strftime("%H:%M:%S"),
                remaining,
            )
            return True, data

        # Allow probe retry
        _LOGGER.debug(
            "Rate limit backoff period expired for app_id %s, allowing retry attempt",
            app_id,
        )
        return False, None

    def clear_rate_limit(self, app_id: str, _app_secret: str) -> None:
        """Clear rate limit state after successful API call.

        Args:
            app_id: The Imou API App ID
            _app_secret: Not currently used, kept for API consistency

        """
        key = self._get_credential_key(app_id, _app_secret)
        storage = self._get_storage()

        if key in storage:
            _LOGGER.debug("Clearing rate limit state for app_id %s", app_id)
            del storage[key]

    def get_state(self, app_id: str, _app_secret: str) -> RateLimitState | None:
        """Get the current rate limit state.

        Args:
            app_id: The Imou API App ID
            _app_secret: Not currently used, kept for API consistency

        Returns:
            RateLimitState if exists, None otherwise

        """
        key = self._get_credential_key(app_id, _app_secret)
        return self._get_storage().get(key)
