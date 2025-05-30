#python .\prompt-engineering\gemini_api.py --model_name "gemini-2.5-flash-preview-05-20" --template_path "./prompt-engineering/prompt-templates/v6-multi-shot.txt" --date_filter "2024-01-31 18:00:00"

import subprocess
import sys
import time

models = [
    "google/gemma-3-4b-it",
    "mmedved/gemma-3-finetune-v2",
    "mmedved/gemma-3-finetune-v6"
]

templates = [
    "v1",
    "v2",
    "v3",
    "v4",
    "v5",
    "v6",
    "v6-multi-shot",
    "v6-zero-shot",
]

date_filters = [
    "2024-07-21 06:30:00",
    "2024-07-21 11:00:00",
    "2024-10-19 15:30:00",
    "2024-10-20 08:30:00",
    "2024-10-20 13:00:00",
    "2024-11-18 09:30:00",
]

for model in models:
    for template in templates:
        for date_filter in date_filters:
            print(f"Generating reports for {model} with {template} and date filter {date_filter}")
            
            # Construct the command
            cmd = [
                sys.executable, 
                "./prompt-engineering/llm_local.py",
                "--model_id", model,
                "--template_path", f"./prompt-engineering/prompt-templates/{template}.txt",
                "--date_filter", date_filter
            ]
            
            try:
                # Execute the command
                result = subprocess.run(cmd)
                print(f"✓ Success: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Error: {e.stderr}")
                print(f"Return code: {e.returncode}")
            except Exception as e:
                print(f"✗ Unexpected error: {str(e)}")
            
            print("-" * 50)
            
