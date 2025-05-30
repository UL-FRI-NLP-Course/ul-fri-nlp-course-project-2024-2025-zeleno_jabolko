import google.generativeai as genai
from gemini_api import generate_and_save_report, load_data
from dotenv import load_dotenv
import os
import glob
import json
from datetime import datetime
import re


reports_dir = './prompt-engineering/reports'
original_reports_json = './prompt-engineering/reports-originals/dataset-2024.json'

evalutation_template_string = f"""
Please examine the reports provided in <original-report> and <generated-report> tags and provide a grading in similarity (range the scores from 0 to 100) on the following aspects:
- are the same underlying events mentioned (wordking can be different)
- are the road namings the same in both reports
- is the length of the report similar to the original report

Return the scores in the following format:
<scores>
X, Y, Z
</scores>
"""

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
eval_model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

scores = {}

# Load original reports from JSON once
print("Loading original reports from JSON...")
with open(original_reports_json, 'r', encoding='utf-8') as f:
    original_reports_data = json.load(f)

print(f"Loaded {len(original_reports_data)} original reports from JSON")

# Get all generated reports
generated_reports = glob.glob(os.path.join(reports_dir, '*.txt'))
# Filter out comparison and evaluation files
generated_reports = [f for f in generated_reports if not (
    'comparison' in os.path.basename(f) or 'evaluation' in os.path.basename(f)
)]

print(f"Found {len(generated_reports)} generated reports")

# scores structure: {model_name: {template_name: [score1, score2, score3]}}}

log_comparisons = True  # Set to False to disable logging
comparison_log_path = os.path.join(reports_dir, 'comparison-log.txt')

