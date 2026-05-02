"""Tests for battery type definitions."""

from custom_components.imou_life.battery_types import (
    BATTERY_SPECS,
    get_battery_spec,
    is_battery_powered,
    is_rechargeable_model,
)


class TestBatteryTypes:
    """Test battery type utilities."""

    def test_get_battery_spec_direct_match(self):
        """Test getting battery spec with direct model match."""
        spec = get_battery_spec("IPC-A26HP")

        assert spec is not None
        assert spec["battery_type"] == "Rechargeable Li-ion 5200mAh"
        assert spec["battery_quantity"] == 1
        assert spec["is_rechargeable"] is True
        assert spec["typical_life_days"] is None

    def test_get_battery_spec_all_models(self):
        """Test that all models in BATTERY_SPECS are accessible."""
        for model in BATTERY_SPECS:
            spec = get_battery_spec(model)
            assert spec is not None
            assert spec == BATTERY_SPECS[model]

    def test_get_battery_spec_prefix_match(self):
        """Test getting battery spec with prefix matching for variants."""
        # Variant model with suffix
        spec = get_battery_spec("IPC-A26HP-5M")

        assert spec is not None
        assert spec["battery_type"] == "Rechargeable Li-ion 5200mAh"
        assert spec["battery_quantity"] == 1
        assert spec["is_rechargeable"] is True

    def test_get_battery_spec_unknown_model(self):
        """Test getting battery spec for unknown model returns None."""
        spec = get_battery_spec("UNKNOWN-MODEL-123")

        assert spec is None

    def test_get_battery_spec_partial_match_not_prefix(self):
        """Test that partial match that's not a prefix returns None."""
        # "A26HP" is part of "IPC-A26HP" but not a prefix
        spec = get_battery_spec("A26HP")

        assert spec is None

    def test_is_battery_powered_known_model(self):
        """Test is_battery_powered returns True for known models."""
        assert is_battery_powered("IPC-A26HP") is True
        assert is_battery_powered("IPC-A22E") is True
        assert is_battery_powered("IPC-B46L") is True

    def test_is_battery_powered_variant_model(self):
        """Test is_battery_powered returns True for model variants."""
        assert is_battery_powered("IPC-A26HP-5M") is True
        assert is_battery_powered("IPC-A22E-V2") is True

    def test_is_battery_powered_unknown_model(self):
        """Test is_battery_powered returns False for unknown models."""
        assert is_battery_powered("UNKNOWN-MODEL") is False
        assert is_battery_powered("IPC-XXXXX") is False

    def test_is_rechargeable_model_true(self):
        """Test is_rechargeable_model returns True for rechargeable models."""
        # IPC-A26HP has rechargeable battery
        assert is_rechargeable_model("IPC-A26HP") is True
        assert is_rechargeable_model("IPC-B46L") is True
        assert is_rechargeable_model("IPC-A28HWP") is True

    def test_is_rechargeable_model_false(self):
        """Test is_rechargeable_model returns False for replaceable battery models."""
        # IPC-A22E has replaceable AA batteries
        assert is_rechargeable_model("IPC-A22E") is False
        assert is_rechargeable_model("IPC-A22EP") is False

    def test_is_rechargeable_model_unknown(self):
        """Test is_rechargeable_model returns False for unknown models."""
        assert is_rechargeable_model("UNKNOWN-MODEL") is False
        assert is_rechargeable_model("IPC-XXXXX") is False

    def test_is_rechargeable_model_variant(self):
        """Test is_rechargeable_model works with model variants."""
        # Rechargeable model variant
        assert is_rechargeable_model("IPC-A26HP-5M") is True
        # Replaceable battery model variant
        assert is_rechargeable_model("IPC-A22E-V2") is False

    def test_battery_specs_structure(self):
        """Test that all battery specs have required fields."""
        required_fields = [
            "battery_type",
            "battery_quantity",
            "is_rechargeable",
            "typical_life_days",
        ]

        for model, spec in BATTERY_SPECS.items():
            for field in required_fields:
                assert field in spec, f"Model {model} missing field {field}"

    def test_battery_specs_types(self):
        """Test that battery spec values have correct types."""
        for _model, spec in BATTERY_SPECS.items():
            assert isinstance(spec["battery_type"], str)
            assert isinstance(spec["battery_quantity"], int)
            assert isinstance(spec["is_rechargeable"], bool)
            assert spec["typical_life_days"] is None or isinstance(
                spec["typical_life_days"], int
            )

    def test_battery_specs_rechargeable_no_life_days(self):
        """Test that rechargeable batteries have None for typical_life_days."""
        for model, spec in BATTERY_SPECS.items():
            if spec["is_rechargeable"]:
                assert (
                    spec["typical_life_days"] is None
                ), f"Rechargeable model {model} should have None for typical_life_days"

    def test_battery_specs_replaceable_has_life_days(self):
        """Test that replaceable batteries have typical_life_days set."""
        for model, spec in BATTERY_SPECS.items():
            if not spec["is_rechargeable"]:
                assert (
                    spec["typical_life_days"] is not None
                ), f"Replaceable battery model {model} should have typical_life_days"
