"""
High School Standardization Utility

A reusable utility for normalizing and standardizing high school names across datasets.

This package provides functions for:
- Normalizing high school names for matching
- Categorizing school types (public, private, prep, international)
- Building standardization mappings
- Applying mappings to datasets

Originally extracted from the Sports-Roster-Data/womens-college-basketball project.

Example usage:
    >>> from hs_standardization import normalize_hs_name, build_complete_mapping
    >>>
    >>> # Normalize a single name
    >>> normalized = normalize_hs_name("Central High School")
    >>> print(normalized)
    'CENTRAL'
    >>>
    >>> # Build a mapping from a DataFrame
    >>> import pandas as pd
    >>> schools = pd.DataFrame({
    ...     'high_school_original': ['Central HS', 'Central High School'],
    ...     'state': ['CA', 'CA'],
    ...     'player_count': [10, 15]
    ... })
    >>> schools['high_school_normalized'] = schools['high_school_original'].apply(normalize_hs_name)
    >>> mapping = build_complete_mapping(schools)
"""

__version__ = "1.0.0"
__author__ = "Sports Roster Data"
__license__ = "MIT"

# Import main functions for easy access
from .normalize import (
    normalize_hs_name,
    extract_disambiguator,
    categorize_school_type,
    is_likely_common_name,
    is_international_school,
    standardize_suffix
)

from .mapping import (
    select_canonical_name,
    create_duplicate_mapping,
    create_prep_school_mapping,
    apply_mapping,
    build_complete_mapping
)

__all__ = [
    # Normalization functions
    'normalize_hs_name',
    'extract_disambiguator',
    'categorize_school_type',
    'is_likely_common_name',
    'is_international_school',
    'standardize_suffix',

    # Mapping functions
    'select_canonical_name',
    'create_duplicate_mapping',
    'create_prep_school_mapping',
    'apply_mapping',
    'build_complete_mapping',
]
