import google.generativeai as genai
from gemini_api import generate_and_save_report, load_data
from dotenv import load_dotenv
import os
import glob
import datetime
from striprtf.striprtf import rtf_to_text


reports_dir = './prompt-engineering/reports'
original_reports_dir = './prompt-engineering/reports-originals'

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
eval_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

scores = {}
original_reports = glob.glob(os.path.join(original_reports_dir, '*.rtf'))
generated_reports = glob.glob(os.path.join(reports_dir, '*.txt'))

print(f"Found {len(original_reports)} original reports")
print(f"Found {len(generated_reports)} generated reports")

# scores structure: {model_name: {template_name: {time: [score1, score2, score3]}}}

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

def get_corresponding_files(original_path, generated_reports):
    # Extract date from original path (format: 2022-01-01_10-00-00.rtf)
    base_name = os.path.basename(original_path)
    date_str = base_name.split('.')[0]  # Get 2022-01-01_10-00-00
    
    print(f"Looking for generated reports matching date: {date_str}")
    # Find matching generated report
    matching_reports = [
        report for report in generated_reports
        if date_str in report  # Check if the date string appears anywhere in the filename
    ]
    
    if not matching_reports:
        print(f"No matches found among generated reports:")
        for report in generated_reports:
            print(f"  - {report}")
    
    return matching_reports

# Process each original report
for original_path in original_reports:
    print(f"\nProcessing original report: {original_path}")
    matching_reports = get_corresponding_files(original_path, generated_reports)
    print(f"Found {len(matching_reports)} matching generated reports")
    
    original_content = read_file_content(original_path)
    original_content = rtf_to_text(original_content)
    
    for generated_path in matching_reports:
        print(f"\nComparing with generated report: {generated_path}")
        generated_content = read_file_content(generated_path)
        
        # Extract model and template names from the generated report filename
        # Format: gemini-2.0-flash-v1-2022-01-01_10-00-00.txt
        filename = os.path.basename(generated_path)[:-4]  # remove .txt
        # Extract everything before the date
        model_part = filename.split('-2022-')[0]
        model_name = model_part  # The whole part before date is the model name
        template_name = "default"  # Since template isn't in filename, use default
        
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
                        f"Date: {filename.split('-')[-1]}\n"
                        f"Model: {model_name}\n"
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
from datetime import datetime

timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
eval_output_path = os.path.join(reports_dir, f'evaluation-{timestamp}.txt')

output_lines = []
output_lines.append("\nEvaluation Results:")
output_lines.append("==================")
for model_name, templates in scores.items():
    output_lines.append(f"\nModel-Template: {model_name}")
    for template_name, score_lists in templates.items():
        if score_lists:
            # Calculate averages for each metric
            avg_scores = [
                sum(metric_scores) / len(metric_scores)
                for metric_scores in zip(*score_lists)
            ]
            output_lines.append(f"Scores:")
            output_lines.append(f"- Event similarity: {avg_scores[0]:.2f}")
            output_lines.append(f"- Road naming accuracy: {avg_scores[1]:.2f}")
            output_lines.append(f"- Length similarity: {avg_scores[2]:.2f}")
            output_lines.append(f"- Overall average: {sum(avg_scores) / 3:.2f}")

# Print to console
print('\n'.join(output_lines))

# Write to file
with open(eval_output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))
print(f"\nEvaluation results written to {eval_output_path}")

