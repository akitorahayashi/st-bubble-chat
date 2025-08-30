import time
from typing import Optional

from src.clients.ollama_api_client.interface import OllamaClientInterface


class MockOllamaApiClient(OllamaClientInterface):
    """
    A mock client for testing and development purposes.
    """

    def __init__(self):
        self.mock_responses = [
            "こんにちは！どのようなお手伝いができますか？",
            "それは興味深い質問ですね。詳しく教えてください。",
            "分かりました。他に何かご質問はありますか？",
            "そうですね、その通りだと思います。",
            "申し訳ございませんが、もう少し具体的に教えていただけますか？",
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
            "テスト": "これはテスト応答です。",
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
