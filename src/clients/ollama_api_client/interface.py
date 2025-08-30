from abc import ABC, abstractmethod
from typing import Optional


class OllamaClientInterface(ABC):
    """
    Abstract base class for Ollama API clients.
    """

    @abstractmethod
    def generate(self, prompt: str, model: str = None) -> Optional[str]:
        """
        Generate text using the model.

        Args:
            prompt: The prompt to send to the model.
            model: The name of the model to use for generation.

        Returns:
            The generated text or None if an error occurs.
        """
        pass
