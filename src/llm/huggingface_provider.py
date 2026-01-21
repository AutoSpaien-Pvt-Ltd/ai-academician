"""HuggingFace LLM provider implementation."""

from typing import Optional

import aiohttp

from src.config import LLMConfig
from src.llm.base import BaseLLMProvider, LLMResponse, Message
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace Inference API provider."""

    API_URL = "https://api-inference.huggingface.co/models"

    def __init__(self, config: LLMConfig):
        """Initialize HuggingFace provider."""
        super().__init__(config)
        self._headers = {"Authorization": f"Bearer {config.api_key}"}

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a response from a single prompt."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]"

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "temperature": self._get_temperature(temperature),
                "max_new_tokens": self._get_max_tokens(max_tokens),
                "return_full_text": False,
            },
        }

        url = f"{self.API_URL}/{self.model}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self._headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()

        # Handle response format
        if isinstance(result, list) and len(result) > 0:
            content = result[0].get("generated_text", "")
        else:
            content = str(result)

        return LLMResponse(
            content=content,
            model=self.model,
            tokens_used=0,  # HF API doesn't always return token counts
            finish_reason="stop",
            raw_response=result,
        )

    async def chat(
        self,
        messages: list[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a response from a conversation."""
        # Format messages for instruction-tuned models
        formatted_prompt = ""
        system_content = ""

        for msg in messages:
            if msg.role == "system":
                system_content = msg.content
            elif msg.role == "user":
                if system_content:
                    formatted_prompt += f"<s>[INST] <<SYS>>\n{system_content}\n<</SYS>>\n\n{msg.content} [/INST]"
                    system_content = ""
                else:
                    formatted_prompt += f"<s>[INST] {msg.content} [/INST]"
            elif msg.role == "assistant":
                formatted_prompt += f" {msg.content} </s>"

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "temperature": self._get_temperature(temperature),
                "max_new_tokens": self._get_max_tokens(max_tokens),
                "return_full_text": False,
            },
        }

        url = f"{self.API_URL}/{self.model}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self._headers, json=payload) as response:
                response.raise_for_status()
                result = await response.json()

        if isinstance(result, list) and len(result) > 0:
            content = result[0].get("generated_text", "")
        else:
            content = str(result)

        return LLMResponse(
            content=content,
            model=self.model,
            tokens_used=0,
            finish_reason="stop",
            raw_response=result,
        )

    async def health_check(self) -> bool:
        """Check if HuggingFace is available."""
        try:
            url = f"{self.API_URL}/{self.model}"
            payload = {
                "inputs": "Hi",
                "parameters": {"max_new_tokens": 5},
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self._headers, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"HuggingFace health check failed: {e}")
            return False
