import pandas as pd
import re
from datetime import datetime, timedelta

def load_prompt_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
    return prompt_template

def compare_rtf_excel_data(rtf_result: dict, excel_df: pd.DataFrame) -> dict:
    """
    Compares important data between an RTF result dictionary and an Excel DataFrame.

    Args:
        rtf_result (dict): A dictionary containing RTF data with 'date_time' and 'text' keys.
        excel_df (pd.DataFrame): A pandas DataFrame containing Excel data.

    Returns:
        dict: A dictionary containing:
            - 'match' (bool): True if the important data matches, False otherwise.
            - 'match_score' (float): A score between 0 and 1 indicating how well the data matches.
            - 'details' (list): A list of strings with details about the comparison.
    """
    if not rtf_result:
        return {
            'match': False,
            'match_score': 0.0,
            'details': ["Invalid RTF data."]
        }

    # Extract date, time, and text from the RTF file
    rtf_date_time = rtf_result.get('date_time')
    rtf_text = rtf_result.get('text', '')

    if not rtf_date_time:
        return {
            'match': False,
            'match_score': 0.0,
            'details': ["Could not extract date and time from the RTF data."]
        }

    if excel_df.empty:
        return {
            'match': False,
            'match_score': 0.0,
            'details': ["No matching data found in the Excel data."]
        }

    # Initialize comparison results
    details = []
    match_points = 0
    total_points = 3  # Date, time, and content

    # Compare date and time
    date_match = False
    time_match = False

    # Check if the RTF date and time matches any row in the Excel file
    for _, row in excel_df.iterrows():
        excel_date_time = row.get('Datum')
        if excel_date_time:
            # Compare date
            if excel_date_time.date() == rtf_date_time.date():
                date_match = True
                match_points += 1
                details.append(f"Date match: {rtf_date_time.date()} == {excel_date_time.date()}")

            # Compare time (allow for small differences, e.g., within 5 minutes)
            time_diff = abs((excel_date_time - rtf_date_time).total_seconds() / 60)
            if time_diff <= 5:  # Within 5 minutes
                time_match = True
                match_points += 1
                details.append(f"Time match: {rtf_date_time.strftime('%H:%M')} ≈ {excel_date_time.strftime('%H:%M')} (within {time_diff:.1f} minutes)")

    if not date_match:
        details.append(f"Date mismatch: RTF date {rtf_date_time.date()} not found in Excel data.")

    if not time_match:
        details.append(f"Time mismatch: RTF time {rtf_date_time.strftime('%H:%M')} not closely matched in Excel data.")

    # Compare content
    # Extract key information from RTF text (e.g., location names, traffic conditions)
    # This is a simplified approach - in a real-world scenario, you might use NLP techniques
    # to extract and compare more sophisticated features

    # Extract location names and traffic conditions from RTF text
    locations = []
    traffic_conditions = []

    # Common location patterns in traffic reports
    location_patterns = [
        r'(avtocest[a-z]+)',  # highways
        r'(cest[a-z]+)',      # roads
        r'(Ljubljana|Maribor|Celje|Kranj|Koper|Novo mesto|Nova Gorica)',  # major cities
        r'(predorom \w+)',    # tunnels
        r'(most\w* \w+)'      # bridges
    ]

    # Common traffic condition patterns
    condition_patterns = [
        r'(zastoj)',          # traffic jam
        r'(kolona)',          # queue
        r'(zaprta)',          # closed
        r'(oviran promet)',   # hindered traffic
        r'(nesreča)',         # accident
        r'(dela)',            # roadworks
        r'(pokvarjen)'        # broken down
    ]

    # Extract locations
    for pattern in location_patterns:
        matches = re.finditer(pattern, rtf_text, re.IGNORECASE)
        for match in matches:
            locations.append(match.group(0).lower())

    # Extract traffic conditions
    for pattern in condition_patterns:
        matches = re.finditer(pattern, rtf_text, re.IGNORECASE)
        for match in matches:
            traffic_conditions.append(match.group(0).lower())

    # Check if any of the extracted information is present in the Excel data
    content_match_score = 0
    content_matches = []

    # Convert Excel data to string for text search
    excel_text = ' '.join(excel_df.astype(str).values.flatten()).lower()

    # Check locations
    for location in locations:
        if location in excel_text:
            content_match_score += 1
            content_matches.append(f"Location '{location}' found in Excel data")

    # Check traffic conditions
    for condition in traffic_conditions:
        if condition in excel_text:
            content_match_score += 1
            content_matches.append(f"Traffic condition '{condition}' found in Excel data")

    # Calculate content match percentage
    total_items = len(locations) + len(traffic_conditions)
    if total_items > 0:
        content_match_percentage = content_match_score / total_items
        if content_match_percentage >= 0.5:  # At least 50% of items match
            match_points += 1
            details.append(f"Content match: {content_match_percentage:.0%} of key items found in Excel data")
            details.extend(content_matches)
        else:
            details.append(f"Content mismatch: Only {content_match_percentage:.0%} of key items found in Excel data")
    else:
        details.append("No key content items extracted from RTF text for comparison")

    # Calculate overall match score
    match_score = match_points / total_points if total_points > 0 else 0

    # Determine if it's a match (threshold: 2 out of 3 points, or about 67%)
    is_match = match_score >= 0.67

    return {
        'match': is_match,
        'match_score': match_score,
        'details': details
    }

