"""
Height Utilities

A utility module for converting and formatting height values in sports roster data.

This package provides functions for:
- Converting various height formats to total inches
- Converting inches back to formatted height strings

Example usage:
    >>> from height_utils import height_to_inches, inches_to_height_str
    >>>
    >>> # Convert various formats to inches
    >>> height_to_inches("5-10")
    70
    >>> height_to_inches("6'2\"")
    74
    >>> height_to_inches("5 ft 11 in")
    71
    >>>
    >>> # Convert inches to formatted string
    >>> inches_to_height_str(70)
    '5-10'
    >>> inches_to_height_str(74, format="quote")
    '6\\'2"'
"""

__version__ = "1.0.0"
__author__ = "Sports Roster Data"
__license__ = "MIT"

from .converter import (
    height_to_inches,
    inches_to_height_str
)

__all__ = [
    'height_to_inches',
    'inches_to_height_str',
]
