"""
NCES Data Integration

This module provides functions for downloading and working with NCES
(National Center for Education Statistics) data for U.S. schools.

Data Sources:
- NCES Common Core of Data (CCD): Public schools (~100,000 schools)
- NCES Private School Survey (PSS): Private schools

The NCES API via Urban Institute is currently blocked (403 errors),
so this module supports manual download of CSV files from the NCES website.

References:
- CCD: https://nces.ed.gov/ccd/files.asp
- PSS: https://nces.ed.gov/surveys/pss/pssdata.asp
"""

import os
import pandas as pd
import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from .normalize import normalize_hs_name


# Default data directory
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'nces')


def get_data_directory(data_dir: Optional[str] = None) -> Path:
    """
    Get the data directory for NCES files, creating it if needed.

    Args:
        data_dir: Optional custom data directory path

    Returns:
        Path object for the data directory
    """
    if data_dir is None:
        data_dir = DEFAULT_DATA_DIR

    path = Path(data_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_instructions_ccd() -> Dict[str, str]:
    """
    Provide instructions for manually downloading NCES CCD data.

    The Urban Institute API is currently returning 403 errors, so manual
    download is required.

    Returns:
        Dictionary with download instructions and URLs
    """
    return {
        'title': 'NCES Common Core of Data (CCD) - Public Schools',
        'url': 'https://nces.ed.gov/ccd/files.asp',
        'instructions': [
            '1. Visit https://nces.ed.gov/ccd/files.asp',
            '2. Navigate to "Public School Data"',
            '3. Select the most recent year available',
            '4. Download the "Directory" file (usually CSV format)',
            '5. Save as "ccd_directory_YYYY.csv" in the data/nces directory',
            '   where YYYY is the school year (e.g., ccd_directory_2023.csv)'
        ],
        'expected_filename_pattern': 'ccd_directory_*.csv',
        'key_fields': [
            'NCESSCH (12-digit NCES school ID)',
            'SCH_NAME (School name)',
            'LSTREET1, LSTREET2, LSTREET3 (Address)',
            'LCITY (City)',
            'LSTATE (State)',
            'LZIP (ZIP code)',
            'PHONE (Phone number)',
            'LEVEL (School level: 1=Primary, 2=Middle, 3=High, 4=Other)',
            'SCHOOL_TYPE_TEXT (School type description)'
        ]
    }


def download_instructions_pss() -> Dict[str, str]:
    """
    Provide instructions for manually downloading NCES PSS data.

    Returns:
        Dictionary with download instructions and URLs
    """
    return {
        'title': 'NCES Private School Universe Survey (PSS) - Private Schools',
        'url': 'https://nces.ed.gov/surveys/pss/pssdata.asp',
        'instructions': [
            '1. Visit https://nces.ed.gov/surveys/pss/pssdata.asp',
            '2. Select the most recent survey year',
            '3. Download the "Private School Data File" (CSV format)',
            '4. Save as "pss_YYYY.csv" in the data/nces directory',
            '   where YYYY is the survey year (e.g., pss_2021.csv)'
        ],
        'expected_filename_pattern': 'pss_*.csv',
        'key_fields': [
            'PPIN (Private school ID)',
            'PINST (School name)',
            'PADDRS (Address)',
            'PCITY (City)',
            'PSTATE (State)',
            'PZIP (ZIP code)',
            'LEVEL (School level codes)',
            'AFFIL (Religious affiliation code)'
        ]
    }


def print_download_instructions(source: str = 'both'):
    """
    Print download instructions for NCES data files.

    Args:
        source: 'ccd', 'pss', or 'both' (default: 'both')
    """
    if source in ['ccd', 'both']:
        ccd_info = download_instructions_ccd()
        print(f"\n{'='*70}")
        print(f"{ccd_info['title']}")
        print(f"{'='*70}")
        print(f"URL: {ccd_info['url']}\n")
        for instruction in ccd_info['instructions']:
            print(instruction)
        print(f"\nKey fields needed:")
        for field in ccd_info['key_fields']:
            print(f"  - {field}")

    if source in ['pss', 'both']:
        pss_info = download_instructions_pss()
        print(f"\n{'='*70}")
        print(f"{pss_info['title']}")
        print(f"{'='*70}")
        print(f"URL: {pss_info['url']}\n")
        for instruction in pss_info['instructions']:
            print(instruction)
        print(f"\nKey fields needed:")
        for field in pss_info['key_fields']:
            print(f"  - {field}")

    print(f"\n{'='*70}\n")


def find_latest_ccd_file(data_dir: Optional[str] = None) -> Optional[Path]:
    """
    Find the most recent CCD data file in the data directory.

    Args:
        data_dir: Optional custom data directory path

    Returns:
        Path to the most recent CCD file, or None if not found
    """
    dir_path = get_data_directory(data_dir)
    ccd_files = list(dir_path.glob('ccd_directory_*.csv'))

    if not ccd_files:
        return None

    # Sort by filename to get most recent year
    ccd_files.sort(reverse=True)
    return ccd_files[0]


def find_latest_pss_file(data_dir: Optional[str] = None) -> Optional[Path]:
    """
    Find the most recent PSS data file in the data directory.

    Args:
        data_dir: Optional custom data directory path

    Returns:
        Path to the most recent PSS file, or None if not found
    """
    dir_path = get_data_directory(data_dir)
    pss_files = list(dir_path.glob('pss_*.csv'))

    if not pss_files:
        return None

    # Sort by filename to get most recent year
    pss_files.sort(reverse=True)
    return pss_files[0]


def load_ccd_data(file_path: Optional[str] = None,
                  data_dir: Optional[str] = None,
                  high_schools_only: bool = True) -> pd.DataFrame:
    """
    Load NCES Common Core of Data (public schools).

    Args:
        file_path: Path to specific CCD CSV file (if None, finds latest)
        data_dir: Directory containing NCES data files
        high_schools_only: If True, filter to only high schools (LEVEL=3)

    Returns:
        DataFrame with CCD data

    Raises:
        FileNotFoundError: If no CCD file is found
    """
    if file_path is None:
        file_path = find_latest_ccd_file(data_dir)
        if file_path is None:
            raise FileNotFoundError(
                "No CCD data file found. Please download manually.\n"
                "Use print_download_instructions('ccd') for details."
            )

    # Load the CSV file
    # Note: NCES files often have encoding issues, try UTF-8 first, then latin1
    try:
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='latin1', low_memory=False)

    # Standardize column names to uppercase for consistency
    df.columns = df.columns.str.upper()

    # Filter to high schools if requested
    if high_schools_only:
        # LEVEL column: 1=Primary, 2=Middle, 3=High, 4=Other/Alternative
        # Some files may have different column names for level
        level_col = None
        for col in ['LEVEL', 'SCH_LEVEL', 'SCHOOL_LEVEL']:
            if col in df.columns:
                level_col = col
                break

        if level_col:
            # Keep high schools (level 3) and schools with multiple levels including high
            df = df[df[level_col].astype(str).str.contains('3', na=False)]

    return df


