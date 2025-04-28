import google.generativeai as genai
import time
from utils import read_recent_excel_data, load_prompt_template
import pandas as pd
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import re
import argparse

# --- Configuration and Setup Functions ---
def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate traffic reports using Gemini API.")
    parser.add_argument(
        "--model_name", 
        type=str, 
        default='gemini-2.5-flash-preview-04-17',
        help="Name of the Gemini model to use."
    )
    parser.add_argument(
        "--template_path", 
        type=str, 
        default="./prompt-engineering/prompt-templates/v1.txt", 
        help="Path to the prompt template file."
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="./data/Podatki - PrometnoPorocilo_2022_2023_2024.xlsx",
        help="Path to the Excel data file."
    )
    parser.add_argument(
        "--date_filter",
        type=str,
        default="2022-01-01 00:30:00",
        help="Date filter for reading recent Excel data."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./prompt-engineering/reports/",
        help="Directory to save the generated report."
    )
    return parser.parse_args()

def load_api_key():
    """Loads the Gemini API key from .env file."""
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return api_key

def load_data(file_path, date_filter):
    """Loads and preprocesses data from the Excel file."""
    df_data = read_recent_excel_data(file_path, date_filter)

    # Configure pandas display options (optional, can be removed if not needed globally)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    columns_to_keep = ['TitlePomembnoSLO', 'ContentPomembnoSLO', 'TitleNesreceSLO',
                       'ContentNesreceSLO', 'TitleZastojiSLO', 'ContentZastojiSLO',
                       'TitleVremeSLO', 'ContentVremeSLO', 'TitleOvireSLO',
                       'ContentOvireSLO', 'TitleDeloNaCestiSLO', 'ContentDeloNaCestiSLO',
                       'TitleOpozorilaSLO', 'ContentOpozorilaSLO',
                       'TitleMednarodneInformacijeSLO', 'ContentMednarodneInformacijeSLO',
                       'TitleSplosnoSLO', 'ContentSplosnoSLO']
    
    # Ensure only existing columns are selected
    existing_columns = [col for col in columns_to_keep if col in df_data.columns]
    data_str = df_data[existing_columns].fillna('').to_string(index=False)

    # Use BeautifulSoup to convert HTML to plain text and clean whitespace
    soup = BeautifulSoup(data_str, 'html.parser')
    cleaned_data = soup.get_text()
    cleaned_data = re.sub(r'\s+', ' ', cleaned_data).strip()
    return cleaned_data

# --- Core Logic Function ---
def generate_and_save_report(model, system_prompt, model_name, template_path, output_dir, date_filter):
    """Generates the report using the model and saves it to a file."""
    print("Generating report...")
    start_time = time.time()

    try:
        # Generate content using Gemini
        response = model.generate_content(system_prompt)
        end_time = time.time()

        print("\nModel's response:\n", response.text)
        print(f"\nResponse generated in: {end_time - start_time:.2f} seconds")

        # --- Save response to file ---
        # Extract the base name of the template file without extension
        prompt_template_basename = os.path.splitext(os.path.basename(template_path))[0]
        # Format the date_filter for use in a filename
        formatted_date_filter = date_filter.replace(' ', '_').replace(':', '-')
        # Construct the output filename including model name, template base name, and formatted date filter
        output_filename = f"{model_name}-{prompt_template_basename}-{formatted_date_filter}.txt"
        output_filepath = os.path.join(output_dir, output_filename)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Write the response text to the file
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"\nResponse saved to: {output_filepath}")

    except Exception as e:
        print(f"\nError during report generation or saving: {e}")

# --- Main Execution ---
def main():
    """Main function to orchestrate the report generation."""
    # 1. Parse Arguments
    args = parse_arguments()
    model_name = args.model_name
    prompt_template_path = args.template_path
    data_path = args.data_path
    date_filter = args.date_filter
    output_dir = args.output_dir

    print(f"Using Model: {model_name}")
    print(f"Using Prompt Template: {prompt_template_path}")
    print(f"Using Data File: {data_path}")

    # 2. Load Configuration and Initialize Model
    api_key = load_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    # 3. Load Prompt Template
    custom_instructions = load_prompt_template(prompt_template_path)

    # 4. Load and Prepare Data
    traffic_data = load_data(data_path, date_filter)

    # 5. Construct System Prompt
    system_prompt = f"{custom_instructions}\n\nTrenutni podatki o prometu:\n{traffic_data}"
    # print("\n--- System Prompt ---") # Uncomment to print the full prompt
    # print(system_prompt)
    # print("--- End System Prompt ---\n")

    # 6. Generate and Save Report
    generate_and_save_report(model, system_prompt, model_name, prompt_template_path, output_dir, date_filter) # Pass date_filter here

if __name__ == "__main__":
    main()
