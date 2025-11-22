# Sports Roster Data - Utilities

Common utilities for sports roster data processing and standardization.

## Table of Contents
- [Web Scraper Utility](#web-scraper-utility)
- [Height Conversion Utility](#height-conversion-utility)
- [High School Standardization Utility](#high-school-standardization-utility)

## Web Scraper Utility

A utility for extracting article text from web URLs using the newspaper4k library.

### Features

- **Article Text Extraction**: Automatically extract main article text from web pages
- **Metadata Support**: Optionally extract article metadata (title, authors, publish date, top image)
- **Simple API**: Easy-to-use functions for both detailed and simple text extraction
- **Command-line Interface**: Run as a standalone script for quick article extraction
- **Error Handling**: Robust error handling with informative error messages

### Quick Start

```python
from web_scraper import extract_article_text, extract_article_text_simple

# Simple text extraction
text = extract_article_text_simple('https://example.com/article')
if text:
    print(text)

# Extract with metadata
result = extract_article_text('https://example.com/article', include_metadata=True)
print(f"Title: {result['title']}")
print(f"Authors: {', '.join(result['authors'])}")
print(f"Text: {result['text']}")
```

### Usage Examples

#### Example 1: Basic Article Extraction

```python
from web_scraper import extract_article_text_simple

url = "https://example.com/sports-news/player-signs-contract"
article_text = extract_article_text_simple(url)

if article_text:
    print(article_text)
else:
    print("Failed to extract article text")
```

#### Example 2: Extract with Full Metadata

```python
from web_scraper import extract_article_text

url = "https://example.com/sports-news/player-signs-contract"
result = extract_article_text(url, include_metadata=True)

if result['error']:
    print(f"Error: {result['error']}")
else:
    print(f"Title: {result['title']}")
    print(f"Authors: {', '.join(result['authors']) if result['authors'] else 'N/A'}")
    print(f"Published: {result['publish_date']}")
    print(f"Top Image: {result['top_image']}")
    print(f"\nArticle Text:\n{result['text']}")
```

#### Example 3: Command-line Usage

```bash
# Using uv to run the script
uv run python -m web_scraper.scraper https://example.com/article

# With metadata
uv run python -m web_scraper.scraper https://example.com/article --metadata
```

### API Reference

#### `extract_article_text(url, download_timeout=10, include_metadata=False)`

Extract text content from a web article URL.

**Parameters:**
- `url` (str): The URL of the article to scrape
- `download_timeout` (int): Timeout in seconds for downloading the article (default: 10)
- `include_metadata` (bool): If True, include additional metadata (default: False)

**Returns:**
- Dictionary containing:
  - `text`: The extracted article text
  - `url`: The original URL
  - `error`: Error message if extraction failed
  - `title`: Article title (if include_metadata=True)
  - `authors`: List of authors (if include_metadata=True)
  - `publish_date`: Publication date (if include_metadata=True)
  - `top_image`: URL of the top image (if include_metadata=True)

#### `extract_article_text_simple(url)`

Simple wrapper to extract just the text content from a URL.

**Parameters:**
- `url` (str): The URL of the article to scrape

**Returns:**
- str or None: The extracted article text, or None if extraction failed

## Height Conversion Utility

A utility for converting various height formats commonly found in sports roster data to a standardized format (total inches).

### Features

- **Multiple Format Support**: Parse heights in various formats:
  - Hyphen format: "5-10", "6-2"
  - Feet/inches with quotes: "6'2\"", "5'11"
  - Feet/inches with text: "6 ft 2 in", "5 feet 11 inches"
  - Plain numbers (assumes inches): 72, "71"
- **Flexible Output**: Convert inches back to formatted strings in multiple formats
- **Robust Parsing**: Handles whitespace, case-insensitivity, and various punctuation
- **Type Flexibility**: Accepts strings, integers, and floats as input

### Quick Start

```python
from height_utils import height_to_inches, inches_to_height_str

# Convert various formats to inches
height_to_inches("5-10")        # Returns: 70
height_to_inches("6'2\"")       # Returns: 74
height_to_inches("5 ft 11 in")  # Returns: 71
height_to_inches(72)            # Returns: 72

# Convert inches to formatted strings
inches_to_height_str(70)                    # Returns: "5-10"
inches_to_height_str(74, format="quote")    # Returns: "6'2\""
inches_to_height_str(71, format="text")     # Returns: "5 ft 11 in"
```

### Usage Examples

#### Example 1: Converting Roster Data

```python
import pandas as pd
from height_utils import height_to_inches

# Your roster data with various height formats
roster = pd.DataFrame({
    'player': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'height': ['5-10', '6\'2"', '5 ft 11 in', '72']
})

# Convert all heights to inches for analysis
roster['height_inches'] = roster['height'].apply(height_to_inches)

print(roster)
# Output:
#    player        height  height_inches
# 0   Alice          5-10             70
# 1     Bob          6'2"             74
# 2 Charlie  5 ft 11 in             71
# 3   Diana            72             72
```

#### Example 2: Standardizing Height Format

```python
from height_utils import height_to_inches, inches_to_height_str

# Mixed height formats
heights = ["5-10", "6'2\"", "5 ft 11 in", 72, "6-0"]

# Standardize all to hyphen format
standardized = [inches_to_height_str(height_to_inches(h)) for h in heights]

print(standardized)
# Output: ['5-10', '6-2', '5-11', '6-0', '6-0']
```

### Supported Height Formats

The `height_to_inches()` function supports the following input formats:

| Format | Example | Description |
|--------|---------|-------------|
| Hyphen | "5-10", "6-2" | Feet and inches separated by hyphen |
| Quotes | "6'2\"", "5'11" | Feet marked with single quote, inches with double quote (optional) |
| Text (full) | "6 ft 2 in", "5 feet 11 inches" | Spelled out with 'ft'/'feet' and 'in'/'inches' |
| Feet only (quote) | "6'", "5'" | Just feet with quote mark |
| Feet only (text) | "6 ft", "5 feet" | Just feet with text |
| Inches only (text) | "72 in", "71 inches" | Total inches with text |
| Plain number | 72, 71.5, "70" | Assumes total inches |

### API Reference

#### `height_to_inches(height)`

Convert height value to total inches.

- **Parameters**:
  - `height` (str, int, or float): Height value in any supported format
- **Returns**: `int` - Total height in inches, or `None` if format is invalid
- **Examples**:
  ```python
  height_to_inches("5-10")  # 70
  height_to_inches("6'2\"")  # 74
  height_to_inches(72)       # 72
  ```

#### `inches_to_height_str(inches, format="hyphen")`

Convert total inches to formatted height string.

- **Parameters**:
  - `inches` (int or float): Total height in inches
  - `format` (str): Output format - "hyphen" (default), "quote", or "text"
- **Returns**: `str` - Formatted height string, or `None` if inches is invalid
- **Examples**:
  ```python
  inches_to_height_str(70)                    # "5-10"
  inches_to_height_str(74, format="quote")    # "6'2\""
  inches_to_height_str(71, format="text")     # "5 ft 11 in"
  ```

## High School Standardization Utility

A reusable Python package for normalizing and standardizing high school names across datasets. This utility helps clean and standardize high school names that may appear in different formats (e.g., "Central HS", "Central High School", "Central H.S.") into a single canonical form.

### Features

- **Name Normalization**: Convert high school names to a standardized format for matching
- **"H.S." Suffix**: Uses "H.S." suffix by default to avoid confusion with similarly-named colleges
- **NCES Integration**: Match schools to NCES (National Center for Education Statistics) database
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
- `standardize_suffix(name, preferred_suffix="H.S.")`: Standardize the high school suffix (defaults to "H.S.")

#### Mapping Functions

- `build_complete_mapping(schools_df)`: Build a complete standardization mapping
- `create_duplicate_mapping(schools_df)`: Create mapping from duplicate variations
- `create_prep_school_mapping()`: Get built-in prep school mappings
- `select_canonical_name(group_df)`: Select the best canonical name from duplicates
- `apply_mapping(df, mapping_df)`: Apply standardization mapping to a DataFrame

#### NCES Integration Functions

- `print_download_instructions()`: Display instructions for downloading NCES data
- `load_ccd_data()`: Load NCES Common Core of Data (public schools)
- `load_pss_data()`: Load NCES Private School Survey data
- `load_and_prepare_all_nces()`: Load both CCD and PSS data
- `match_to_nces(school_name, state, city)`: Match a single school to NCES database
- `batch_match_to_nces(schools_df)`: Match multiple schools to NCES database
- `get_nces_standardized_name(school_name)`: Get NCES-standardized name with "H.S." suffix
- `create_nces_lookup(nces_df)`: Create a fast lookup dictionary for matching

### NCES Integration

The package now supports matching high schools to the NCES (National Center for Education Statistics) database, which includes ~100,000 public schools (CCD) and private schools (PSS).

#### Setting Up NCES Data

Due to API access limitations, NCES data must be downloaded manually:

```python
from hs_standardization import print_download_instructions

# Print instructions for downloading NCES data files
print_download_instructions()
```

Follow the printed instructions to download:
1. **CCD (Common Core of Data)**: Public schools from https://nces.ed.gov/ccd/files.asp
2. **PSS (Private School Survey)**: Private schools from https://nces.ed.gov/surveys/pss/pssdata.asp

Save the files to `data/nces/` directory as:
- `ccd_directory_YYYY.csv` (e.g., `ccd_directory_2023.csv`)
- `pss_YYYY.csv` (e.g., `pss_2021.csv`)

#### Using NCES Matching

```python
import pandas as pd
from hs_standardization import load_and_prepare_all_nces, batch_match_to_nces

# Load NCES data (only needs to be done once)
nces_data = load_and_prepare_all_nces()
# Output: Loaded 18,000 public schools (CCD)
#         Loaded 2,500 private schools (PSS)
#         Total NCES schools loaded: 20,500

# Your school data
schools = pd.DataFrame({
    'high_school': ['Central High School', 'St. Mary Catholic HS', 'Lincoln HS'],
    'state': ['CA', 'IL', 'NE']
})

# Match to NCES database
matched = batch_match_to_nces(
    schools,
    name_col='high_school',
    state_col='state',
    nces_df=nces_data
)

# View results with NCES information
print(matched[['high_school', 'nces_id', 'nces_matched_name', 'nces_city', 'nces_confidence']])
```

The matched DataFrame will include:
- `nces_id`: Official 12-digit NCES school ID
- `nces_matched_name`: Official name from NCES database
- `nces_street`, `nces_city`, `nces_state`, `nces_zip`: School address
- `nces_source`: 'ccd' (public) or 'pss' (private)
- `nces_confidence`: 'exact' (single match) or 'ambiguous' (multiple matches)

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
   - Suffix preference (H.S. > High School > HS to avoid college confusion)
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