def load_pss_data(file_path: Optional[str] = None,
                  data_dir: Optional[str] = None,
                  high_schools_only: bool = True) -> pd.DataFrame:
    """
    Load NCES Private School Survey data.

    Args:
        file_path: Path to specific PSS CSV file (if None, finds latest)
        data_dir: Directory containing NCES data files
        high_schools_only: If True, filter to only high schools

    Returns:
        DataFrame with PSS data

    Raises:
        FileNotFoundError: If no PSS file is found
    """
    if file_path is None:
        file_path = find_latest_pss_file(data_dir)
        if file_path is None:
            raise FileNotFoundError(
                "No PSS data file found. Please download manually.\n"
                "Use print_download_instructions('pss') for details."
            )

    # Load the CSV file
    try:
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='latin1', low_memory=False)

    # Standardize column names to uppercase
    df.columns = df.columns.str.upper()

    # Filter to high schools if requested
    if high_schools_only:
        # PSS LEVEL encoding may vary by year, but typically includes high school codes
        level_col = None
        for col in ['LEVEL', 'LEVEL12', 'LEVEL_CODE']:
            if col in df.columns:
                level_col = col
                break

        if level_col:
            # Keep schools that serve high school grades
            # This typically means having grades 9-12
            df = df[df[level_col].astype(str).str.contains('3|4|HS|HIGH', case=False, na=False)]

    return df


