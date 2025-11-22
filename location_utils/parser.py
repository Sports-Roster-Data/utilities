"""
Parser functions for extracting and standardizing city and country names.

This module provides functionality to parse location strings (e.g., "London, England")
and standardize country names to their official ISO 3166-1 names.
"""

import re
from typing import Optional, Dict, Union

try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False


# Mapping for special cases (e.g., England, Scotland, Wales to United Kingdom)
COUNTRY_ALIASES = {
    'ENGLAND': 'United Kingdom',
    'SCOTLAND': 'United Kingdom',
    'WALES': 'United Kingdom',
    'NORTHERN IRELAND': 'United Kingdom',
    'REPUBLIC OF IRELAND': 'Ireland',
    'HOLLAND': 'Netherlands',
    'GREAT BRITAIN': 'United Kingdom',
    'UK': 'United Kingdom',
    'USA': 'United States',
    'US': 'United States',
    'UAE': 'United Arab Emirates',
}


def standardize_country_name(country: str) -> Optional[Dict[str, str]]:
    """
    Standardize a country name to its official ISO 3166-1 name.

    This function uses the pycountry library to match country names (including
    fuzzy matching) and returns standardized country information.

    Args:
        country: Country name to standardize (e.g., "England", "Sweden", "USA")

    Returns:
        Dictionary containing standardized country information with keys:
        - 'name': Official country name (e.g., "United Kingdom")
        - 'alpha_2': ISO 3166-1 alpha-2 code (e.g., "GB")
        - 'alpha_3': ISO 3166-1 alpha-3 code (e.g., "GBR")
        - 'numeric': ISO 3166-1 numeric code (e.g., "826")
        Returns None if country cannot be identified.

    Examples:
        >>> result = standardize_country_name("England")
        >>> result['name']
        'United Kingdom'
        >>> result = standardize_country_name("Sweden")
        >>> result['name']
        'Sweden'
        >>> standardize_country_name("Invalid")
        None
    """
    if not country:
        return None

    country_clean = country.strip()
    if not country_clean:
        return None

    # Check if pycountry is available
    if not PYCOUNTRY_AVAILABLE:
        # Fallback: return the input as-is if pycountry is not available
        return {
            'name': country_clean,
            'alpha_2': None,
            'alpha_3': None,
            'numeric': None,
        }

    # Check aliases first (for England, Scotland, Wales, etc.)
    country_upper = country_clean.upper()
    if country_upper in COUNTRY_ALIASES:
        country_clean = COUNTRY_ALIASES[country_upper]

    # Try exact match first
    try:
        country_obj = pycountry.countries.get(name=country_clean)
        if country_obj:
            return {
                'name': country_obj.name,
                'alpha_2': country_obj.alpha_2,
                'alpha_3': country_obj.alpha_3,
                'numeric': country_obj.numeric,
            }
    except (AttributeError, LookupError):
        pass

    # Try alpha-2 code match
    try:
        if len(country_clean) == 2:
            country_obj = pycountry.countries.get(alpha_2=country_clean.upper())
            if country_obj:
                return {
                    'name': country_obj.name,
                    'alpha_2': country_obj.alpha_2,
                    'alpha_3': country_obj.alpha_3,
                    'numeric': country_obj.numeric,
                }
    except (AttributeError, LookupError):
        pass

    # Try alpha-3 code match
    try:
        if len(country_clean) == 3:
            country_obj = pycountry.countries.get(alpha_3=country_clean.upper())
            if country_obj:
                return {
                    'name': country_obj.name,
                    'alpha_2': country_obj.alpha_2,
                    'alpha_3': country_obj.alpha_3,
                    'numeric': country_obj.numeric,
                }
    except (AttributeError, LookupError):
        pass

    # Try fuzzy matching
    try:
        matches = pycountry.countries.search_fuzzy(country_clean)
        if matches:
            # Return the first (best) match
            country_obj = matches[0]
            return {
                'name': country_obj.name,
                'alpha_2': country_obj.alpha_2,
                'alpha_3': country_obj.alpha_3,
                'numeric': country_obj.numeric,
            }
    except LookupError:
        pass

    # If all matching fails, return None
    return None


def parse_city_country(
    location: str,
    standardize: bool = True
) -> Optional[Dict[str, Union[str, Dict[str, str]]]]:
    """
    Parse a location string to extract city and country names.

    This function parses location strings in the format "City, Country" and
    optionally standardizes the country name using ISO 3166-1 data.

    Args:
        location: Location string (e.g., "London, England" or "Stockholm, Sweden")
        standardize: If True, standardize country names to ISO 3166-1 format (default: True)

    Returns:
        Dictionary containing:
        - 'city': City name (e.g., "London")
        - 'country_input': Original country string as provided (e.g., "England")
        - 'country': Standardized country information dict (if standardize=True)
                     or original country string (if standardize=False)
        Returns None if the location string cannot be parsed.

    Examples:
        >>> result = parse_city_country("London, England")
        >>> result['city']
        'London'
        >>> result['country_input']
        'England'
        >>> result['country']['name']
        'United Kingdom'

        >>> result = parse_city_country("Stockholm, Sweden")
        >>> result['city']
        'Stockholm'
        >>> result['country']['name']
        'Sweden'

        >>> result = parse_city_country("Paris", standardize=False)
        None

        >>> result = parse_city_country("Tokyo, Japan", standardize=False)
        >>> result['country']
        'Japan'
    """
    if not location:
        return None

    location_clean = location.strip()
    if not location_clean:
        return None

    # Split by comma - expecting format "City, Country"
    parts = [part.strip() for part in location_clean.split(',')]

    # We need at least 2 parts (city and country)
    if len(parts) < 2:
        return None

    # Handle cases like "City, State, Country" by taking the last part as country
    city = parts[0]
    country_input = parts[-1]

    # If there are more than 2 parts, join the middle parts with the city
    # Example: "New York, NY, USA" -> city="New York, NY", country="USA"
    if len(parts) > 2:
        city = ', '.join(parts[:-1])

    if not city or not country_input:
        return None

    result = {
        'city': city,
        'country_input': country_input,
    }

    if standardize:
        country_info = standardize_country_name(country_input)
        result['country'] = country_info
    else:
        result['country'] = country_input

    return result
