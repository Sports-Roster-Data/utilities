"""
Tests for height conversion utilities
"""

import pytest
from height_utils import height_to_inches, inches_to_height_str


class TestHeightToInches:
    """Test suite for height_to_inches function"""

    def test_hyphen_format(self):
        """Test hyphen format (e.g., '5-10', '6-2')"""
        assert height_to_inches("5-10") == 70
        assert height_to_inches("6-2") == 74
        assert height_to_inches("6-0") == 72
        assert height_to_inches("5-11") == 71
        assert height_to_inches("7-1") == 85

    def test_hyphen_format_with_spaces(self):
        """Test hyphen format with extra spaces"""
        assert height_to_inches("5 - 10") == 70
        assert height_to_inches("6- 2") == 74
        assert height_to_inches("6 -0") == 72

    def test_quote_format(self):
        """Test quote format (e.g., '6\\'2\"', '5\\'11')"""
        assert height_to_inches("6'2\"") == 74
        assert height_to_inches("5'11\"") == 71
        assert height_to_inches("6'0\"") == 72
        assert height_to_inches("5'10") == 70  # Without closing quote
        assert height_to_inches("6'2") == 74

    def test_quote_format_with_unicode(self):
        """Test quote format with unicode quotes"""
        assert height_to_inches("6′2″") == 74
        assert height_to_inches("5′11″") == 71

    def test_feet_only_quote(self):
        """Test feet-only with quote (e.g., '6\\'')"""
        assert height_to_inches("6'") == 72
        assert height_to_inches("5'") == 60
        assert height_to_inches("7'") == 84

    def test_text_format(self):
        """Test text format (e.g., '6 ft 2 in', '5 feet 11 inches')"""
        assert height_to_inches("6 ft 2 in") == 74
        assert height_to_inches("5 feet 11 inches") == 71
        assert height_to_inches("6 foot 0 inch") == 72
        assert height_to_inches("5ft10in") == 70
        assert height_to_inches("6ft2in") == 74

    def test_feet_only_text(self):
        """Test feet-only text format (e.g., '6 ft', '5 feet')"""
        assert height_to_inches("6 ft") == 72
        assert height_to_inches("5 feet") == 60
        assert height_to_inches("7 foot") == 84
        assert height_to_inches("6ft") == 72

    def test_inches_only_text(self):
        """Test inches-only text format (e.g., '72 in', '71 inches')"""
        assert height_to_inches("72 in") == 72
        assert height_to_inches("71 inches") == 71
        assert height_to_inches("70 inch") == 70
        assert height_to_inches("74in") == 74

    def test_plain_number_string(self):
        """Test plain number as string (assumes inches)"""
        assert height_to_inches("72") == 72
        assert height_to_inches("71") == 71
        assert height_to_inches("70") == 70

    def test_numeric_input(self):
        """Test numeric input (int and float)"""
        assert height_to_inches(72) == 72
        assert height_to_inches(71.5) == 72  # Rounds to nearest
        assert height_to_inches(70.2) == 70
        assert height_to_inches(74.8) == 75

    def test_case_insensitive(self):
        """Test that text parsing is case-insensitive"""
        assert height_to_inches("6 FT 2 IN") == 74
        assert height_to_inches("5 Feet 11 Inches") == 71
        assert height_to_inches("72 IN") == 72

    def test_invalid_formats(self):
        """Test invalid formats return None"""
        assert height_to_inches("invalid") is None
        assert height_to_inches("5'10'11") is None
        assert height_to_inches("abc") is None
        assert height_to_inches("") is None
        assert height_to_inches("   ") is None

    def test_none_input(self):
        """Test None input returns None"""
        assert height_to_inches(None) is None

    def test_edge_cases(self):
        """Test edge cases"""
        assert height_to_inches("0-0") == 0
        assert height_to_inches("10-6") == 126  # Very tall


class TestInchesToHeightStr:
    """Test suite for inches_to_height_str function"""

    def test_hyphen_format(self):
        """Test conversion to hyphen format"""
        assert inches_to_height_str(70) == "5-10"
        assert inches_to_height_str(74) == "6-2"
        assert inches_to_height_str(72) == "6-0"
        assert inches_to_height_str(71) == "5-11"

    def test_hyphen_format_explicit(self):
        """Test explicit hyphen format"""
        assert inches_to_height_str(70, format="hyphen") == "5-10"
        assert inches_to_height_str(74, format="hyphen") == "6-2"

    def test_quote_format(self):
        """Test conversion to quote format"""
        assert inches_to_height_str(70, format="quote") == "5'10\""
        assert inches_to_height_str(74, format="quote") == "6'2\""
        assert inches_to_height_str(72, format="quote") == "6'0\""

    def test_text_format(self):
        """Test conversion to text format"""
        assert inches_to_height_str(70, format="text") == "5 ft 10 in"
        assert inches_to_height_str(74, format="text") == "6 ft 2 in"
        assert inches_to_height_str(72, format="text") == "6 ft 0 in"

    def test_float_input(self):
        """Test float input (should round)"""
        assert inches_to_height_str(70.6) == "5-11"  # Rounds to 71
        assert inches_to_height_str(74.2) == "6-2"  # Rounds to 74
        assert inches_to_height_str(71.8) == "6-0"  # Rounds to 72

    def test_invalid_format(self):
        """Test invalid format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid format"):
            inches_to_height_str(70, format="invalid")

    def test_none_input(self):
        """Test None input returns None"""
        assert inches_to_height_str(None) is None

    def test_negative_input(self):
        """Test negative input returns None"""
        assert inches_to_height_str(-5) is None

    def test_zero_input(self):
        """Test zero input"""
        assert inches_to_height_str(0) == "0-0"
        assert inches_to_height_str(0, format="quote") == "0'0\""
        assert inches_to_height_str(0, format="text") == "0 ft 0 in"


class TestRoundTripConversion:
    """Test round-trip conversions"""

    def test_hyphen_round_trip(self):
        """Test converting from hyphen format and back"""
        original = "5-10"
        inches = height_to_inches(original)
        result = inches_to_height_str(inches, format="hyphen")
        assert result == original

    def test_various_round_trips(self):
        """Test various round-trip conversions"""
        test_cases = [
            ("5-10", 70),
            ("6-2", 74),
            ("6-0", 72),
            ("5-11", 71),
            ("7-1", 85),
        ]
        for original, expected_inches in test_cases:
            inches = height_to_inches(original)
            assert inches == expected_inches
            result = inches_to_height_str(inches, format="hyphen")
            assert result == original


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
