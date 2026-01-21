"""Google Gemini LLM provider implementation."""

from typing import Optional

import google.generativeai as genai

from src.config import LLMConfig
from src.llm.base import BaseLLMProvider, LLMResponse, Message
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self, config: LLMConfig):
        """Initialize Gemini provider."""
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self._model = genai.GenerativeModel(config.model)

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
            full_prompt = f"{system_prompt}\n\n{prompt}"

        generation_config = genai.GenerationConfig(
            temperature=self._get_temperature(temperature),
            max_output_tokens=self._get_max_tokens(max_tokens),
        )

        response = await self._model.generate_content_async(
            full_prompt,
            generation_config=generation_config,
        )

        # Extract token counts if available
        tokens_used = 0
        if hasattr(response, 'usage_metadata'):
            tokens_used = getattr(response.usage_metadata, 'total_token_count', 0)

        return LLMResponse(
            content=response.text,
            model=self.config.model,
            tokens_used=tokens_used,
            finish_reason="stop",
            raw_response=response,
        )

    async def chat(
        self,
        messages: list[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a response from a conversation."""
        # Convert messages to Gemini format
        chat = self._model.start_chat(history=[])

        generation_config = genai.GenerationConfig(
            temperature=self._get_temperature(temperature),
            max_output_tokens=self._get_max_tokens(max_tokens),
        )

        # Process system messages first
        system_content = ""
        for msg in messages:
            if msg.role == "system":
                system_content += msg.content + "\n"

        # Build conversation history
        for msg in messages:
            if msg.role == "user":
                content = msg.content
                if system_content:
                    content = f"{system_content}\n{content}"
                    system_content = ""  # Only prepend once
                response = await chat.send_message_async(
                    content,
                    generation_config=generation_config,
                )
            elif msg.role == "assistant":
                # Add to history
                chat.history.append({
                    "role": "model",
                    "parts": [msg.content],
                })

        # Get token count if available
        tokens_used = 0
        if hasattr(response, 'usage_metadata'):
            tokens_used = getattr(response.usage_metadata, 'total_token_count', 0)

        return LLMResponse(
            content=response.text,
            model=self.config.model,
            tokens_used=tokens_used,
            finish_reason="stop",
            raw_response=response,
        )

    async def health_check(self) -> bool:
        """Check if Gemini is available."""
        try:
            response = await self._model.generate_content_async(
                "Hi",
                generation_config=genai.GenerationConfig(max_output_tokens=5),
            )
            return bool(response.text)
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False
