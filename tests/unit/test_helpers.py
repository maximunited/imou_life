"""Tests for helper utilities."""

from custom_components.imou_life.helpers import camel_to_snake


class TestCamelToSnake:
    """Test the camel_to_snake helper function."""

    def test_camel_to_snake_basic(self):
        """Test basic camelCase to snake_case conversion."""
        assert camel_to_snake("batteryLevel") == "battery_level"
        assert camel_to_snake("motionDetect") == "motion_detect"

    def test_camel_to_snake_single_word(self):
        """Test single word (no conversion needed)."""
        assert camel_to_snake("camera") == "camera"

    def test_camel_to_snake_empty_string(self):
        """Test empty string."""
        assert camel_to_snake("") == ""

    def test_camel_to_snake_already_snake(self):
        """Test already snake_case string."""
        assert camel_to_snake("already_snake") == "already_snake"

    def test_camel_to_snake_non_string_input(self):
        """Test non-string input (edge case for line 24 coverage)."""
        # Should convert to string first
        assert camel_to_snake(123) == "123"
        assert camel_to_snake(None) == "None"
        assert camel_to_snake(True) == "True"

    def test_camel_to_snake_multiple_capitals(self):
        """Test multiple consecutive capitals."""
        assert camel_to_snake("HTTPSConnection") == "h_t_t_p_s_connection"
        assert camel_to_snake("XMLParser") == "x_m_l_parser"

    def test_camel_to_snake_leading_capital(self):
        """Test leading capital letter."""
        assert camel_to_snake("BatteryLevel") == "battery_level"
        assert camel_to_snake("MotionDetect") == "motion_detect"
