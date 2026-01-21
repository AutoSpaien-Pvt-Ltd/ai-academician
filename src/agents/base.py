"""Base agent class for AI Academician."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from src.config import LLMProvider, get_config
from src.llm import get_llm_provider, BaseLLMProvider
from src.models.session import ResearchSession
from src.utils.logger import get_logger


class AgentState(str, Enum):
    """State of an agent."""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    ERROR = "error"
    BLOCKED = "blocked"


@dataclass
class AgentResult:
    """Result from an agent operation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    needs_input: bool = False
    input_prompt: Optional[str] = None
    tokens_used: int = 0
    processing_time: float = 0.0
    next_action: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "needs_input": self.needs_input,
            "input_prompt": self.input_prompt,
            "tokens_used": self.tokens_used,
            "processing_time": self.processing_time,
            "next_action": self.next_action,
        }


class BaseAgent(ABC):
    """Base class for all agents."""

    # Agent name for identification
    name: str = "base_agent"

    # System prompt template for this agent
    system_prompt: str = "You are a helpful AI assistant."

    def __init__(
        self,
        session: Optional[ResearchSession] = None,
        provider: Optional[LLMProvider] = None,
    ):
        """Initialize the agent.

        Args:
            session: The research session this agent is working on
            provider: LLM provider to use (defaults to session or config default)
        """
        self.session = session
        self.state = AgentState.IDLE
        self._logger = get_logger(f"agent.{self.name}")

        # Determine which LLM provider to use
        if provider:
            self._provider_type = provider
        elif session and self.name in session.agent_providers:
            self._provider_type = session.agent_providers[self.name]
        else:
            config = get_config()
            self._provider_type = config.get_agent_provider(self.name)

        self._llm: Optional[BaseLLMProvider] = None

    @property
    def llm(self) -> BaseLLMProvider:
        """Get the LLM provider, lazily initialized."""
        if self._llm is None:
            self._llm = get_llm_provider(self._provider_type)
        return self._llm

    @abstractmethod
    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the agent's main task.

        Args:
            **kwargs: Task-specific arguments

        Returns:
            AgentResult with the outcome
        """
        pass

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a response using the LLM.

        Args:
            prompt: The user prompt
            context: Optional additional context
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            Generated text
        """
        self.state = AgentState.PROCESSING

        try:
            if context:
                response = await self.llm.generate_with_context(
                    prompt=prompt,
                    context=context,
                    system_prompt=self.system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                response = await self.llm.generate(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

            self.state = AgentState.COMPLETED
            return response.content

        except Exception as e:
            self.state = AgentState.ERROR
            self._logger.error(f"Generation failed: {e}")
            raise

    async def request_user_input(self, prompt: str) -> AgentResult:
        """Request input from the user.

        Args:
            prompt: The prompt to show the user

        Returns:
            AgentResult indicating input is needed
        """
        self.state = AgentState.WAITING_INPUT
        return AgentResult(
            success=True,
            needs_input=True,
            input_prompt=prompt,
        )

    def log_info(self, message: str) -> None:
        """Log an info message."""
        self._logger.info(f"[{self.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        self._logger.error(f"[{self.name}] {message}")

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(f"[{self.name}] {message}")
