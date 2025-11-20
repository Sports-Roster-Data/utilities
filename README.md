# Sports Roster Data - Utilities

Common utilities for sports roster data processing and standardization.

## High School Standardization Utility

A reusable Python package for normalizing and standardizing high school names across datasets. This utility helps clean and standardize high school names that may appear in different formats (e.g., "Central HS", "Central High School", "Central H.S.") into a single canonical form.

### Features

- **Name Normalization**: Convert high school names to a standardized format for matching
- **Duplicate Resolution**: Identify and merge duplicate school names with different formatting
- **School Type Categorization**: Automatically categorize schools as public, private, prep, or international
- **Canonical Name Selection**: Smart selection of the best canonical name from multiple variants
- **Prep School Mapping**: Built-in mappings for well-known basketball prep schools and academies
- **Easy Integration**: Simple API for applying standardization to pandas DataFrames

### Installation

#### From Source

```bash
git clone https://github.com/Sports-Roster-Data/utilities.git
cd utilities
pip install -e .
```

#### Direct Installation

```bash
pip install git+https://github.com/Sports-Roster-Data/utilities.git
```

### Quick Start

```python
import pandas as pd
from hs_standardization import normalize_hs_name, build_complete_mapping, apply_mapping

# Normalize a single high school name
normalized = normalize_hs_name("Central High School")
print(normalized)  # Output: 'CENTRAL'

# Build a standardization mapping from your data
schools_df = pd.DataFrame({
    'high_school_original': ['Central HS', 'Central High School', 'Central H.S.', 'IMG Academy'],
    'state': ['CA', 'CA', 'CA', 'FL'],
    'player_count': [10, 25, 5, 50]
})

# Add normalized names
schools_df['high_school_normalized'] = schools_df['high_school_original'].apply(normalize_hs_name)

# Build mapping
mapping = build_complete_mapping(schools_df)

# Apply to your dataset
roster_df = pd.DataFrame({
    'player': ['Alice', 'Bob', 'Charlie'],
    'high_school': ['Central HS', 'IMG Academy', 'Lincoln High School']
})

roster_df = apply_mapping(roster_df, mapping)
print(roster_df)
```

### Core Functions

#### Normalization Functions

- `normalize_hs_name(name)`: Normalize a high school name for matching
- `categorize_school_type(name)`: Categorize school as public, private, prep, or international
- `is_likely_common_name(normalized_name)`: Check if name is ambiguous (e.g., "Central")
- `extract_disambiguator(name)`: Extract parenthetical information from name
- `standardize_suffix(name, preferred_suffix)`: Standardize the high school suffix

#### Mapping Functions

- `build_complete_mapping(schools_df)`: Build a complete standardization mapping
- `create_duplicate_mapping(schools_df)`: Create mapping from duplicate variations
- `create_prep_school_mapping()`: Get built-in prep school mappings
- `select_canonical_name(group_df)`: Select the best canonical name from duplicates
- `apply_mapping(df, mapping_df)`: Apply standardization mapping to a DataFrame

### Usage Examples

#### Example 1: Basic Normalization

```python
from hs_standardization import normalize_hs_name

names = [
    "Central High School",
    "Central HS",
    "St. Mary's H.S.",
    "Lincoln High School (North)"
]

for name in names:
    print(f"{name} -> {normalize_hs_name(name)}")

# Output:
# Central High School -> CENTRAL
# Central HS -> CENTRAL
# St. Mary's H.S. -> SAINT MARYS
# Lincoln High School (North) -> LINCOLN
```

#### Example 2: Building and Applying a Mapping

```python
import pandas as pd
from hs_standardization import normalize_hs_name, build_complete_mapping, apply_mapping

# Your data with duplicate high school names
schools = pd.DataFrame({
    'high_school_original': [
        'Central HS',
        'Central High School',
        'Central H.S.',
        'Lincoln High School',
        'IMG Academy'
    ],
    'state': ['CA', 'CA', 'CA', 'IL', 'FL'],
    'player_count': [10, 25, 5, 15, 50]
})

# Add normalized column
schools['high_school_normalized'] = schools['high_school_original'].apply(normalize_hs_name)

# Build mapping (automatically selects "Central High School" as canonical)
mapping = build_complete_mapping(schools)

# Apply to your roster data
roster = pd.DataFrame({
    'player_name': ['Alice Smith', 'Bob Jones'],
    'high_school': ['Central HS', 'IMG Academy']
})

roster = apply_mapping(roster, mapping)
print(roster[['player_name', 'high_school', 'high_school_standardized']])
```

#### Example 3: School Type Categorization

```python
from hs_standardization import categorize_school_type

schools = [
    "Central High School",           # public
    "St. Mary's Catholic School",    # private
    "IMG Academy",                   # prep
    "Archbishop Mitty High School",  # private
]

for school in schools:
    school_type = categorize_school_type(school)
    print(f"{school}: {school_type}")
```

### How It Works

1. **Normalization**: Names are normalized by:
   - Converting to uppercase
   - Removing suffixes (High School, HS, H.S.)
   - Standardizing St./Saint
   - Removing punctuation
   - Collapsing whitespace

2. **Duplicate Detection**: Schools with the same normalized name (within the same state) are identified as potential duplicates

3. **Canonical Selection**: The canonical name is selected based on:
   - Frequency (most common variant)
   - Suffix preference (High School > HS > H.S.)
   - Fewer special characters
   - Alphabetical order (as tiebreaker)

4. **Mapping Application**: The mapping is applied to your dataset, adding:
   - `high_school_standardized`: The canonical name
   - `hs_confidence`: Confidence level of the mapping
   - `hs_was_standardized`: Boolean flag if the name changed

### Confidence Levels

- `high_auto`: Automatically resolved duplicates (same school, different formatting)
- `high_manual`: Manually curated (prep schools, well-known programs)
- `unstandardized`: No mapping available

### Extending the Utility

You can add custom mappings to handle special cases:

```python
import pandas as pd
from hs_standardization import create_prep_school_mapping, create_duplicate_mapping

# Get existing prep school mappings
prep_mapping = create_prep_school_mapping()

# Add your custom mappings
custom_mapping = pd.DataFrame({
    'high_school_original': ['My Local HS Variant'],
    'high_school_standardized': ['My Local High School'],
    'state': ['CA'],
    'confidence': ['high_manual'],
    'source': ['custom'],
})

# Combine mappings
complete_mapping = pd.concat([prep_mapping, custom_mapping], ignore_index=True)
```

### Contributing

This utility was originally developed as part of the [womens-college-basketball](https://github.com/Sports-Roster-Data/womens-college-basketball) project and extracted for reuse across other Sports Roster Data projects.

Contributions are welcome! Please feel free to submit issues or pull requests.

### License

MIT License - See LICENSE file for details

### Credits

Originally developed for the Sports Roster Data womens-college-basketball project.
