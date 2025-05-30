# Natural language processing course: `Automatic generation of Slovenian traffic news for RTV Slovenija`

## Prerequisites

Nvidia GPU with at least 16 GB of memory (e.g., RTX 3090, A6000, etc.) or access to a cloud service with similar capabilities (e.g., Google Colab Pro, AWS, Azure, etc.).
Or when running `./prompt_engineering/llm_local.py` use `--device cpu` option to run the code on CPU, but it will be very slow.

## Assignment

LLM, »fine-tune« it, leverage prompt engineering techniques to generate short traffic reports. You are given Excel data from promet.si portal and your goal is to generate regular and important traffic news that are read by the radio presenters at RTV Slovenija. You also need to take into account guidelines and instructions to form the news. Currently, they hire students to manually check and type reports that are read every 30 minutes.

### Methodology

1. Literature Review: Conduct a thorough review of existing research and select appropriate LLMs for the task. Review and prepare an exploratory report on the data provided.
2. Initial solution: Try to solve the task initially only by using prompt engineering techniques.
3. Evaulation definition: Define (semi-)automatic evaluation criteria and implement it. Take the following into account: identification of important news, correct roads namings, correct filtering, text lengths and words, ...
4. LLM (Parameter-efficient) fine-tuning: Improve an existing LLM to perform the task automatically. Provide an interface to do an interactive test.
5. Evaluation and Performance Analysis: Assess the effectiveness of each technique by measuring improvements in model performance, using appropriate automatic (P, R, F1) and human evaluation metrics.

## Project Structure

```plaintext
data/                     # Directory containing the original excel file
fine-tuning/              # Directory containing fine-tuning scripts and configurations
├── prompt_templates/     # Directory containing prompt templates for generating reports
├── dataset-2024.json/    # JSON converted dataset from original reports (excel)
prompt_engineering/       # Directory containing scripts for prompt engineering and evaluation
├── prompt_templates/     # Directory containing prompt templates for generating reports
├── reports/              # Directory to save generated reports
├── reports_original/     # Directory containing original reports (rtfs)
report/                   # Directory containing the latex report
```

## Tutorial to run

1. Clone the repository and run the following commands to install the required packages and run the code:
   ```bash
   git clone *this_repository_url*
   pip install -r requirements.txt
   python ./prompt_engineering/llm_local.py --model_id "mmedved/gemma-3-finetune-v6" --date_filter "2024-11-18 9:30:00"
   ```
Generated templates are saved in the `./prompt_engineering/reports` directory. The `--date_filter` argument is used to filter the reports by date and time, e.g., "2024-11-18 9:30:00" will generate reports for that specific date and time.

2. To evaluate generated data to expected output using Gemini run the following commands:

*Note 1: Make sure you generate your own API key for Gemini for free on the following link: [AI Studio](https://aistudio.google.com/)*
*Note 2: Make sure the reports dir is ./prompt_engineering/reports and original reports (rtfs) dir is ./prompt_engineering/reports_original*
  
```bash
python ./prompt_engineering/evaluator.py
``` 

3. To evaluate generated data to expected output using BERT and ROUGE metrics, run the following commands:

*Note 1: Output will be logged to console*
*Note 2: Make sure the dataset path is "./prompt_engineering/reports-originals/dataset-2024.json"*
*Note 2: dataset-2024.json is a dataset with RAW inputs from Excel converted to JSON format. If dataset is not present you can generate it with ./fine-tuning/create-dataset.py*

```bash
python ./prompt_engineering/evaluator-bert.py
python ./prompt_engineering/evaluator-rouge.py
```

### Recommended Literature

- Hugging Face Fine-tuned Gemma-3: [LINK](https://huggingface.co/mmedved/gemma-3-finetune-v6)
- Lab session materials
- RTV Slo data: [LINK](https://unilj-my.sharepoint.com/:u:/g/personal/slavkozitnik_fri1_uni-lj_si/EdQ2XlMf8eJMleZoxUc89E4B0lDWdyAzFh3xmKxg9y_pVA?e=EOQ54M) (zip format). The data consists of:
  - Promet.si input resources (Podatki - PrometnoPorocilo_2022_2023_2024.xlsx).
  - RTV Slo news texts to be read through the radio stations (Podatki - rtvslo.si).
  - Additional instructions for the students that manually type news texts (PROMET, osnove.docx, PROMET.docx).
  
