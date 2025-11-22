"""
Tests for location parsing utilities.
"""

import pytest
from location_utils import parse_city_country, standardize_country_name


class TestStandardizeCountryName:
    """Tests for standardize_country_name function."""

    def test_standard_country_names(self):
        """Test standardization of common country names."""
        result = standardize_country_name("Sweden")
        assert result is not None
        assert result['name'] == "Sweden"
        assert result['alpha_2'] == "SE"
        assert result['alpha_3'] == "SWE"

        result = standardize_country_name("Japan")
        assert result is not None
        assert result['name'] == "Japan"
        assert result['alpha_2'] == "JP"

    def test_england_to_uk(self):
        """Test that England maps to United Kingdom."""
        result = standardize_country_name("England")
        assert result is not None
        assert result['name'] == "United Kingdom"
        assert result['alpha_2'] == "GB"

    def test_scotland_to_uk(self):
        """Test that Scotland maps to United Kingdom."""
        result = standardize_country_name("Scotland")
        assert result is not None
        assert result['name'] == "United Kingdom"

    def test_wales_to_uk(self):
        """Test that Wales maps to United Kingdom."""
        result = standardize_country_name("Wales")
        assert result is not None
        assert result['name'] == "United Kingdom"

    def test_usa_aliases(self):
        """Test USA aliases (USA, US)."""
        result = standardize_country_name("USA")
        assert result is not None
        assert result['name'] == "United States"

        result = standardize_country_name("US")
        assert result is not None
        assert result['name'] == "United States"

    def test_iso_codes(self):
        """Test that ISO codes are recognized."""
        # Alpha-2 code
        result = standardize_country_name("GB")
        assert result is not None
        assert result['name'] == "United Kingdom"

        # Alpha-3 code
        result = standardize_country_name("SWE")
        assert result is not None
        assert result['name'] == "Sweden"

    def test_fuzzy_matching(self):
        """Test fuzzy matching for alternative country names."""
        # Note: fuzzy matching behavior depends on pycountry implementation
        # Test with full official name that should fuzzy match
        result = standardize_country_name("United States of America")
        assert result is not None
        assert result['name'] == "United States"

    def test_invalid_country(self):
        """Test that invalid country names return None."""
        result = standardize_country_name("NotACountry123")
        assert result is None

    def test_empty_input(self):
        """Test that empty input returns None."""
        assert standardize_country_name("") is None
        assert standardize_country_name("   ") is None
        assert standardize_country_name(None) is None

    def test_case_insensitive(self):
        """Test that country name matching is case-insensitive."""
        result = standardize_country_name("england")
        assert result is not None
        assert result['name'] == "United Kingdom"

        result = standardize_country_name("SWEDEN")
        assert result is not None
        assert result['name'] == "Sweden"


class TestParseCityCountry:
    """Tests for parse_city_country function."""

    def test_basic_parsing(self):
        """Test basic city, country parsing."""
        result = parse_city_country("London, England")
        assert result is not None
        assert result['city'] == "London"
        assert result['country_input'] == "England"
        assert result['country'] is not None
        assert result['country']['name'] == "United Kingdom"

    def test_stockholm_sweden(self):
        """Test Stockholm, Sweden example."""
        result = parse_city_country("Stockholm, Sweden")
        assert result is not None
        assert result['city'] == "Stockholm"
        assert result['country_input'] == "Sweden"
        assert result['country']['name'] == "Sweden"
        assert result['country']['alpha_2'] == "SE"

    def test_tokyo_japan(self):
        """Test Tokyo, Japan example."""
        result = parse_city_country("Tokyo, Japan")
        assert result is not None
        assert result['city'] == "Tokyo"
        assert result['country']['name'] == "Japan"

    def test_paris_france(self):
        """Test Paris, France example."""
        result = parse_city_country("Paris, France")
        assert result is not None
        assert result['city'] == "Paris"
        assert result['country']['name'] == "France"

    def test_without_standardization(self):
        """Test parsing without country standardization."""
        result = parse_city_country("London, England", standardize=False)
        assert result is not None
        assert result['city'] == "London"
        assert result['country'] == "England"  # Should be string, not dict

    def test_city_state_country(self):
        """Test parsing with city, state, country format."""
        result = parse_city_country("New York, NY, USA")
        assert result is not None
        assert result['city'] == "New York, NY"
        assert result['country_input'] == "USA"
        assert result['country']['name'] == "United States"

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        result = parse_city_country("  London  ,  England  ")
        assert result is not None
        assert result['city'] == "London"
        assert result['country_input'] == "England"

    def test_invalid_formats(self):
        """Test that invalid formats return None."""
        # Single word (no comma)
        assert parse_city_country("London") is None

        # Empty string
        assert parse_city_country("") is None

        # Only whitespace
        assert parse_city_country("   ") is None

        # None
        assert parse_city_country(None) is None

        # Only comma
        assert parse_city_country(",") is None

        # Missing city
        assert parse_city_country(", England") is None

        # Missing country
        assert parse_city_country("London, ") is None

    def test_city_with_comma_in_name(self):
        """Test handling of cities that might have commas."""
        # This should take the last comma-separated value as country
        result = parse_city_country("São Paulo, SP, Brazil")
        assert result is not None
        assert result['city'] == "São Paulo, SP"
        assert result['country']['name'] == "Brazil"

    def test_special_characters(self):
        """Test that special characters in city names are preserved."""
        result = parse_city_country("São Paulo, Brazil")
        assert result is not None
        assert result['city'] == "São Paulo"

        result = parse_city_country("Zürich, Switzerland")
        assert result is not None
        assert result['city'] == "Zürich"
        assert result['country']['name'] == "Switzerland"

    def test_multiple_word_cities(self):
        """Test cities with multiple words."""
        result = parse_city_country("Los Angeles, USA")
        assert result is not None
        assert result['city'] == "Los Angeles"
        assert result['country']['name'] == "United States"

        result = parse_city_country("Buenos Aires, Argentina")
        assert result is not None
        assert result['city'] == "Buenos Aires"
        assert result['country']['name'] == "Argentina"

    def test_unrecognized_country(self):
        """Test behavior when country cannot be standardized."""
        result = parse_city_country("SomeCity, NotACountry")
        assert result is not None
        assert result['city'] == "SomeCity"
        assert result['country_input'] == "NotACountry"
        assert result['country'] is None  # Country standardization failed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
