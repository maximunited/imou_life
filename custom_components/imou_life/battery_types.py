"""Battery type definitions for Imou camera models.

This module provides battery type information for different Imou camera models
to improve compatibility with HA-Battery-Notes integration.
"""

from typing import Dict, Optional, TypedDict


class BatterySpec(TypedDict):
    """Battery specification for a device model."""

    battery_type: str  # e.g., "18650", "CR123A", "Rechargeable Li-ion 5200mAh"
    battery_quantity: int  # Number of batteries
    is_rechargeable: bool  # Whether battery is rechargeable
    typical_life_days: Optional[int]  # Typical battery life in days (for replaceable)


# Battery specifications by camera model
# Based on Imou official specifications
BATTERY_SPECS: Dict[str, BatterySpec] = {
    # Cell series - Battery powered cameras
    "IPC-A26HP": {
        "battery_type": "Rechargeable Li-ion 5200mAh",
        "battery_quantity": 1,
        "is_rechargeable": True,
        "typical_life_days": None,  # Rechargeable, not applicable
    },
    "IPC-A26Z": {
        "battery_type": "Rechargeable Li-ion 5200mAh",
        "battery_quantity": 1,
        "is_rechargeable": True,
        "typical_life_days": None,
    },
    # Cell 2 series - 5200mAh rechargeable (FRB20 battery)
    "IPC-B46L": {
        "battery_type": "Rechargeable Li-ion 5200mAh",
        "battery_quantity": 1,
        "is_rechargeable": True,
        "typical_life_days": None,
    },
    "IPC-B46LP": {
        "battery_type": "Rechargeable Li-ion 5200mAh",
        "battery_quantity": 1,
        "is_rechargeable": True,
        "typical_life_days": None,
    },
    "IPC-B46LN": {
        "battery_type": "Rechargeable Li-ion 5200mAh",
        "battery_quantity": 1,
        "is_rechargeable": True,
        "typical_life_days": None,
    },
    # Cell Pro series
    "IPC-A28HWP": {
        "battery_type": "Rechargeable Li-ion 10400mAh",
        "battery_quantity": 1,
        "is_rechargeable": True,
        "typical_life_days": None,
    },
    # Cell Go series - Ultra-low power
    "IPC-A22E": {
        "battery_type": "4× AA",
        "battery_quantity": 4,
        "is_rechargeable": False,
        "typical_life_days": 180,  # ~6 months typical
    },
    "IPC-A22EP": {
        "battery_type": "4× AA",
        "battery_quantity": 4,
        "is_rechargeable": False,
        "typical_life_days": 180,
    },
    # Add more models as needed
}


def get_battery_spec(model: str) -> Optional[BatterySpec]:
    """Get battery specification for a camera model.

    Args:
        model: Camera model number (e.g., "IPC-A26HP")

    Returns:
        BatterySpec dict if model is known, None otherwise
    """
    # Direct match
    if model in BATTERY_SPECS:
        return BATTERY_SPECS[model]

    # Try prefix matching for variants (e.g., IPC-A26HP-5M → IPC-A26HP)
    for known_model, spec in BATTERY_SPECS.items():
        if model.startswith(known_model):
            return spec

    return None


def is_battery_powered(model: str) -> bool:
    """Check if a camera model is battery powered.

    Args:
        model: Camera model number

    Returns:
        True if model has battery specifications, False otherwise
    """
    return get_battery_spec(model) is not None


def is_rechargeable_model(model: str) -> bool:
    """Check if a camera model uses rechargeable batteries.

    Args:
        model: Camera model number

    Returns:
        True if model uses rechargeable battery, False if replaceable or unknown
    """
    spec = get_battery_spec(model)
    return spec["is_rechargeable"] if spec else False
