"""
Height conversion utilities for sports roster data processing.

This module provides functions for converting various height formats
(e.g., "5-10", "6'2\"", "5'11", "6 ft 2 in") to total inches.
"""

import re
from typing import Union, Optional


def height_to_inches(height: Union[str, int, float]) -> Optional[int]:
    """
    Convert standard height values to total inches.

    Supported formats:
    - Hyphen format: "5-10", "6-2"
    - Feet/inches with quotes: "6'2\"", "5'11\"", "6'2", "5'11"
    - Feet/inches with text: "6 ft 2 in", "5 feet 11 inches"
    - Total inches as number: 72, 71.5
    - Total inches as string: "72", "71"

    Args:
        height: Height value in various formats (string, int, or float)

    Returns:
        Total height in inches as an integer, or None if the format is invalid

    Examples:
        >>> height_to_inches("5-10")
        70
        >>> height_to_inches("6'2\"")
        74
        >>> height_to_inches("6'2")
        74
        >>> height_to_inches("5 ft 11 in")
        71
        >>> height_to_inches(72)
        72
        >>> height_to_inches("invalid")
        None
    """
    if height is None:
        return None

    # If it's already a number, assume it's total inches
    if isinstance(height, (int, float)):
        return int(round(height))

    # Convert to string and strip whitespace
    height_str = str(height).strip()

    if not height_str:
        return None

    # Try to parse as a plain number (total inches)
    try:
        return int(round(float(height_str)))
    except ValueError:
        pass

    # Pattern 1: Hyphen format (e.g., "5-10", "6-2")
    hyphen_match = re.match(r'^(\d+)\s*-\s*(\d+)$', height_str)
    if hyphen_match:
        feet = int(hyphen_match.group(1))
        inches = int(hyphen_match.group(2))
        return feet * 12 + inches

    # Pattern 2: Feet/inches with quotes (e.g., "6'2\"", "5'11", "6'2")
    quote_match = re.match(r'^(\d+)\s*[\'′]\s*(\d+)\s*[\"″]?$', height_str)
    if quote_match:
        feet = int(quote_match.group(1))
        inches = int(quote_match.group(2))
        return feet * 12 + inches

    # Pattern 3: Just feet with quote (e.g., "6'", "5'")
    feet_only_match = re.match(r'^(\d+)\s*[\'′]\s*$', height_str)
    if feet_only_match:
        feet = int(feet_only_match.group(1))
        return feet * 12

    # Pattern 4: Feet/inches with text (e.g., "6 ft 2 in", "5 feet 11 inches")
    text_match = re.match(
        r'^(\d+)\s*(?:ft|feet|foot)\s*(\d+)?\s*(?:in|inches|inch)?$',
        height_str,
        re.IGNORECASE
    )
    if text_match:
        feet = int(text_match.group(1))
        inches = int(text_match.group(2)) if text_match.group(2) else 0
        return feet * 12 + inches

    # Pattern 5: Just feet with text (e.g., "6 ft", "5 feet")
    feet_text_only_match = re.match(
        r'^(\d+)\s*(?:ft|feet|foot)\s*$',
        height_str,
        re.IGNORECASE
    )
    if feet_text_only_match:
        feet = int(feet_text_only_match.group(1))
        return feet * 12

    # Pattern 6: Just inches with text (e.g., "72 in", "71 inches")
    inches_only_match = re.match(
        r'^(\d+)\s*(?:in|inches|inch)\s*$',
        height_str,
        re.IGNORECASE
    )
    if inches_only_match:
        return int(inches_only_match.group(1))

    # If no pattern matched, return None
    return None


def inches_to_height_str(inches: Union[int, float], format: str = "hyphen") -> Optional[str]:
    """
    Convert total inches to a formatted height string.

    Args:
        inches: Total height in inches
        format: Output format - "hyphen" (default), "quote", or "text"

    Returns:
        Formatted height string, or None if inches is invalid

    Examples:
        >>> inches_to_height_str(70)
        '5-10'
        >>> inches_to_height_str(74, format="quote")
        '6\\'2"'
        >>> inches_to_height_str(71, format="text")
        '5 ft 11 in'
    """
    if inches is None or inches < 0:
        return None

    total_inches = int(round(inches))
    feet = total_inches // 12
    remaining_inches = total_inches % 12

    if format == "hyphen":
        return f"{feet}-{remaining_inches}"
    elif format == "quote":
        return f"{feet}'{remaining_inches}\""
    elif format == "text":
        return f"{feet} ft {remaining_inches} in"
    else:
        raise ValueError(f"Invalid format: {format}. Must be 'hyphen', 'quote', or 'text'")
