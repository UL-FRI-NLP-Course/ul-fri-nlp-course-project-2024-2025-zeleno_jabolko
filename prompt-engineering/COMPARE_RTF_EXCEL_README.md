# RTF and Excel Data Comparison

This module provides functionality to compare important data between RTF (Rich Text Format) files and Excel files.

## Overview

The `compare_rtf_excel_data` function in `utils.py` allows you to:
- Compare date and time information between RTF and Excel files
- Extract and compare key content (locations and traffic conditions) from both sources
- Get a match score and detailed comparison results

## Usage

### Basic Usage

```python
from utils import read_rtf_file, read_recent_excel_data, compare_rtf_excel_data

# Read the RTF file
rtf_file_path = "path/to/your/file.rtf"
rtf_result = read_rtf_file(rtf_file_path)

# Get the date and time from the RTF file
rtf_date_time = rtf_result['date_time']
current_time_str = rtf_date_time.strftime('%Y-%m-%d %H:%M:%S')

# Read the Excel file
excel_file_path = "path/to/your/file.xlsx"
excel_df = read_recent_excel_data(excel_file_path, current_time_str)

# Compare the RTF and Excel data
result = compare_rtf_excel_data(rtf_result, excel_df)

if result['match']:
    print("The important data in the RTF and Excel files match!")
    print(f"Match score: {result['match_score']:.2f}")
else:
    print("The important data in the RTF and Excel files do not match.")
    print(f"Match score: {result['match_score']:.2f}")

# Print detailed comparison results
if result['details']:
    print("\nComparison details:")
    for detail in result['details']:
        print(f"- {detail}")
```

### Advanced Usage

See `compare_rtf_excel.py` for a complete example of how to use the function.

## Implementation Details

The `compare_rtf_excel_data` function compares three key aspects of the data:

1. **Date Comparison**: Checks if the date in the RTF file matches any date in the Excel file.

2. **Time Comparison**: Checks if the time in the RTF file is within 5 minutes of any time in the Excel file.

3. **Content Comparison**: 
   - Extracts locations (highways, cities, tunnels, etc.) from the RTF text
   - Extracts traffic conditions (jams, accidents, roadworks, etc.) from the RTF text
   - Checks if these key items appear in the Excel data

The function calculates a match score based on these three aspects, with each aspect contributing equally to the score. A match score of 0.67 (2 out of 3 points) or higher is considered a match.

## Return Value

The function returns a dictionary with the following keys:

- `match` (bool): True if the important data matches, False otherwise.
- `match_score` (float): A score between 0 and 1 indicating how well the data matches.
- `details` (list): A list of strings with details about the comparison.

## Example

```python
# Read the RTF file
rtf_result = read_rtf_file("traffic_report.rtf")

# Get the date and time from the RTF file
rtf_date_time = rtf_result['date_time']
current_time_str = rtf_date_time.strftime('%Y-%m-%d %H:%M:%S')

# Read the Excel file
excel_df = read_recent_excel_data("traffic_data.xlsx", current_time_str)

# Compare the RTF and Excel data
result = compare_rtf_excel_data(rtf_result, excel_df)

# Sample result
{
    'match': True,
    'match_score': 0.67,
    'details': [
        "Date match: 2024-09-30 == 2024-09-30",
        "Time match: 17:30 ≈ 17:32 (within 2.0 minutes)",
        "Content match: 60% of key items found in Excel data",
        "Location 'avtocesti' found in Excel data",
        "Location 'ljubljana' found in Excel data",
        "Traffic condition 'zastoj' found in Excel data"
    ]
}
```

## Limitations

- The content comparison is based on simple text matching and may not capture semantic similarities.
- The function assumes specific formats for dates and times in both RTF and Excel files.
- The function is designed for traffic information and may need to be adapted for other types of data.
