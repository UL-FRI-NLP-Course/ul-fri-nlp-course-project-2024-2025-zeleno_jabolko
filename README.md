# Natural language processing course: `Automatic generation of Slovenian traffic news for RTV Slovenija`


## Assignment

LLM, »fine-tune« it, leverage prompt engineering techniques to generate short traffic reports. You are given Excel data from promet.si portal and your goal is to generate regular and important traffic news that are read by the radio presenters at RTV Slovenija. You also need to take into account guidelines and instructions to form the news. Currently, they hire students to manually check and type reports that are read every 30 minutes.

### Methodology

1. Literature Review: Conduct a thorough review of existing research and select appropriate LLMs for the task. Review and prepare an exploratory report on the data provided.
2. Initial solution: Try to solve the task initially only by using prompt engineering techniques.
3. Evaulation definition: Define (semi-)automatic evaluation criteria and implement it. Take the following into account: identification of important news, correct roads namings, correct filtering, text lengths and words, ...
4. LLM (Parameter-efficient) fine-tuning: Improve an existing LLM to perform the task automatically. Provide an interface to do an interactive test.
5. Evaluation and Performance Analysis: Assess the effectiveness of each technique by measuring improvements in model performance, using appropriate automatic (P, R, F1) and human evaluation metrics.

### Recommended Literature

- Lab session materials
- RTV Slo data: [LINK](https://unilj-my.sharepoint.com/:u:/g/personal/slavkozitnik_fri1_uni-lj_si/EdQ2XlMf8eJMleZoxUc89E4B0lDWdyAzFh3xmKxg9y_pVA?e=EOQ54M) (zip format). The data consists of:
  - Promet.si input resources (Podatki - PrometnoPorocilo_2022_2023_2024.xlsx).
  - RTV Slo news texts to be read through the radio stations (Podatki - rtvslo.si).
  - Additional instructions for the students that manually type news texts (PROMET, osnove.docx, PROMET.docx).
  
