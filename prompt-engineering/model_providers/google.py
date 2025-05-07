import os
from typing import Any


from dotenv import load_dotenv
import google.generativeai as genai
from . import ModelProvider

class GoogleGeminiProvider(ModelProvider):
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None

    def configure(self):
        genai.configure(api_key=self.get_api_key())
        self.model = genai.GenerativeModel(self.model_name)

    def generate_content(self, prompt):
        return self.model.generate_content(prompt).text
    
    def get_api_key(self):
        load_dotenv()
        api_key: Any = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        return api_key

__provider = GoogleGeminiProvider
