import json
import random
from pathlib import Path

template_path = "./prompt-engineering/prompt-templates/v2.txt"
dataset_path = "./fine-tuning/dataset-2024.json"
output_path = "./fine-tuning/dataset-2024-v2.json"

def load_template(template_path):
    """Load the prompt template."""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def load_dataset(dataset_path):
    """Load the original dataset."""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_record(record, template):
    """Process a single record by prepending template and wrapping output."""
    # Prepend template to input
    new_input = template + "\n" + record["input"]
    
    # Wrap output with traffic report tags
    new_output = f"<START_TRAFFIC_REPORT>\n{record['output']}\n<END_TRAFFIC_REPORT>"
    
    return {
        "input": new_input,
        "output": new_output,
        "date": record["date"]
    }

def split_dataset(data, train_ratio=0.8):
    """Split dataset into train and test sets."""
    # Shuffle the data for random split
    shuffled_data = data.copy()
    random.shuffle(shuffled_data)
    
    # Calculate split point
    split_point = int(len(shuffled_data) * train_ratio)
    
    train_data = shuffled_data[:split_point]
    test_data = shuffled_data[split_point:]
    
    return train_data, test_data

def main():
    print("Loading template...")
    template = load_template(template_path)
    
    print("Loading dataset...")
    dataset = load_dataset(dataset_path)
    print(f"Loaded {len(dataset)} records")
    
    print("Processing records...")
    processed_data = []
    for record in dataset:
        processed_record = process_record(record, template)
        processed_data.append(processed_record)
    
    print("Splitting dataset...")
    train_data, test_data = split_dataset(processed_data)
    print(f"Train set: {len(train_data)} records")
    print(f"Test set: {len(test_data)} records")
    
    # Create final dataset structure
    final_dataset = {
        "train": train_data,
        "test": test_data
    }
    
    print(f"Saving to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    
    print("Done!")
    print(f"Dataset saved to {output_path}")
    print(f"Total records: {len(processed_data)}")
    print(f"Train: {len(train_data)} ({len(train_data)/len(processed_data)*100:.1f}%)")
    print(f"Test: {len(test_data)} ({len(test_data)/len(processed_data)*100:.1f}%)")

if __name__ == "__main__":
    # Set random seed for reproducible splits
    random.seed(42)
    main()
