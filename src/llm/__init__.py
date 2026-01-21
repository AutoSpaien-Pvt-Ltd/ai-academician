"""LLM provider abstractions for AI Academician."""

from src.llm.base import BaseLLMProvider, LLMResponse
from src.llm.openai_provider import OpenAIProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.claude_provider import ClaudeProvider
from src.llm.huggingface_provider import HuggingFaceProvider
from src.config import LLMProvider, get_config

__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "OpenAIProvider",
    "GeminiProvider",
    "ClaudeProvider",
    "HuggingFaceProvider",
    "get_llm_provider",
]


def get_llm_provider(provider: LLMProvider | None = None) -> BaseLLMProvider:
    """Get an LLM provider instance.

    Args:
        provider: The provider to use. If None, uses default from config.

    Returns:
        An LLM provider instance.

    Raises:
        ValueError: If the provider is not configured.
    """
    config = get_config()
    llm_config = config.get_llm_config(provider)

    provider_map = {
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.GEMINI: GeminiProvider,
        LLMProvider.CLAUDE: ClaudeProvider,
        LLMProvider.HUGGINGFACE: HuggingFaceProvider,
    }

    provider_class = provider_map.get(llm_config.provider)
    if not provider_class:
        raise ValueError(f"Unknown provider: {llm_config.provider}")

    return provider_class(llm_config)