def prepare_nces_for_matching(df: pd.DataFrame, source: str = 'ccd') -> pd.DataFrame:
    """
    Prepare NCES data for matching by standardizing columns and adding normalized names.

    Args:
        df: Raw NCES DataFrame (CCD or PSS)
        source: 'ccd' or 'pss' to indicate data source

    Returns:
        DataFrame with standardized columns and normalized names
    """
    result = df.copy()

    # Identify key columns based on source
    if source == 'ccd':
        name_col = 'SCH_NAME'
        id_col = 'NCESSCH'
        street_cols = ['LSTREET1', 'LSTREET2', 'LSTREET3']
        city_col = 'LCITY'
        state_col = 'LSTATE'
        zip_col = 'LZIP'
    else:  # pss
        name_col = 'PINST'
        id_col = 'PPIN'
        street_cols = ['PADDRS']
        city_col = 'PCITY'
        state_col = 'PSTATE'
        zip_col = 'PZIP'

    # Create standardized columns
    result['nces_id'] = result[id_col] if id_col in result.columns else ''
    result['school_name_original'] = result[name_col] if name_col in result.columns else ''
    result['school_name_normalized'] = result['school_name_original'].apply(normalize_hs_name)

    # Combine street address fields
    street_parts = []
    for col in street_cols:
        if col in result.columns:
            street_parts.append(result[col].fillna(''))
    if street_parts:
        result['street'] = street_parts[0]
        for part in street_parts[1:]:
            result['street'] = result['street'] + ' ' + part
        result['street'] = result['street'].str.strip()
    else:
        result['street'] = ''

    result['city'] = result[city_col] if city_col in result.columns else ''
    result['state'] = result[state_col] if state_col in result.columns else ''
    result['zip'] = result[zip_col] if zip_col in result.columns else ''
    result['source'] = source

    return result


def load_and_prepare_all_nces(data_dir: Optional[str] = None,
                               high_schools_only: bool = True) -> pd.DataFrame:
    """
    Load and combine both CCD (public) and PSS (private) school data.

    Args:
        data_dir: Directory containing NCES data files
        high_schools_only: If True, filter to only high schools

    Returns:
        Combined DataFrame with all NCES schools
    """
    dfs = []

    # Try to load CCD data
    try:
        ccd = load_ccd_data(data_dir=data_dir, high_schools_only=high_schools_only)
        ccd_prepared = prepare_nces_for_matching(ccd, source='ccd')
        dfs.append(ccd_prepared)
        print(f"Loaded {len(ccd_prepared):,} public schools (CCD)")
    except FileNotFoundError as e:
        print(f"Warning: {e}")

    # Try to load PSS data
    try:
        pss = load_pss_data(data_dir=data_dir, high_schools_only=high_schools_only)
        pss_prepared = prepare_nces_for_matching(pss, source='pss')
        dfs.append(pss_prepared)
        print(f"Loaded {len(pss_prepared):,} private schools (PSS)")
    except FileNotFoundError as e:
        print(f"Warning: {e}")

    if not dfs:
        raise FileNotFoundError(
            "No NCES data files found. Please download manually.\n"
            "Use print_download_instructions() for details."
        )

    # Combine all data
    combined = pd.concat(dfs, ignore_index=True)
    print(f"Total NCES schools loaded: {len(combined):,}")

    return combined


def create_nces_lookup(nces_df: pd.DataFrame) -> Dict[str, List[Dict]]:
    """
    Create a lookup dictionary for fast NCES matching.

    Args:
        nces_df: Prepared NCES DataFrame with normalized names

    Returns:
        Dictionary mapping normalized names to list of school records
    """
    lookup = {}

    for _, row in nces_df.iterrows():
        normalized = row['school_name_normalized']
        if pd.notna(normalized) and normalized != '':
            if normalized not in lookup:
                lookup[normalized] = []
            lookup[normalized].append({
                'nces_id': row['nces_id'],
                'name': row['school_name_original'],
                'street': row['street'],
                'city': row['city'],
                'state': row['state'],
                'zip': row['zip'],
                'source': row['source']
            })

    return lookup


def match_to_nces(school_name: str,
                  state: Optional[str] = None,
                  city: Optional[str] = None,
                  nces_lookup: Optional[Dict] = None,
                  nces_df: Optional[pd.DataFrame] = None) -> Optional[Dict]:
    """
    Match a school name to NCES database.

    Args:
        school_name: High school name to match
        state: State code (e.g., 'CA', 'NY') for disambiguation
        city: City name for disambiguation
        nces_lookup: Pre-built NCES lookup dictionary (preferred for batch matching)
        nces_df: NCES DataFrame (will build lookup if nces_lookup not provided)

    Returns:
        Dictionary with match information, or None if no match found
        {
            'nces_id': NCES school ID,
            'matched_name': Official NCES school name,
            'street': Street address,
            'city': City,
            'state': State,
            'zip': ZIP code,
            'source': 'ccd' or 'pss',
            'confidence': 'exact' or 'ambiguous'
        }
    """
    if nces_lookup is None:
        if nces_df is None:
            raise ValueError("Either nces_lookup or nces_df must be provided")
        nces_lookup = create_nces_lookup(nces_df)

    # Normalize the input name
    normalized = normalize_hs_name(school_name)

    if not normalized or normalized not in nces_lookup:
        return None

    candidates = nces_lookup[normalized]

    # If only one match, return it
    if len(candidates) == 1:
        result = candidates[0].copy()
        result['matched_name'] = result.pop('name')
        result['confidence'] = 'exact'
        return result

    # Multiple matches - try to disambiguate by state
    if state:
        state_matches = [c for c in candidates if c['state'].upper() == state.upper()]
        if len(state_matches) == 1:
            result = state_matches[0].copy()
            result['matched_name'] = result.pop('name')
            result['confidence'] = 'exact'
            return result
        elif len(state_matches) > 1:
            candidates = state_matches

    # Try to disambiguate by city if we still have multiple matches
    if city and len(candidates) > 1:
        city_matches = [c for c in candidates
                       if c['city'].upper() == city.upper()]
        if len(city_matches) == 1:
            result = city_matches[0].copy()
            result['matched_name'] = result.pop('name')
            result['confidence'] = 'exact'
            return result
        elif len(city_matches) > 1:
            candidates = city_matches

    # Still ambiguous - return first match but mark as ambiguous
    result = candidates[0].copy()
    result['matched_name'] = result.pop('name')
    result['confidence'] = 'ambiguous'
    result['num_candidates'] = len(candidates)
    return result


