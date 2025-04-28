import pandas as pd
from datetime import datetime, timedelta

def load_prompt_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        prompt_template = file.read()
    return prompt_template
    
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