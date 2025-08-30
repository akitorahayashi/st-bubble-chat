import asyncio
from typing import AsyncGenerator

from src.clients.ollama_api_client.interface import OllamaClientInterface

# Streaming configuration constants
CHARACTER_DELAY = 0.08  # Delay between characters (seconds)
WORD_SPACE_DELAY = 0.05  # Delay for spaces between words (seconds)


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

    async def _stream_response(self, response_text: str) -> AsyncGenerator[str, None]:
        """
        Stream a response text character by character with word boundaries.
        """
        words = response_text.split()
        for i, word in enumerate(words):
            # Stream each character of the word
            for j, char in enumerate(word):
                await asyncio.sleep(CHARACTER_DELAY)
                yield char
            
            # Add space after word (except for the last word)
            if i < len(words) - 1:
                await asyncio.sleep(WORD_SPACE_DELAY)
                yield " "

    def generate(self, prompt: str, model: str = None) -> AsyncGenerator[str, None]:
        """
        Generates mock text responses with streaming.

        Args:
            prompt: The prompt to send to the model (ignored in mock).
            model: The name of the model to use for generation (ignored in mock).

        Returns:
            AsyncGenerator yielding text chunks.
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
                return self._stream_response(response)

        # デフォルトのモック応答
        response = self.mock_responses[self.response_index % len(self.mock_responses)]
        self.response_index += 1
        
        full_response = f"{response}\n\n（{prompt[:30]} に対するモック応答）"
        
        return self._stream_response(full_response)