def read_recent_excel_data(file_path: str, current_time_str: str, sheet_name=0) -> pd.DataFrame:
    """
    Reads data from an Excel file for the last 30 minutes based on the 'Datum' column.

    Args:
        file_path (str): The path to the Excel file (.xlsx).
        current_time_str (str): The current time as a string ('yyyy-mm-dd H:M:S').
        sheet_name (int or str, optional): The sheet name or index. Defaults to 0 (first sheet).

    Returns:
        pandas.DataFrame: A DataFrame containing rows from the last 30 minutes.
                          Returns an empty DataFrame if the file or sheet is not found,
                          or if the 'Datum' column doesn't exist or has format issues.
    """
    timestamp_column = 'Datum' # Hardcoded timestamp column name
    try:
        current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M:%S')
        start_time = current_time - timedelta(minutes=30)
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        if timestamp_column not in df.columns:
            print(f"Error: Timestamp column '{timestamp_column}' not found in the file.")
            return pd.DataFrame() # Return empty DataFrame

        df[timestamp_column] = pd.to_datetime(df[timestamp_column], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        if df[timestamp_column].isnull().all():
             print(f"Warning: Initial date parsing failed for '{timestamp_column}'. Trying format 'mm-dd-yyyy H:M:S'.")
             original_timestamps = pd.read_excel(file_path, sheet_name=sheet_name, usecols=[timestamp_column]).squeeze("columns")
             df[timestamp_column] = pd.to_datetime(original_timestamps, format='%m-%d-%Y %H:%M:%S', errors='coerce')

        df = df.dropna(subset=[timestamp_column])

        if df.empty:
            print(f"Error: Could not parse dates in column '{timestamp_column}' with supported formats.")
            return pd.DataFrame()

        filtered_df = df[(df[timestamp_column] >= start_time) & (df[timestamp_column] <= current_time)]

        return filtered_df

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()
    except ValueError as ve:
        print(f"Error parsing time string: {ve}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()

def read_rtf_file(file_path: str) -> dict:
    """
    Reads an RTF file and extracts date and time information.

    Args:
        file_path (str): The path to the RTF file.

    Returns:
        dict: A dictionary containing 'date_time' (datetime object) and 'text' (full text content).
              Returns empty dict if file not found or parsing fails.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        # Extract plain text from RTF
        # This is a simple approach that works for basic RTF files
        # For more complex RTF files, consider using a dedicated RTF parser library

        # Remove RTF control sequences and formatting
        text = content

        # Remove RTF header and control words
        text = re.sub(r'^\{\\rtf1.*?\\viewkind4\\uc1\\pard', '', text, flags=re.DOTALL)

        # Remove control sequences
        text = re.sub(r'\\[a-z0-9]+', ' ', text)  # Remove control words
        text = re.sub(r'\\\'[0-9a-f]{2}', '', text)  # Remove special character codes
        text = re.sub(r'\\\n', ' ', text)  # Remove line breaks with backslash
        text = re.sub(r'\\[{}]', '', text)  # Remove escaped braces
        text = re.sub(r'[{}]', '', text)  # Remove braces
        text = re.sub(r'\\par\s*', '\n', text)  # Replace paragraph breaks with newlines

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        # Extract date and time using regex
        # Pattern matches formats like "30. 9. 2024" and "17.30"
        date_pattern = r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})'
        time_pattern = r'(\d{1,2})\.(\d{2})'

        date_match = re.search(date_pattern, text)
        time_match = re.search(time_pattern, text)

        if date_match and time_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            year = int(date_match.group(3))

            hour = int(time_match.group(1))
            minute = int(time_match.group(2))

            date_time = datetime(year, month, day, hour, minute)

            return {
                'date_time': date_time,
                'text': text
            }
        else:
            print(f"Warning: Could not extract date and time from {file_path}")
            return {
                'date_time': None,
                'text': text
            }

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}
