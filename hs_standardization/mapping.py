"""
High School Mapping and Standardization

This module provides functions for building standardization mappings from
duplicate high school names and selecting canonical names.

Extracted from the womens-college-basketball project.
"""

import pandas as pd
from .normalize import normalize_hs_name


def select_canonical_name(group_df):
    """
    Given a group of duplicate high school names, select the canonical one.

    Strategy (in order of preference):
    1. Most common version (highest player_count)
    2. If tie, prefer "High School" over "HS" or "H.S."
    3. If still tie, prefer version without periods
    4. If still tie, take first alphabetically

    Args:
        group_df (pd.DataFrame): DataFrame with columns including:
            - high_school_original: Original school name
            - player_count: Number of occurrences/players

    Returns:
        pd.Series: The row representing the canonical name

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'high_school_original': ['Central HS', 'Central High School', 'Central H.S.'],
        ...     'player_count': [10, 15, 5]
        ... })
        >>> canonical = select_canonical_name(df)
        >>> canonical['high_school_original']
        'Central High School'
    """
    # Start with most common
    group_df = group_df.sort_values('player_count', ascending=False)

    max_count = group_df.iloc[0]['player_count']
    top_candidates = group_df[group_df['player_count'] == max_count].copy()

    if len(top_candidates) == 1:
        return top_candidates.iloc[0]

    # Prefer "High School" suffix
    def score_name(name):
        score = 0
        if 'High School' in str(name):
            score += 100
        elif ' HS' in str(name) and 'H.S.' not in str(name):
            score += 50
        # Deduct points for periods
        score -= str(name).count('.') * 10
        return score

    top_candidates['name_score'] = top_candidates['high_school_original'].apply(score_name)
    top_candidates = top_candidates.sort_values(['name_score', 'high_school_original'],
                                                  ascending=[False, True])

    return top_candidates.iloc[0]


def create_duplicate_mapping(schools_df, group_by_state=True):
    """
    Create mapping from duplicate variations to canonical names.

    This function identifies schools that have the same normalized name
    (potentially the same school with different formatting) and creates
    a mapping to a single canonical version.

    Args:
        schools_df (pd.DataFrame): DataFrame with columns:
            - high_school_original: Original school names
            - high_school_normalized: Normalized names (from normalize_hs_name)
            - state: State code (if group_by_state=True)
            - player_count: Number of occurrences
        group_by_state (bool): Whether to group by state when finding duplicates
            (default: True, recommended for US schools)

    Returns:
        pd.DataFrame: Mapping with columns:
            - high_school_original: Original name
            - high_school_standardized: Canonical name to use
            - state: State code
            - confidence: Confidence level ('high_auto')
            - source: Source of mapping ('duplicate_resolution')
            - player_count: Count for this variant
            - canonical_player_count: Count for canonical variant

    Examples:
        >>> import pandas as pd
        >>> from hs_standardization.normalize import normalize_hs_name
        >>> df = pd.DataFrame({
        ...     'high_school_original': ['Central HS', 'Central High School'],
        ...     'state': ['CA', 'CA'],
        ...     'player_count': [10, 15]
        ... })
        >>> df['high_school_normalized'] = df['high_school_original'].apply(normalize_hs_name)
        >>> mapping = create_duplicate_mapping(df)
        >>> len(mapping)
        2
    """
    # Determine grouping columns
    group_cols = ['high_school_normalized']
    if group_by_state and 'state' in schools_df.columns:
        group_cols.append('state')

    mappings = []

    for group_key, group in schools_df.groupby(group_cols):
        if len(group) == 1:
            # Not a duplicate, but still add to mapping for completeness
            row = group.iloc[0]
            mappings.append({
                'high_school_original': row['high_school_original'],
                'high_school_standardized': row['high_school_original'],
                'state': row.get('state', ''),
                'confidence': 'high_auto',
                'source': 'no_variation',
                'player_count': row.get('player_count', 1),
                'canonical_player_count': row.get('player_count', 1)
            })
            continue

        # Select canonical name for duplicates
        canonical = select_canonical_name(group)

        # Create mappings for all variations
        state = group_key[1] if isinstance(group_key, tuple) and len(group_key) > 1 else ''

        for _, row in group.iterrows():
            mappings.append({
                'high_school_original': row['high_school_original'],
                'high_school_standardized': canonical['high_school_original'],
                'state': state if state else row.get('state', ''),
                'confidence': 'high_auto',
                'source': 'duplicate_resolution',
                'player_count': row.get('player_count', 1),
                'canonical_player_count': canonical.get('player_count', 1)
            })

    mapping_df = pd.DataFrame(mappings)
    return mapping_df


