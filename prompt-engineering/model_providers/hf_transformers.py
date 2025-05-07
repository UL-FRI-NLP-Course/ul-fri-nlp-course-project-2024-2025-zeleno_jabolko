import os
os.environ['HF_HOME'] = '.huggingface_cache/'

from transformers import pipeline


from . import ModelProvider

class HuggingFaceTransformersProvider(ModelProvider):
    pline: pipeline
    def __init__(self, model_name):
        self.model_name = model_name

    def configure(self):
        self.pline = pipeline(
            "text-generation",
            model=self.model_name,
            device_map="cuda"
        )

    def generate_content(self, prompt):
        message = [{"role": "user", "content": prompt}]
        response = self.pline(message, max_new_tokens=512)
        return response

__provider = HuggingFaceTransformersProvider
