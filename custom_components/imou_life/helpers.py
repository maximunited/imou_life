"""Helper utilities for the Imou Life integration."""

import re


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