def create_prep_school_mapping():
    """
    Create manually curated mapping for well-known prep schools and basketball academies.

    These schools often won't be in public school databases (like NCES) and need
    manual curation. This includes variations of the same school name.

    Returns:
        pd.DataFrame: Mapping with columns:
            - high_school_original: Original/variant name
            - high_school_standardized: Canonical name
            - state: State code
            - city: City name
            - confidence: 'high_manual'
            - source: 'prep_school_curated'
            - notes: Additional information

    Examples:
        >>> mapping = create_prep_school_mapping()
        >>> img = mapping[mapping['high_school_standardized'] == 'IMG Academy']
        >>> len(img)
        1
    """
    # Well-known basketball prep schools and academies
    prep_schools = [
        {'original': 'IMG Academy', 'standardized': 'IMG Academy', 'city': 'Bradenton', 'state': 'FL'},
        {'original': 'Montverde Academy', 'standardized': 'Montverde Academy', 'city': 'Montverde', 'state': 'FL'},
        {'original': 'Oak Hill Academy', 'standardized': 'Oak Hill Academy', 'city': 'Mouth of Wilson', 'state': 'VA'},
        {'original': 'Brewster Academy', 'standardized': 'Brewster Academy', 'city': 'Wolfeboro', 'state': 'NH'},
        {'original': 'Prolific Prep', 'standardized': 'Prolific Prep', 'city': 'Napa', 'state': 'CA'},
        {'original': 'Spire Academy', 'standardized': 'Spire Institute', 'city': 'Geneva', 'state': 'OH'},
        {'original': 'Spire Institute', 'standardized': 'Spire Institute', 'city': 'Geneva', 'state': 'OH'},
        {'original': 'Link Academy', 'standardized': 'Link Academy', 'city': 'Branson', 'state': 'MO'},
        {'original': 'La Lumiere School', 'standardized': 'La Lumiere School', 'city': 'La Porte', 'state': 'IN'},
        {'original': 'New Hope Academy', 'standardized': 'New Hope Christian Academy', 'city': 'Landover Hills', 'state': 'MD'},
        {'original': 'New Hope Christian Academy', 'standardized': 'New Hope Christian Academy', 'city': 'Landover Hills', 'state': 'MD'},
        {'original': 'Hamilton Heights Christian Academy', 'standardized': 'Hamilton Heights Christian Academy', 'city': 'Chattanooga', 'state': 'TN'},
        {'original': 'Northfield Mount Hermon', 'standardized': 'Northfield Mount Hermon School', 'city': 'Gill', 'state': 'MA'},
        {'original': 'Northfield Mount Hermon School', 'standardized': 'Northfield Mount Hermon School', 'city': 'Gill', 'state': 'MA'},
        {'original': 'South Kent School', 'standardized': 'South Kent School', 'city': 'South Kent', 'state': 'CT'},
        {'original': 'Wilbraham & Monson Academy', 'standardized': 'Wilbraham & Monson Academy', 'city': 'Wilbraham', 'state': 'MA'},
        {'original': 'Westtown School', 'standardized': 'Westtown School', 'city': 'West Chester', 'state': 'PA'},
        {'original': 'Worcester Academy', 'standardized': 'Worcester Academy', 'city': 'Worcester', 'state': 'MA'},
        {'original': "The Governor's Academy", 'standardized': "The Governor's Academy", 'city': 'Byfield', 'state': 'MA'},
        {'original': 'Governors Academy', 'standardized': "The Governor's Academy", 'city': 'Byfield', 'state': 'MA'},
        {'original': 'Blair Academy', 'standardized': 'Blair Academy', 'city': 'Blairstown', 'state': 'NJ'},
        {'original': 'Putnam Science Academy', 'standardized': 'Putnam Science Academy', 'city': 'Putnam', 'state': 'CT'},
        {'original': "St. Andrew's School", 'standardized': "St. Andrew's School", 'city': 'Barrington', 'state': 'RI'},
        {'original': 'Tabor Academy', 'standardized': 'Tabor Academy', 'city': 'Marion', 'state': 'MA'},
        {'original': 'Choate Rosemary Hall', 'standardized': 'Choate Rosemary Hall', 'city': 'Wallingford', 'state': 'CT'},
    ]

    mapping_records = []
    for school in prep_schools:
        mapping_records.append({
            'high_school_original': school['original'],
            'high_school_standardized': school['standardized'],
            'state': school['state'],
            'city': school.get('city', ''),
            'confidence': 'high_manual',
            'source': 'prep_school_curated',
            'notes': 'Manually curated prep/basketball academy'
        })

    return pd.DataFrame(mapping_records)


