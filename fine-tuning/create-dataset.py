import os
import json
import pandas as pd
from utils import read_rtf_file
from datetime import datetime
import argparse

def load_excel_data(file_path: str) -> pd.DataFrame:
    """Load Excel data once and return the DataFrame."""
    try:
        df = pd.read_excel(file_path, sheet_name=2)  # Using sheet index 2 for 2024 data
        df['Datum'] = pd.to_datetime(df['Datum'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        if df['Datum'].isnull().all():
            print("Warning: Initial date parsing failed. Trying alternative format.")
            original_timestamps = pd.read_excel(file_path, sheet_name=2, usecols=['Datum']).squeeze("columns")
            df['Datum'] = pd.to_datetime(original_timestamps, format='%m-%d-%Y %H:%M:%S', errors='coerce')
        return df.dropna(subset=['Datum'])
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return pd.DataFrame()

def get_recent_excel_data(df: pd.DataFrame, current_time: datetime, minutes=30) -> pd.DataFrame:
    """Get data from the last X minutes from the pre-loaded DataFrame."""
    start_time = current_time - pd.Timedelta(minutes=minutes)
    return df[(df['Datum'] >= start_time) & (df['Datum'] <= current_time)]

def process_rtf_files(base_dir: str, excel_df: pd.DataFrame, output_file: str, max_files: int = None):
    """Process all RTF files in the directory structure and create dataset."""
    dataset = []
    files_processed = 0
    
    # Walk through all subdirectories
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.rtf'):
                if max_files is not None and files_processed >= max_files:
                    print(f"Reached maximum number of files ({max_files}). Stopping processing.")
                    break
                    
                rtf_path = os.path.join(root, file)
                print(f"Processing {rtf_path}")
                files_processed += 1
                
                # Read RTF file
                rtf_data = read_rtf_file(rtf_path)
                if not rtf_data or not rtf_data['date_time']:
                    print(f"Skipping {rtf_path} - could not extract date/time")
                    continue
                
                # Get matching Excel data
                excel_data = get_recent_excel_data(excel_df, rtf_data['date_time'])
                
                # Create text input from A1 and B1 columns
                input_text = ""
                for _, row in excel_data.iterrows():
                    a1 = str(row['A1']) if 'A1' in row and pd.notna(row['A1']) else ""
                    b1 = str(row['B1']) if 'B1' in row and pd.notna(row['B1']) else ""
                    if a1 or b1:  # Only add non-empty values
                        input_text += f"{a1} {b1}\n"
                input_text = input_text.strip()  # Remove trailing newline
                
                # Clean output text by removing everything before first double newline
                output_text = rtf_data['text']
                if '\n\n' in output_text:
                    output_text = output_text.split('\n\n', 1)[1]
                    # Strip leading tabs if they exist
                    output_text = output_text.lstrip('\t')
                
                dataset_entry = {
                    'input': input_text,
                    'output': output_text,
                    'date': rtf_data['date_time'].strftime('%Y-%m-%d %H:%M:%S')
                }
                dataset.append(dataset_entry)
        
        if max_files is not None and files_processed >= max_files:
            break
    
    # Save dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"Created dataset with {len(dataset)} entries")
    print(f"Processed {files_processed} RTF files")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process RTF files and create dataset')
    parser.add_argument('--test', type=int, help='Process only N files for testing')
    args = parser.parse_args()
    
    # Configuration
    base_dir = "data/Podatki - rtvslo.si/Promet 2024"
    excel_file = "data/Podatki - PrometnoPorocilo_2022_2023_2024.xlsx"
    output_file = "fine-tuning/dataset.json"
    
    # Load Excel data once
    print("Loading Excel data...")
    excel_df = load_excel_data(excel_file)
    if excel_df.empty:
        print("Error: Could not load Excel data")
        return
    
    # Process RTF files and create dataset
    print("Processing RTF files...")
    process_rtf_files(base_dir, excel_df, output_file, max_files=args.test)

if __name__ == "__main__":
    main()