def batch_match_to_nces(schools_df: pd.DataFrame,
                        name_col: str = 'high_school',
                        state_col: Optional[str] = 'state',
                        city_col: Optional[str] = 'city',
                        nces_df: Optional[pd.DataFrame] = None,
                        data_dir: Optional[str] = None) -> pd.DataFrame:
    """
    Batch match schools to NCES database.

    Args:
        schools_df: DataFrame with school names to match
        name_col: Column name containing school names
        state_col: Column name containing state codes (optional but recommended)
        city_col: Column name containing city names (optional)
        nces_df: Pre-loaded NCES DataFrame (if None, will load from data_dir)
        data_dir: Directory containing NCES data files

    Returns:
        DataFrame with NCES match information added
    """
    # Load NCES data if not provided
    if nces_df is None:
        nces_df = load_and_prepare_all_nces(data_dir=data_dir)

    # Create lookup for efficient matching
    nces_lookup = create_nces_lookup(nces_df)

    # Prepare result DataFrame
    result = schools_df.copy()

    # Initialize new columns
    result['nces_id'] = None
    result['nces_matched_name'] = None
    result['nces_street'] = None
    result['nces_city'] = None
    result['nces_state'] = None
    result['nces_zip'] = None
    result['nces_source'] = None
    result['nces_confidence'] = None

    # Match each school
    matched_count = 0
    for idx, row in result.iterrows():
        school_name = row[name_col]
        state = row[state_col] if state_col and state_col in result.columns else None
        city = row[city_col] if city_col and city_col in result.columns else None

        match = match_to_nces(school_name, state, city, nces_lookup=nces_lookup)

        if match:
            result.at[idx, 'nces_id'] = match['nces_id']
            result.at[idx, 'nces_matched_name'] = match['matched_name']
            result.at[idx, 'nces_street'] = match['street']
            result.at[idx, 'nces_city'] = match['city']
            result.at[idx, 'nces_state'] = match['state']
            result.at[idx, 'nces_zip'] = match['zip']
            result.at[idx, 'nces_source'] = match['source']
            result.at[idx, 'nces_confidence'] = match['confidence']
            matched_count += 1

    print(f"Matched {matched_count:,} of {len(result):,} schools "
          f"({matched_count/len(result)*100:.1f}%)")

    return result


def get_nces_standardized_name(school_name: str,
                               state: Optional[str] = None,
                               city: Optional[str] = None,
                               nces_lookup: Optional[Dict] = None,
                               nces_df: Optional[pd.DataFrame] = None,
                               add_hs_suffix: bool = True) -> str:
    """
    Get the standardized name for a school based on NCES data.

    Args:
        school_name: High school name to standardize
        state: State code for disambiguation
        city: City name for disambiguation
        nces_lookup: Pre-built NCES lookup dictionary
        nces_df: NCES DataFrame
        add_hs_suffix: If True, add "H.S." suffix to avoid college confusion

    Returns:
        Standardized school name, or original name if no match found
    """
    match = match_to_nces(school_name, state, city, nces_lookup, nces_df)

    if match:
        name = match['matched_name']
        if add_hs_suffix and 'H.S.' not in name and 'High School' not in name:
            # Add H.S. suffix if not already present
            from .normalize import standardize_suffix
            name = standardize_suffix(name)
        return name

    # No match - return original name
    if add_hs_suffix:
        from .normalize import standardize_suffix
        return standardize_suffix(school_name)

    return school_name
