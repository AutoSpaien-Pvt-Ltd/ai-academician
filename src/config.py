"""Configuration management for AI Academician."""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    HUGGINGFACE = "huggingface"


class CitationStyle(str, Enum):
    """Supported citation styles."""
    APA = "APA"
    MLA = "MLA"
    CHICAGO = "CHICAGO"
    IEEE = "IEEE"
    HARVARD = "HARVARD"


class ExportFormat(str, Enum):
    """Supported export formats."""
    PDF = "pdf"
    DOCX = "docx"
    LATEX = "latex"


@dataclass
class LLMConfig:
    """Configuration for a specific LLM provider."""
    provider: LLMProvider
    model: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class SearchConfig:
    """Configuration for search APIs."""
    google_api_key: str
    google_cse_id: str
    max_results_per_query: int = 10
    min_sources: int = 20
    max_sources: int = 30


@dataclass
class PaperConfig:
    """Configuration for paper generation."""
    default_word_count: int = 18000
    min_word_count: int = 5000
    max_word_count: int = 30000
    default_citation_style: CitationStyle = CitationStyle.APA
    min_review_cycles: int = 2
    max_review_cycles: int = 5


@dataclass
class StorageConfig:
    """Configuration for storage."""
    database_path: Path = field(default_factory=lambda: Path("./data/ai_academician.db"))
    output_dir: Path = field(default_factory=lambda: Path("./output"))


@dataclass
class Config:
    """Main configuration class."""
    llm_configs: dict[LLMProvider, LLMConfig] = field(default_factory=dict)
    default_provider: LLMProvider = LLMProvider.GEMINI
    agent_providers: dict[str, LLMProvider] = field(default_factory=dict)
    search: SearchConfig = field(default_factory=lambda: SearchConfig(
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        google_cse_id=os.getenv("GOOGLE_CSE_ID", ""),
    ))
    paper: PaperConfig = field(default_factory=PaperConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        llm_configs = {}

        # OpenAI
        if api_key := os.getenv("OPENAI_API_KEY"):
            llm_configs[LLMProvider.OPENAI] = LLMConfig(
                provider=LLMProvider.OPENAI,
                model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                api_key=api_key,
            )

        # Gemini
        if api_key := os.getenv("GOOGLE_API_KEY"):
            llm_configs[LLMProvider.GEMINI] = LLMConfig(
                provider=LLMProvider.GEMINI,
                model=os.getenv("GEMINI_MODEL", "gemini-pro"),
                api_key=api_key,
            )

        # Claude
        if api_key := os.getenv("ANTHROPIC_API_KEY"):
            llm_configs[LLMProvider.CLAUDE] = LLMConfig(
                provider=LLMProvider.CLAUDE,
                model=os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229"),
                api_key=api_key,
            )

        # HuggingFace
        if api_key := os.getenv("HUGGINGFACE_API_KEY"):
            llm_configs[LLMProvider.HUGGINGFACE] = LLMConfig(
                provider=LLMProvider.HUGGINGFACE,
                model=os.getenv("HUGGINGFACE_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1"),
                api_key=api_key,
            )

        default_provider_str = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        default_provider = LLMProvider(default_provider_str)

        search_config = SearchConfig(
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            google_cse_id=os.getenv("GOOGLE_CSE_ID", ""),
            min_sources=int(os.getenv("MIN_SOURCES", "20")),
            max_sources=int(os.getenv("MAX_SOURCES", "30")),
        )

        paper_config = PaperConfig(
            default_word_count=int(os.getenv("DEFAULT_WORD_COUNT", "18000")),
            default_citation_style=CitationStyle(os.getenv("DEFAULT_CITATION_STYLE", "APA")),
            min_review_cycles=int(os.getenv("MIN_REVIEW_CYCLES", "2")),
            max_review_cycles=int(os.getenv("MAX_REVIEW_CYCLES", "5")),
        )

        storage_config = StorageConfig(
            database_path=Path(os.getenv("DATABASE_PATH", "./data/ai_academician.db")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "./output")),
        )

        return cls(
            llm_configs=llm_configs,
            default_provider=default_provider,
            search=search_config,
            paper=paper_config,
            storage=storage_config,
        )

    def get_llm_config(self, provider: Optional[LLMProvider] = None) -> LLMConfig:
        """Get LLM configuration for a provider, with fallback."""
        provider = provider or self.default_provider
        if provider in self.llm_configs:
            return self.llm_configs[provider]
        # Fallback to any available provider
        if self.llm_configs:
            return next(iter(self.llm_configs.values()))
        raise ValueError("No LLM provider configured")

    def get_agent_provider(self, agent_name: str) -> LLMProvider:
        """Get the LLM provider for a specific agent."""
        return self.agent_providers.get(agent_name, self.default_provider)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
