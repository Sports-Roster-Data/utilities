# NCES Data Directory

This directory is for storing NCES (National Center for Education Statistics) data files.

## Required Data Files

Due to API access limitations, NCES data must be downloaded manually:

### 1. Common Core of Data (CCD) - Public Schools

- **Source**: https://nces.ed.gov/ccd/files.asp
- **File naming**: Save as `ccd_directory_YYYY.csv` (e.g., `ccd_directory_2023.csv`)
- **Contains**: ~100,000 U.S. public schools with canonical names and addresses

**Download Instructions**:
1. Visit https://nces.ed.gov/ccd/files.asp
2. Navigate to "Public School Data"
3. Select the most recent year available
4. Download the "Directory" file (CSV format)
5. Save to this directory as `ccd_directory_YYYY.csv`

### 2. Private School Universe Survey (PSS) - Private Schools

- **Source**: https://nces.ed.gov/surveys/pss/pssdata.asp
- **File naming**: Save as `pss_YYYY.csv` (e.g., `pss_2021.csv`)
- **Contains**: Private schools including religious and independent institutions

**Download Instructions**:
1. Visit https://nces.ed.gov/surveys/pss/pssdata.asp
2. Select the most recent survey year
3. Download the "Private School Data File" (CSV format)
4. Save to this directory as `pss_YYYY.csv`

## Usage

After downloading the data files, you can use them in Python:

```python
from hs_standardization import load_and_prepare_all_nces, batch_match_to_nces
import pandas as pd

# Load NCES data
nces_data = load_and_prepare_all_nces()

# Match your school data to NCES
schools = pd.DataFrame({
    'high_school': ['Central High School', 'Lincoln HS'],
    'state': ['CA', 'IL']
})

matched = batch_match_to_nces(schools, name_col='high_school', nces_df=nces_data)
```

## Notes

- The NCES API via Urban Institute is currently blocked (403 errors)
- Files are ignored by git due to their large size
- Update data files periodically to ensure accuracy
- NCES school IDs are 12-digit unique identifiers
