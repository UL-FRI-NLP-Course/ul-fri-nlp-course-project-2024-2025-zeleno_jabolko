#python .\prompt-engineering\gemini_api.py --model_name "gemini-2.5-flash-preview-05-20" --template_path "./prompt-engineering/prompt-templates/v6-multi-shot.txt" --date_filter "2024-01-31 18:00:00"

import subprocess
import sys
import time

models = [
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.0-flash",
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
    "2024-07-21 11:00:00",
    "2024-07-21 06:30:00",
    "2024-07-20 22:00:00",
    "2024-11-18 09:30:00",
    "2024-11-18 07:16:00",
    "2024-10-20 13:00:00",
    "2024-10-30 12:30:00",
    "2024-10-20 08:30:00",
    "2024-10-19 15:30:00",
    "2024-10-19 10:00:00"
]

for model in models:
    for template in templates:
        for date_filter in date_filters:
            print(f"Generating reports for {model} with {template} and date filter {date_filter}")
            
            # Construct the command
            cmd = [
                "python", 
                "./prompt-engineering/gemini_api.py",
                "--model_name", model,
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
            
            # Add delay to prevent rate limiting
            time.sleep(2)  # 2 second delay between API calls
