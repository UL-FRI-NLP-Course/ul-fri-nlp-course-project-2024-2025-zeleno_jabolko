import json
import os
import re
from rouge_score import rouge_scorer
import numpy as np
from datetime import datetime

def load_dataset(dataset_path):
    """Load the original dataset from JSON file."""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_generated_reports(reports_dir):
    """
    Get all generated report files, excluding comparison and evaluation files.
    Returns a dictionary grouped by model-template combination.
    """
    reports_by_model = {}
    
    for filename in os.listdir(reports_dir):
        # Skip files that start with 'comparison' or 'evaluation'
        if filename.startswith('comparison') or filename.startswith('evaluation'):
            continue
            
        # Extract date from filename (format: {model}-{template}-{date}.txt)
        # Handle both patterns: model-v{template}-date.txt and model-template-date.txt
        date_match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.txt$', filename)
        if date_match:
            date_str = date_match.group(1)
            
            # Extract model-template combination (everything before the date)
            model_template = filename.replace(f'-{date_str}.txt', '')
            
            # Convert to datetime for easier matching
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d_%H-%M-%S')
                
                # Read the file content
                file_path = os.path.join(reports_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Initialize model-template group if not exists
                if model_template not in reports_by_model:
                    reports_by_model[model_template] = {}
                
                # Store with both original date string and datetime object
                reports_by_model[model_template][date_str] = {
                    'content': content,
                    'datetime': date_obj,
                    'filename': filename
                }
            except ValueError:
                print(f"Warning: Could not parse date from filename: {filename}")
                continue
    
    return reports_by_model

def match_reports_with_originals(dataset, generated_reports, model_template_name):
    """
    Match generated reports with original texts based on exact date and hour.
    Works with a specific model-template combination.
    Returns lists of matched references and predictions.
    """
    references = []
    predictions = []
    matched_pairs = []
    unmatched_originals = []
    
    for original in dataset:
        original_date_str = original['date']
        original_output = original['output']
        
        # Parse the original date (format: YYYY-MM-DD HH:MM:SS)
        try:
            original_date = datetime.strptime(original_date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(f"Warning: Could not parse original date: {original_date_str}")
            continue
        
        # Find exact matches for this date and hour in the specific model-template group
        found_match = False
        for date_key, report_data in generated_reports.items():
            generated_date = report_data['datetime']
            
            # Check if date and hour match exactly
            if (generated_date.year == original_date.year and
                generated_date.month == original_date.month and
                generated_date.day == original_date.day and
                generated_date.hour == original_date.hour):
                
                references.append(original_output)
                predictions.append(report_data['content'])
                matched_pairs.append({
                    'original_date': original_date_str,
                    'generated_file': report_data['filename'],
                    'model_template': model_template_name,
                    'exact_match': True
                })
                found_match = True
                break  # Take the first match for this date/hour
        
        if not found_match:
            unmatched_originals.append(original_date_str)
    
    return references, predictions, matched_pairs, unmatched_originals

def output_rouge_scores(references, predictions):
    """Calculate and output ROUGE scores in LaTeX table format."""
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL', 'rougeLsum'], use_stemmer=True)

    scores_accum = {
        'rouge1': {'p': [], 'r': [], 'f': []},
        'rouge2': {'p': [], 'r': [], 'f': []},
        'rougeL': {'p': [], 'r': [], 'f': []},
        'rougeLsum': {'p': [], 'r': [], 'f': []},
    }

    for pred, ref in zip(predictions, references):
        scores = scorer.score(ref, pred)
        for metric in scores:
            scores_accum[metric]['p'].append(scores[metric].precision)
            scores_accum[metric]['r'].append(scores[metric].recall)
            scores_accum[metric]['f'].append(scores[metric].fmeasure)

    scores = {
        metric: {
            'precision': np.mean(scores_accum[metric]['p']),
            'recall': np.mean(scores_accum[metric]['r']),
            'f1': np.mean(scores_accum[metric]['f']),
        }
        for metric in scores_accum
    }

    print("\nROUGE Evaluation Results:")
    print("=" * 60)
    print("Metric  &  Precision & Recall & F1-Score \\\\")
    print(f"ROUGE1 & {scores['rouge1']['precision']:.4f} & {scores['rouge1']['recall']:.4f} & {scores['rouge1']['f1']:.4f} \\\\ \\hline")
    print(f"ROUGE2 & {scores['rouge2']['precision']:.4f} & {scores['rouge2']['recall']:.4f} & {scores['rouge2']['f1']:.4f} \\\\ \\hline")
    print(f"ROUGEL & {scores['rougeL']['precision']:.4f} & {scores['rougeL']['recall']:.4f} & {scores['rougeL']['f1']:.4f} \\\\ \\hline")
    print(f"ROUGELsum & {scores['rougeLsum']['precision']:.4f} & {scores['rougeLsum']['recall']:.4f} & {scores['rougeLsum']['f1']:.4f} \\\\ \\hline")
    
    return scores

def main():
    # Paths
    dataset_path = "reports-originals/dataset-2024.json"
    reports_dir = "reports"
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, dataset_path)
    reports_dir = os.path.join(script_dir, reports_dir)
    
    print("Loading dataset...")
    dataset = load_dataset(dataset_path)
    print(f"Loaded {len(dataset)} original reports")
    
    print("\nLoading generated reports...")
    reports_by_model = get_generated_reports(reports_dir)
    
    total_generated = sum(len(reports) for reports in reports_by_model.values())
    print(f"Found {len(reports_by_model)} model-template combinations with {total_generated} total reports")
    
    # Evaluate each model-template combination separately
    all_results = {}
    
    for model_template, generated_reports in reports_by_model.items():
        print(f"\n{'='*80}")
        print(f"Evaluating: {model_template}")
        print(f"{'='*80}")
        
        print(f"Found {len(generated_reports)} reports for this model-template")
        
        # Match reports with originals for this specific model-template
        references, predictions, matched_pairs, unmatched_originals = match_reports_with_originals(
            dataset, generated_reports, model_template
        )
        
        print(f"Successfully matched {len(references)} pairs for {model_template}")
        
        if len(references) == 0:
            print(f"No matches found for {model_template}! Skipping ROUGE evaluation.")
            all_results[model_template] = None
            continue
        
        # Show matched pairs
        print(f"\nMatched pairs for {model_template}:")
        for pair in matched_pairs:
            print(f"  {pair['original_date']} -> {pair['generated_file']}")
        
        # Calculate and display ROUGE scores for this model-template
        scores = output_rouge_scores(references, predictions)
        all_results[model_template] = {
            'scores': scores,
            'matches': len(references),
            'total_generated': len(generated_reports)
        }
        
        # Print statistics for this model-template
        print(f"\nStatistics for {model_template}:")
        print(f"  Generated reports: {len(generated_reports)}")
        print(f"  Successfully matched: {len(references)}")
        print(f"  Match rate: {len(references)/len(generated_reports)*100:.1f}%")
    
    # Summary comparison table
    print(f"\n{'='*140}")
    print("SUMMARY - ROUGE SCORES COMPARISON")
    print(f"{'='*140}")
    
    if any(result is not None for result in all_results.values()):
        # Print header
        print(f"{'Model-Template':<45} {'Matches':<8} {'ROUGE-1':<30} {'ROUGE-2':<30} {'ROUGE-L':<30}")
        print(f"{'':45} {'':8} {'P':<10}{'R':<10}{'F1':<10} {'P':<10}{'R':<10}{'F1':<10} {'P':<10}{'R':<10}{'F1':<10}")
        print("-" * 140)
        
        for model_template, result in all_results.items():
            if result is not None:
                scores = result['scores']
                matches = result['matches']
                
                # ROUGE-1 scores
                r1_p = scores['rouge1']['precision']
                r1_r = scores['rouge1']['recall']
                r1_f1 = scores['rouge1']['f1']
                
                # ROUGE-2 scores
                r2_p = scores['rouge2']['precision']
                r2_r = scores['rouge2']['recall']
                r2_f1 = scores['rouge2']['f1']
                
                # ROUGE-L scores
                rl_p = scores['rougeL']['precision']
                rl_r = scores['rougeL']['recall']
                rl_f1 = scores['rougeL']['f1']
                
                print(f"{model_template:<45} {matches:<8} "
                      f"{r1_p:<10.4f}{r1_r:<10.4f}{r1_f1:<10.4f} "
                      f"{r2_p:<10.4f}{r2_r:<10.4f}{r2_f1:<10.4f} "
                      f"{rl_p:<10.4f}{rl_r:<10.4f}{rl_f1:<10.4f}")
            else:
                print(f"{model_template:<45} {'0':<8} "
                      f"{'N/A':<10}{'N/A':<10}{'N/A':<10} "
                      f"{'N/A':<10}{'N/A':<10}{'N/A':<10} "
                      f"{'N/A':<10}{'N/A':<10}{'N/A':<10}")
        
        # Add ROUGE-Lsum scores in a separate table
        print(f"\n{'='*100}")
        print("ROUGE-Lsum SCORES")
        print(f"{'='*100}")
        print(f"{'Model-Template':<45} {'Matches':<8} {'ROUGE-Lsum':<30}")
        print(f"{'':45} {'':8} {'P':<10}{'R':<10}{'F1':<10}")
        print("-" * 100)
        
        for model_template, result in all_results.items():
            if result is not None:
                scores = result['scores']
                matches = result['matches']
                
                # ROUGE-Lsum scores
                rls_p = scores['rougeLsum']['precision']
                rls_r = scores['rougeLsum']['recall']
                rls_f1 = scores['rougeLsum']['f1']
                
                print(f"{model_template:<45} {matches:<8} "
                      f"{rls_p:<10.4f}{rls_r:<10.4f}{rls_f1:<10.4f}")
            else:
                print(f"{model_template:<45} {'0':<8} "
                      f"{'N/A':<10}{'N/A':<10}{'N/A':<10}")
    else:
        print("No successful evaluations found!")
    
    # Overall statistics
    total_matches = sum(result['matches'] for result in all_results.values() if result is not None)
    print(f"\nOverall Statistics:")
    print(f"Total original reports: {len(dataset)}")
    print(f"Total model-template combinations: {len(reports_by_model)}")
    print(f"Total generated reports: {total_generated}")
    print(f"Total successful matches: {total_matches}")
    print(f"Overall coverage: {total_matches}/{len(dataset)} ({total_matches/len(dataset)*100:.1f}%)")

if __name__ == "__main__":
    main()
