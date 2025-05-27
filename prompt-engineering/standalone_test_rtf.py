import re
from datetime import datetime

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

# Test the read_rtf_file function with a sample RTF file
file_path = "../data/RTVSlo/Podatki - rtvslo.si/Promet 2024/September 2024/TMP9-2024-2.rtf"
result = read_rtf_file(file_path)

if result:
    if result['date_time']:
        print(f"Date and time extracted: {result['date_time']}")
        print(f"Formatted date: {result['date_time'].strftime('%Y-%m-%d')}")
        print(f"Formatted time: {result['date_time'].strftime('%H:%M')}")
    else:
        print("Date and time could not be extracted.")

    print("\nExtracted text:")
    print(result['text'][:200] + "..." if len(result['text']) > 200 else result['text'])
else:
    print("Failed to read the RTF file.")
