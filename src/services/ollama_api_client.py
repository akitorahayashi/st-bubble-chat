import logging
import os
import time
from typing import Optional

import requests
import streamlit as st

logger = logging.getLogger(__name__)


class OllamaApiClient:
    """
    A client for interacting with the Ollama API.
    """
    
    DEFAULT_MODEL = "llama3.2"

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
            model = os.getenv("OLLAMA_MODEL", self.DEFAULT_MODEL)
            
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


class MockOllamaApiClient:
    """
    A mock client for testing and development purposes.
    """
    
    DEFAULT_MODEL = "llama3.2"

    def __init__(self):
        self.mock_responses = [
            "こんにちは！どのようなお手伝いができますか？",
            "それは興味深い質問ですね。詳しく教えてください。", 
            "分かりました。他に何かご質問はありますか？",
            "そうですね、その通りだと思います。",
            "申し訳ございませんが、もう少し具体的に教えていただけますか？"
        ]
        self.response_index = 0

    def generate(self, prompt: str, model: str = None) -> Optional[str]:
        """
        Generates mock text responses.

        Args:
            prompt: The prompt to send to the model (ignored in mock).
            model: The name of the model to use for generation (ignored in mock).

        Returns:
            A mock generated text response.
        """
        # 特定の入力に対するカスタム応答
        custom_responses = {
            "fsfs": "（fsfs に対するモック応答）",
            "こんにちは": "こんにちは！元気ですか？",
            "hello": "Hello! How can I help you?",
            "test": "テスト用のモック応答です。",
            "テスト": "これはテスト応答です。"
        }
        
        # カスタム応答をチェック
        for key, response in custom_responses.items():
            if prompt.lower().strip() == key.lower():
                time.sleep(0.5)  # 短い遅延
                return response
        
        # デフォルトのモック応答
        # Simulate API call delay
        time.sleep(2)
        
        # Return mock response
        response = self.mock_responses[self.response_index % len(self.mock_responses)]
        self.response_index += 1
        
        return f"{response}\n\n（{prompt[:30]} に対するモック応答）"


def get_ollama_client():
    """
    Factory function to get the appropriate Ollama client based on DEBUG setting.
    
    Returns:
        OllamaApiClient or MockOllamaApiClient based on DEBUG environment variable.
    """
    is_debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes", "on")
    
    if is_debug:
        return MockOllamaApiClient()
    else:
        return OllamaApiClient()