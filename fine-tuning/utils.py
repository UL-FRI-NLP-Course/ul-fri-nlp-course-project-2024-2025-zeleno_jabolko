import re
from datetime import datetime
from striprtf.striprtf import rtf_to_text

def load_prompt_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
    return prompt_template

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

        # Convert RTF to plain text using striprtf
        text = rtf_to_text(content)

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
