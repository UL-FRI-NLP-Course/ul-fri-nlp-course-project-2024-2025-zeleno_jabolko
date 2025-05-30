from transformers import pipeline
import time
from utils import read_recent_excel_data, load_prompt_template
from gemini_api import load_data
import pandas as pd
import os
from bs4 import BeautifulSoup
import re
import argparse

# --- Configuration and Setup Functions ---
def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate traffic reports using local LLM.")
    parser.add_argument(
        "--model_id", 
        type=str, 
        default='cjvt/GaMS-2B-Instruct',
        help="Model ID for the local LLM to use. Example: [cjvt/GaMS-2B-Instruct, google/gemma-3-12b-it, google/gemma-3-1b-it]"
    )
    parser.add_argument(
        "--template_path", 
        type=str, 
        default="./prompt-engineering/prompt-templates/v6.txt", 
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
        default="2024-07-21 11:00:00",
        help="Date filter for reading recent Excel data."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./prompt-engineering/reports/",
        help="Directory to save the generated report."
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Device to run the model on (cuda, mps, cpu)."
    )
    return parser.parse_args()

def initialize_model(model_id, device):
    """Initializes the local LLM pipeline."""
    print(f"Initializing model: {model_id} on device: {device}")
    try:
        pline = pipeline(
            "text-generation",
            model=model_id,
            device_map=device
        )
        return pline
    except Exception as e:
        print(f"Error initializing model: {e}")
        print("Falling back to CPU...")
        pline = pipeline(
            "text-generation",
            model=model_id,
            device_map="cpu"
        )
        return pline

# --- Core Logic Function ---
def generate_and_save_report(pline, system_prompt, model_id, template_path, output_dir, date_filter):
    """Generates the report using the model and saves it to a file."""
    print("Generating report...")
    start_time = time.time()

    try:
        # Prepare initial message
        message = [{"role": "user", "content": system_prompt}]
        
        # Generate content using local LLM
        response = pline(message, max_new_tokens=512)
        end_time = time.time()

        # Extract the generated text
        generated_text = response[0]["generated_text"][-1]["content"]
        
        print("\nModel's response:\n", generated_text)
        print(f"\nResponse generated in: {end_time - start_time:.2f} seconds")

        # --- Save response to file ---
        # Extract the base name of the template file without extension
        prompt_template_basename = os.path.splitext(os.path.basename(template_path))[0]
        # Format the date_filter for use in a filename
        formatted_date_filter = date_filter.replace(' ', '_').replace(':', '-')
        # Construct the output filename including model name, template base name, and formatted date filter
        model_name = model_id.replace('/', '-')  # Replace '/' with '-' for filename
        output_filename = f"{model_name}-{prompt_template_basename}-{formatted_date_filter}.txt"
        output_filepath = os.path.join(output_dir, output_filename)

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Write the response text to the file
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(generated_text)
        print(f"\nResponse saved to: {output_filepath}")
        return generated_text
        
    except Exception as e:
        print(f"\nError during report generation or saving: {e}")
        return None

# --- Main Execution ---
def main():
    """Main function to orchestrate the report generation."""
    # 1. Parse Arguments
    args = parse_arguments()
    model_id = args.model_id
    prompt_template_path = args.template_path
    data_path = args.data_path
    date_filter = args.date_filter
    output_dir = args.output_dir
    device = args.device

    print(f"Using Model: {model_id}")
    print(f"Using Prompt Template: {prompt_template_path}")
    print(f"Using Data File: {data_path}")
    print(f"Using Device: {device}")

    # 2. Initialize Model
    pline = initialize_model(model_id, device)

    # 3. Load Prompt Template
    custom_instructions = load_prompt_template(prompt_template_path)

    # 4. Load and Prepare Data
    traffic_data = load_data(data_path, date_filter)
    print(f"Loaded traffic data:\n{traffic_data}\n\n")
    
    # 5. Construct System Prompt
    system_prompt = f"{custom_instructions}\n\n{traffic_data}"
    # print("\n--- System Prompt ---") # Uncomment to print the full prompt
    # print(system_prompt)
    # print("--- End System Prompt ---\n")

    # 6. Generate and Save Report
    generate_and_save_report(pline, system_prompt, model_id, prompt_template_path, output_dir, date_filter)

if __name__ == "__main__":
    main()
