"""
Script to compare data between RTF and Excel files.

This script demonstrates how to use the compare_rtf_excel_data function
to check if important data is the same in both RTF and Excel files.
"""

from utils import read_rtf_file, read_recent_excel_data
from datetime import datetime

def main():
    # Example usage of the compare_rtf_excel_data function
    rtf_file_path = "../data/RTVSlo/Podatki - rtvslo.si/Promet 2024/September 2024/TMP9-2024-2.rtf"
    excel_file_path = "../data/Podatki - PrometnoPorocilo_2022_2023_2024.xlsx"
    
    # Get the current date and time from the RTF file
    rtf_result = read_rtf_file(rtf_file_path)
    if not rtf_result or not rtf_result['date_time']:
        print(f"Error: Could not extract date and time from {rtf_file_path}")
        return
    
    rtf_date_time = rtf_result['date_time']
    current_time_str = rtf_date_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"RTF file: {rtf_file_path}")
    print(f"Date and time: {current_time_str}")
    
    # Compare the RTF and Excel data
    from utils import compare_rtf_excel_data
    
    result = compare_rtf_excel_data(rtf_file_path, excel_file_path)
    
    if result['match']:
        print("\nThe important data in the RTF and Excel files match!")
        print(f"Match score: {result['match_score']:.2f}")
    else:
        print("\nThe important data in the RTF and Excel files do not match.")
        print(f"Match score: {result['match_score']:.2f}")
    
    if result['details']:
        print("\nComparison details:")
        for detail in result['details']:
            print(f"- {detail}")

if __name__ == "__main__":
    main()