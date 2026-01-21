"""Research session model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from src.config import CitationStyle, LLMProvider


class SessionStatus(str, Enum):
    """Status of a research session."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResearchSession:
    """Represents a complete paper generation workflow."""
    id: UUID = field(default_factory=uuid4)
    topic: str = ""
    title: str = ""
    citation_style: CitationStyle = CitationStyle.APA
    target_word_count: int = 18000
    target_journal: Optional[str] = None
    status: SessionStatus = SessionStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    default_provider: LLMProvider = LLMProvider.GEMINI
    agent_providers: dict[str, LLMProvider] = field(default_factory=dict)

    # Progress tracking
    current_stage: str = "init"
    progress_percentage: float = 0.0

    # Error tracking
    last_error: Optional[str] = None
    retry_count: int = 0

    def update_progress(self, stage: str, percentage: float) -> None:
        """Update the session progress."""
        self.current_stage = stage
        self.progress_percentage = percentage
        self.updated_at = datetime.now()

    def mark_completed(self) -> None:
        """Mark the session as completed."""
        self.status = SessionStatus.COMPLETED
        self.progress_percentage = 100.0
        self.updated_at = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Mark the session as failed."""
        self.status = SessionStatus.FAILED
        self.last_error = error
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "topic": self.topic,
            "title": self.title,
            "citation_style": self.citation_style.value,
            "target_word_count": self.target_word_count,
            "target_journal": self.target_journal,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "default_provider": self.default_provider.value,
            "current_stage": self.current_stage,
            "progress_percentage": self.progress_percentage,
            "last_error": self.last_error,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResearchSession":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            topic=data["topic"],
            title=data["title"],
            citation_style=CitationStyle(data["citation_style"]),
            target_word_count=data["target_word_count"],
            target_journal=data.get("target_journal"),
            status=SessionStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            default_provider=LLMProvider(data["default_provider"]),
            current_stage=data.get("current_stage", "init"),
            progress_percentage=data.get("progress_percentage", 0.0),
            last_error=data.get("last_error"),
            retry_count=data.get("retry_count", 0),
        )