def read_file_content(file_path):
    print(f"Reading file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"Successfully read file with {len(content)} characters")
    return content

def extract_scores(response_text):
    try:
        # Extract text between <scores> tags
        start = response_text.find('<scores>') + len('<scores>')
        end = response_text.find('</scores>')
        scores_text = response_text[start:end].strip()
        # Convert scores to integers
        return [int(score.strip()) for score in scores_text.split(',')]
    except:
        print(f"Error parsing scores from response: {response_text}")
        return None

def find_matching_original_report(generated_filename, original_reports):
    """
    Find the matching original report based on date and time.
    Generated filename format: model-template-YYYY-MM-DD_HH-MM-SS.txt
    Original report date format: "YYYY-MM-DD HH:MM:SS"
    """
    # Extract date and time from generated filename
    date_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.txt$', generated_filename)
    if not date_match:
        print(f"Could not extract date from filename: {generated_filename}")
        return None
    
    date_str = date_match.group(1)
    # Convert format from YYYY-MM-DD_HH-MM-SS to YYYY-MM-DD HH:MM:SS
    # First replace underscore with space
    formatted_date = date_str.replace('_', ' ')
    # Split into date and time parts
    parts = formatted_date.split(' ')
    if len(parts) == 2:
        date_part = parts[0]  # Keep date part as is (YYYY-MM-DD)
        time_part = parts[1].replace('-', ':')  # Convert time dashes to colons
        formatted_date = f"{date_part} {time_part}"
    
    print(f"Looking for original report with date: {formatted_date}")
    
    # Find matching original report
    for original in original_reports:
        if original['date'] == formatted_date:
            print(f"Found matching original report for date: {formatted_date}")
            return original
    
    print(f"No matching original report found for date: {formatted_date}")
    return None

def parse_model_template_from_filename(filename):
    """
    Extract model name and template from generated report filename.
    Format: model-template-YYYY-MM-DD_HH-MM-SS.txt
    """
    base_name = os.path.basename(filename)[:-4]  # remove .txt
    
    # Extract everything before the date
    date_match = re.search(r'-(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})$', base_name)
    if date_match:
        model_template_part = base_name[:date_match.start()]
        
        # Split the model-template part to extract model and template
        # Look for template patterns like v1, v2, etc., or multi-shot, zero-shot
        template_patterns = [
            r'-(v\d+)$',  # matches -v1, -v2, etc.
            r'-(v\d+-(multi-shot|zero-shot))$',  # matches -v6-multi-shot, -v6-zero-shot
            r'-(multi-shot)$',  # matches -multi-shot
            r'-(zero-shot)$',   # matches -zero-shot
        ]
        
        template = "default"
        model_name = model_template_part
        
        for pattern in template_patterns:
            match = re.search(pattern, model_template_part)
            if match:
                template = match.group(1)
                model_name = model_template_part[:match.start()]
                break
        
        return model_name, template
    
    # Fallback: use the whole part as model name
    return base_name, "default"

# Process each generated report
for generated_path in generated_reports:
    print(f"\nProcessing generated report: {generated_path}")
    
    # Find matching original report
    original_report = find_matching_original_report(os.path.basename(generated_path), original_reports_data)
    
    if not original_report:
        print(f"Skipping {generated_path} - no matching original report found")
        continue
    
    # Read generated report content
    generated_content = read_file_content(generated_path)
    original_content = original_report['output']
    
    # Extract model and template names from filename
    model_name, template_name = parse_model_template_from_filename(generated_path)
    print(f"Model: {model_name}, Template: {template_name}")

    # Prepare the prompt
    prompt = (
        evalutation_template_string
        + f"\n<original-report>{original_content}</original-report>"
        + f"\n<generated-report>{generated_content}</generated-report>"
    )
    
    try:
        import time
        time.sleep(10)  # To avoid hitting the rate limit
        print("Sending request to Gemini...")
        # Get evaluation from Gemini
        response = eval_model.generate_content(prompt)
        print(f"Received response: {response.text}")
        evaluation_scores = extract_scores(response.text)
        print(f"Extracted scores: {evaluation_scores}")
        
        if evaluation_scores and len(evaluation_scores) == 3:
            # Initialize nested dictionaries if they don't exist
            if model_name not in scores:
                scores[model_name] = {}
            if template_name not in scores[model_name]:
                scores[model_name][template_name] = []
            
            # Store the scores
            scores[model_name][template_name].append(evaluation_scores)
            print(f"Successfully stored scores for {model_name}/{template_name}")

            # Log comparison if enabled
            if log_comparisons:
                log_entry = (
                    "-----\n"
                    f"Date: {original_report['date']}\n"
                    f"Model: {model_name}\n"
                    f"Template: {template_name}\n"
                    f"Score: {','.join(map(str, evaluation_scores))}\n"
                    "Original report:\n"
                    f"{original_content}\n\n"
                    "Generated report:\n"
                    f"{generated_content}\n"
                    "-----\n"
                )
                with open(comparison_log_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(log_entry)
        else:
            print(f"Invalid scores received for {generated_path}")
    
    except Exception as e:
        print(f"Error processing {generated_path}: {str(e)}")

print("\nFinal scores dictionary:")
print(scores)

# Calculate and print averages
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
eval_output_path = os.path.join(reports_dir, f'evaluation-{timestamp}.txt')

output_lines = []
output_lines.append("\nEvaluation Results:")
output_lines.append("==================")
for model_name, templates in scores.items():
    for template_name, score_lists in templates.items():
        if score_lists:
            # Calculate averages for each metric
            avg_scores = [
                sum(metric_scores) / len(metric_scores)
                for metric_scores in zip(*score_lists)
            ]
            output_lines.append(f"\nModel-Template: {model_name}-{template_name}")
            output_lines.append(f"Scores:")
            output_lines.append(f"- Event similarity: {avg_scores[0]:.2f}")
            output_lines.append(f"- Road naming accuracy: {avg_scores[1]:.2f}")
            output_lines.append(f"- Length similarity: {avg_scores[2]:.2f}")
            output_lines.append(f"- Overall average: {sum(avg_scores) / 3:.2f}")
            output_lines.append(f"- Count: {len(score_lists)} evaluations")

# Print to console
print('\n'.join(output_lines))

# Write to file
with open(eval_output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))
print(f"\nEvaluation results written to {eval_output_path}")

