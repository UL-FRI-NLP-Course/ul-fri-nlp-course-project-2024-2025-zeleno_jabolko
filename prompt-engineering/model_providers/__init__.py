from abc import ABC, abstractmethod

class ModelProvider(ABC):
    @abstractmethod
    def configure(self, api_key):
        pass

    @abstractmethod
    def generate_content(self, prompt) -> str:
        pass
