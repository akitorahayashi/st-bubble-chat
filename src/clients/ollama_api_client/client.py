import logging
import os
from typing import Optional

import requests
import streamlit as st

from .interface import OllamaClientInterface

logger = logging.getLogger(__name__)


class OllamaApiClient(OllamaClientInterface):
    """
    A client for interacting with the Ollama API.
    """

    def __init__(self):
        self.api_url = os.getenv("OLLAMA_API_ENDPOINT")
        if not self.api_url:
            # Fallback to Streamlit secrets if available
            try:
                self.api_url = st.secrets.get("OLLAMA_API_ENDPOINT")
            except Exception:
                pass

        if not self.api_url:
            raise ValueError(
                "OLLAMA_API_ENDPOINT is not configured in environment variables or Streamlit secrets."
            )
        self.generate_endpoint = f"{self.api_url}/api/v1/generate"

    def generate(self, prompt: str, model: str = None) -> Optional[str]:
        """
        Generates text using the Ollama API.

        Args:
            prompt: The prompt to send to the model.
            model: The name of the model to use for generation.

        Returns:
            The generated text from the API, or None if an error occurs.

        Raises:
            requests.exceptions.RequestException: If a network error occurs.
        """
        # Use environment variable model if not specified
        if model is None:
            model = os.getenv("OLLAMA_MODEL")
            if not model:
                raise ValueError(
                    "OLLAMA_MODEL is not configured in environment variables."
                )

        payload = {
            "prompt": prompt,
            "model": model,
            "stream": False,
        }
        try:
            response = requests.post(
                self.generate_endpoint,
                json=payload,
                timeout=(10, 120),  # (connect, read)
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Ollama API call: {e}")
            return None