def apply_mapping(df, mapping_df, original_col='high_school',
                  standardized_col='high_school_standardized',
                  confidence_col='hs_confidence',
                  changed_col='hs_was_standardized'):
    """
    Apply a standardization mapping to a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with high school names to standardize
        mapping_df (pd.DataFrame): Mapping DataFrame with columns:
            - high_school_original
            - high_school_standardized
            - confidence (optional)
        original_col (str): Column name in df with original high school names
        standardized_col (str): Name for new column with standardized names
        confidence_col (str): Name for new column with confidence levels
        changed_col (str): Name for new column indicating if name changed

    Returns:
        pd.DataFrame: Original DataFrame with new columns added

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'high_school': ['Central HS', 'Lincoln High School']})
        >>> mapping = pd.DataFrame({
        ...     'high_school_original': ['Central HS'],
        ...     'high_school_standardized': ['Central High School'],
        ...     'confidence': ['high_auto']
        ... })
        >>> result = apply_mapping(df, mapping)
        >>> result[standardized_col].tolist()
        ['Central High School', 'Lincoln High School']
    """
    # Create lookup dictionary
    mapping_dict = dict(zip(
        mapping_df['high_school_original'],
        mapping_df['high_school_standardized']
    ))

    confidence_dict = {}
    if 'confidence' in mapping_df.columns:
        confidence_dict = dict(zip(
            mapping_df['high_school_original'],
            mapping_df['confidence']
        ))

    # Apply mapping
    df = df.copy()
    df[standardized_col] = df[original_col].map(mapping_dict).fillna(df[original_col])

    if confidence_dict:
        df[confidence_col] = df[original_col].map(confidence_dict).fillna('unstandardized')

    df[changed_col] = df[original_col] != df[standardized_col]

    return df


def build_complete_mapping(schools_df, include_prep_schools=True, group_by_state=True):
    """
    Build a complete standardization mapping from a schools DataFrame.

    This is a convenience function that combines duplicate resolution and
    prep school mapping.

    Args:
        schools_df (pd.DataFrame): DataFrame with unique schools and metadata
        include_prep_schools (bool): Whether to include prep school mappings
        group_by_state (bool): Whether to group by state for duplicate detection

    Returns:
        pd.DataFrame: Complete mapping ready to use

    Examples:
        >>> import pandas as pd
        >>> from hs_standardization.normalize import normalize_hs_name
        >>> df = pd.DataFrame({
        ...     'high_school_original': ['IMG Academy', 'Central HS'],
        ...     'state': ['FL', 'CA'],
        ...     'player_count': [50, 10]
        ... })
        >>> df['high_school_normalized'] = df['high_school_original'].apply(normalize_hs_name)
        >>> mapping = build_complete_mapping(df)
        >>> len(mapping) >= 2
        True
    """
    # Create duplicate mapping
    duplicate_mapping = create_duplicate_mapping(schools_df, group_by_state=group_by_state)

    if include_prep_schools:
        # Add prep school mapping
        prep_mapping = create_prep_school_mapping()

        # Combine mappings
        all_mappings = pd.concat([duplicate_mapping, prep_mapping], ignore_index=True)

        # Remove exact duplicates (keep prep school version if both exist)
        all_mappings = all_mappings.drop_duplicates(
            subset=['high_school_original'],
            keep='last'  # Keep prep school mapping if duplicate
        )
    else:
        all_mappings = duplicate_mapping

    return all_mappings
