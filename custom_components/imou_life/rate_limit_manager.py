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
    RATE_LIMIT_RESET_ESTIMATE_HOURS,
)

_LOGGER = logging.getLogger(__name__)


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

    def _get_credential_key(self, app_id: str, app_secret: str) -> str:
        """Generate a key for API credentials.

        We only use app_id as the key since it uniquely identifies the account.
        app_secret is not included to avoid storing sensitive data in the key.
        """
        return app_id

    def record_rate_limit(
        self, app_id: str, app_secret: str, error_message: str
    ) -> None:
        """Record a rate limit error for API credentials.

        Args:
            app_id: The Imou API App ID
            app_secret: The Imou API App Secret (used for key generation only)
            error_message: The error message from the API

        """
        key = self._get_credential_key(app_id, app_secret)
        storage = self._get_storage()
        now = dt_util.utcnow()

        if key in storage:
            # Update existing state
            state = storage[key]
            state.last_rate_limit_time = now
            state.estimated_reset_time = now + timedelta(
                hours=RATE_LIMIT_RESET_ESTIMATE_HOURS
            )
            state.error_message = error_message
            state.hit_count += 1
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

    def is_rate_limited(self, app_id: str, app_secret: str) -> tuple[bool, str | None]:
        """Check if API credentials are currently rate limited.

        Args:
            app_id: The Imou API App ID
            app_secret: The Imou API App Secret (used for key generation only)

        Returns:
            Tuple of (is_limited, message):
            - is_limited: True if currently rate limited
            - message: User-friendly message explaining the rate limit state, or None

        """
        key = self._get_credential_key(app_id, app_secret)
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

        # Check if we're within the minimum backoff period
        time_since_last_error = (now - state.last_rate_limit_time).total_seconds()
        if time_since_last_error < RATE_LIMIT_BACKOFF_SECONDS:
            backoff_remaining = RATE_LIMIT_BACKOFF_SECONDS - int(time_since_last_error)
            message = (
                f"API rate limit active. Retrying in {backoff_remaining}s. "
                f"Estimated reset: {state.estimated_reset_time.strftime('%H:%M:%S')} UTC. "
                f"Error: {state.error_message}"
            )
            _LOGGER.debug(
                "Rate limit active for app_id %s: %d seconds remaining in backoff",
                app_id,
                backoff_remaining,
            )
            return True, message

        # We're past the minimum backoff but before estimated reset
        # Allow retry attempt - if it fails, we'll update the state again
        _LOGGER.debug(
            "Rate limit backoff period expired for app_id %s, allowing retry attempt",
            app_id,
        )
        return False, None

    def clear_rate_limit(self, app_id: str, app_secret: str) -> None:
        """Clear rate limit state after successful API call.

        Args:
            app_id: The Imou API App ID
            app_secret: The Imou API App Secret (used for key generation only)

        """
        key = self._get_credential_key(app_id, app_secret)
        storage = self._get_storage()

        if key in storage:
            _LOGGER.debug("Clearing rate limit state for app_id %s", app_id)
            del storage[key]

    def get_state(self, app_id: str, app_secret: str) -> RateLimitState | None:
        """Get the current rate limit state.

        Args:
            app_id: The Imou API App ID
            app_secret: The Imou API App Secret (used for key generation only)

        Returns:
            RateLimitState if exists, None otherwise

        """
        key = self._get_credential_key(app_id, app_secret)
        return self._get_storage().get(key)
