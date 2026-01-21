"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from src.config import LLMConfig


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    model: str
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: str = "stop"
    raw_response: Optional[Any] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "finish_reason": self.finish_reason,
        }


@dataclass
class Message:
    """A message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {"role": self.role, "content": self.content}


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        """Initialize the provider.

        Args:
            config: LLM configuration
        """
        self.config = config
        self._client: Optional[Any] = None

    @property
    def model(self) -> str:
        """Get the model name."""
        return self.config.model

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a response from a single prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            LLM response
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a response from a conversation.

        Args:
            messages: List of conversation messages
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            LLM response
        """
        pass

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Generate a response with additional context.

        Args:
            prompt: The user prompt
            context: Additional context to include
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            LLM response
        """
        full_prompt = f"Context:\n{context}\n\nTask:\n{prompt}"
        return await self.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _get_temperature(self, override: Optional[float]) -> float:
        """Get temperature, using override if provided."""
        return override if override is not None else self.config.temperature

    def _get_max_tokens(self, override: Optional[int]) -> int:
        """Get max tokens, using override if provided."""
        return override if override is not None else self.config.max_tokens

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available.

        Returns:
            True if the provider is healthy
        """
        pass
