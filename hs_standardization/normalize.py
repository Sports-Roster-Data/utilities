"""
High School Name Normalization

This module provides functions for normalizing and standardizing high school names
for use in data processing and matching.

Extracted from the womens-college-basketball project.
"""

import re
import pandas as pd


def normalize_hs_name(name):
    """
    Create a normalized version of a high school name for matching.
    This is conservative and designed for fuzzy matching.

    The normalization process:
    - Converts to uppercase
    - Removes common high school suffixes (High School, HS, H.S.)
    - Standardizes St./Saint
    - Removes periods, commas, apostrophes
    - Removes parenthetical notes
    - Collapses multiple spaces

    Args:
        name (str): Original high school name

    Returns:
        str: Normalized name for matching (uppercase, no suffix, etc.)

    Examples:
        >>> normalize_hs_name("Central High School")
        'CENTRAL'
        >>> normalize_hs_name("St. Mary's H.S.")
        'SAINT MARYS'
        >>> normalize_hs_name("Lincoln HS (North)")
        'LINCOLN'
    """
    if pd.isna(name) or name == '':
        return ''

    # Convert to string and uppercase
    normalized = str(name).upper().strip()

    # Remove common high school suffixes
    # Order matters - remove longer patterns first
    suffixes = [
        r'\s+HIGH\s+SCHOOL$',
        r'\s+H\.S\.$',
        r'\s+HS$',
        r'\s+H\.S$'
    ]

    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized, flags=re.IGNORECASE)

    # Standardize St./Saint
    normalized = re.sub(r'\bST\.?\s+', 'SAINT ', normalized)

    # Remove periods, commas, apostrophes
    normalized = re.sub(r'[.,\']', '', normalized)

    # Remove parenthetical notes (but save them separately for context)
    # Examples: "Tappan Zee (Saint Rose)" -> "Tappan Zee"
    normalized = re.sub(r'\s*\([^)]+\)$', '', normalized)

    # Collapse multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized


def extract_disambiguator(name):
    """
    Extract any disambiguating information from parentheses.

    This is useful for schools that include additional context in their name,
    such as "Central High School (Phoenix)" or "Lincoln HS (East)".

    Args:
        name (str): Original high school name

    Returns:
        str: Content from parentheses, or empty string if none

    Examples:
        >>> extract_disambiguator("Central High School (Phoenix)")
        'Phoenix'
        >>> extract_disambiguator("Lincoln HS")
        ''
    """
    if pd.isna(name):
        return ''

    match = re.search(r'\(([^)]+)\)$', str(name))
    return match.group(1) if match else ''


def categorize_school_type(name):
    """
    Categorize school type based on name patterns.

    Uses heuristics to identify whether a school is likely:
    - public: Traditional public high schools
    - private: Religious or independent schools
    - prep: Preparatory schools and academies
    - international: Schools outside the US
    - unknown: Unable to determine

    Args:
        name (str): High school name

    Returns:
        str: One of 'public', 'private', 'prep', 'international', or 'unknown'

    Examples:
        >>> categorize_school_type("Central High School")
        'public'
        >>> categorize_school_type("St. Mary's Catholic School")
        'private'
        >>> categorize_school_type("IMG Academy")
        'prep'
    """
    if pd.isna(name):
        return 'unknown'

    name_upper = str(name).upper()

    # Prep schools and academies
    if any(pattern in name_upper for pattern in ['ACADEMY', 'PREP', 'PREPARATORY']):
        return 'prep'

    # Private school indicators
    if any(pattern in name_upper for pattern in [
        'SAINT ', 'ST. ', 'BISHOP ', 'CATHOLIC', 'CHRISTIAN',
        'LUTHERAN', 'METHODIST', 'BAPTIST', 'EPISCOPAL'
    ]):
        return 'private'

    # International patterns
    if any(pattern in name_upper for pattern in [
        'IES ', 'INSTITUT', 'LYCEE', 'GYMNASIUM', 'SECONDARY SCHOOL',
        'COLLEGE '  # In international context, college often means high school
    ]):
        return 'international'

    # Common public school patterns
    if any(pattern in name_upper for pattern in [
        ' HS', 'HIGH SCHOOL', 'H.S.', 'CENTRAL', 'EAST ', 'WEST ',
        'NORTH ', 'SOUTH '
    ]):
        return 'public'

    return 'unknown'


def is_likely_common_name(normalized_name):
    """
    Check if a normalized name is likely to be ambiguous (many schools share it).

    Common school names like "Central", "Liberty", or "Lincoln" appear in many states
    and cities, making them difficult to match without additional context.

    Args:
        normalized_name (str): Normalized school name (from normalize_hs_name)

    Returns:
        bool: True if the name is commonly shared by many schools

    Examples:
        >>> is_likely_common_name("CENTRAL")
        True
        >>> is_likely_common_name("IMG ACADEMY")
        False
    """
    common_names = {
        'CENTRAL', 'LIBERTY', 'LINCOLN', 'WASHINGTON', 'JEFFERSON',
        'ROOSEVELT', 'FRANKLIN', 'MADISON', 'KENNEDY', 'WILSON',
        'EAST', 'WEST', 'NORTH', 'SOUTH', 'NORTHEAST', 'NORTHWEST',
        'SOUTHEAST', 'SOUTHWEST', 'CENTENNIAL', 'HIGHLAND', 'RIVERSIDE'
    }

    return normalized_name in common_names


def is_international_school(name, country=None):
    """
    Determine if a school is likely international (non-US).

    Args:
        name (str): School name
        country (str, optional): Country code or name if available

    Returns:
        bool: True if school is likely international

    Examples:
        >>> is_international_school("London Central School")
        True
        >>> is_international_school("Any School", country="Canada")
        True
        >>> is_international_school("Central High School", country="USA")
        False
    """
    if country and country != 'USA' and country != 'United States':
        return True

    return categorize_school_type(name) == 'international'


def standardize_suffix(name, preferred_suffix="H.S."):
    """
    Standardize the high school suffix to a preferred format.

    This is useful for creating consistent display names after matching.
    By default, uses "H.S." to avoid confusion with similarly-named colleges.

    Args:
        name (str): Original high school name
        preferred_suffix (str): Desired suffix (default: "H.S.")

    Returns:
        str: Name with standardized suffix

    Examples:
        >>> standardize_suffix("Central HS")
        'Central H.S.'
        >>> standardize_suffix("Lincoln High School")
        'Lincoln H.S.'
        >>> standardize_suffix("Lincoln H.S.", preferred_suffix="High School")
        'Lincoln High School'
    """
    if pd.isna(name) or name == '':
        return name

    # Get the base name (normalized)
    base = normalize_hs_name(name)

    # Check if original had a suffix
    name_upper = str(name).upper()
    had_suffix = any(suffix in name_upper for suffix in ['HIGH SCHOOL', 'HS', 'H.S.'])

    if had_suffix and base:
        # Title case the base name
        base_title = base.title()
        return f"{base_title} {preferred_suffix}"

    # Return original if no suffix detected
    return name
