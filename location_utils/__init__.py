"""
Location utilities for parsing and standardizing city and country names.

This module provides functions for extracting and standardizing country names
from location strings (e.g., "London, England" or "Stockholm, Sweden").
"""

from .parser import parse_city_country, standardize_country_name

__all__ = ['parse_city_country', 'standardize_country_name']
