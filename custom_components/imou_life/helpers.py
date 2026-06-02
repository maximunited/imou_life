"""Helper utilities for the Imou Life integration."""

import re

from imouapi.exceptions import ImouException


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case for translation keys.

    Args:
        name: The camelCase string to convert

    Returns:
        The snake_case version of the string

    Examples:
        >>> camel_to_snake("batteryLevel")
        'battery_level'
        >>> camel_to_snake("motionDetect")
        'motion_detect'
        >>> camel_to_snake("camera")
        'camera'
    """
    if not isinstance(name, str):
        return str(name)
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def exception_message(exception: ImouException) -> str:
    """Extract a useful message from an ImouException, even if empty."""
    msg = str(exception).strip()
    return msg or f"{type(exception).__name__} ({exception.get_title()})"
