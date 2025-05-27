"""
Example usage of the read_rtf_file function.

This script demonstrates how to use the read_rtf_file function to extract
date, time, and text content from RTF files.
"""

from utils import read_rtf_file
from datetime import datetime

def main():
    # Example 1: Basic usage - extract date and time from an RTF file
    file_path = "../data/RTVSlo/Podatki - rtvslo.si/Promet 2024/September 2024/TMP9-2024-2.rtf"
    result = read_rtf_file(file_path)
    
    if result and result['date_time']:
        print("Example 1: Basic Usage")
        print(f"Date and time extracted: {result['date_time']}")
        print(f"Formatted date: {result['date_time'].strftime('%Y-%m-%d')}")
        print(f"Formatted time: {result['date_time'].strftime('%H:%M')}")
        print("\nExtracted text preview:")
        print(result['text'][:150] + "..." if len(result['text']) > 150 else result['text'])
        print("\n" + "-"*50 + "\n")
    
    # Example 2: Processing multiple RTF files
    print("Example 2: Processing Multiple Files")
    file_paths = [
        "../data/RTVSlo/Podatki - rtvslo.si/Promet 2024/September 2024/TMP9-2024-1.rtf",
        "../data/RTVSlo/Podatki - rtvslo.si/Promet 2024/September 2024/TMP9-2024-2.rtf",
        "../data/RTVSlo/Podatki - rtvslo.si/Promet 2024/September 2024/TMP9-2024-3.rtf"
    ]
    
    for path in file_paths:
        try:
            result = read_rtf_file(path)
            if result and result['date_time']:
                print(f"File: {path.split('/')[-1]}")
                print(f"Date: {result['date_time'].strftime('%Y-%m-%d')}")
                print(f"Time: {result['date_time'].strftime('%H:%M')}")
                print()
        except Exception as e:
            print(f"Error processing {path}: {e}")
    
    print("-"*50 + "\n")
    
    # Example 3: Filtering files by date
    print("Example 3: Filtering Files by Date")
    target_date = datetime(2024, 9, 30).date()  # September 30, 2024
    
    for path in file_paths:
        try:
            result = read_rtf_file(path)
            if result and result['date_time']:
                file_date = result['date_time'].date()
                
                if file_date == target_date:
                    print(f"File from {file_date}: {path.split('/')[-1]}")
                    print(f"Time: {result['date_time'].strftime('%H:%M')}")
                    print()
        except Exception as e:
            print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    main()