"""Source model for academic and web sources."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class SourceType(str, Enum):
    """Type of source."""
    ARXIV = "arxiv"
    WEB = "web"
    BOOK = "book"
    JOURNAL = "journal"


class CredibilityRating(str, Enum):
    """Credibility rating of a source."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Source:
    """An academic or web source."""
    id: UUID = field(default_factory=uuid4)
    session_id: Optional[UUID] = None
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    url: str = ""
    doi: Optional[str] = None
    abstract: str = ""
    full_text: Optional[str] = None
    summary: str = ""
    source_type: SourceType = SourceType.WEB
    relevance_score: float = 0.0
    credibility_rating: CredibilityRating = CredibilityRating.MEDIUM
    is_accessible: bool = True
    retrieved_at: datetime = field(default_factory=datetime.now)

    # Additional metadata
    journal_name: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None

    def get_authors_str(self, max_authors: int = 3) -> str:
        """Get formatted author string."""
        if not self.authors:
            return "Unknown"
        if len(self.authors) <= max_authors:
            if len(self.authors) == 1:
                return self.authors[0]
            return ", ".join(self.authors[:-1]) + f" & {self.authors[-1]}"
        return f"{self.authors[0]} et al."

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id) if self.session_id else None,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "url": self.url,
            "doi": self.doi,
            "abstract": self.abstract,
            "full_text": self.full_text,
            "summary": self.summary,
            "source_type": self.source_type.value,
            "relevance_score": self.relevance_score,
            "credibility_rating": self.credibility_rating.value,
            "is_accessible": self.is_accessible,
            "retrieved_at": self.retrieved_at.isoformat(),
            "journal_name": self.journal_name,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "publisher": self.publisher,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Source":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            session_id=UUID(data["session_id"]) if data.get("session_id") else None,
            title=data["title"],
            authors=data.get("authors", []),
            year=data.get("year"),
            url=data.get("url", ""),
            doi=data.get("doi"),
            abstract=data.get("abstract", ""),
            full_text=data.get("full_text"),
            summary=data.get("summary", ""),
            source_type=SourceType(data.get("source_type", "web")),
            relevance_score=data.get("relevance_score", 0.0),
            credibility_rating=CredibilityRating(data.get("credibility_rating", "medium")),
            is_accessible=data.get("is_accessible", True),
            retrieved_at=datetime.fromisoformat(data["retrieved_at"]) if data.get("retrieved_at") else datetime.now(),
            journal_name=data.get("journal_name"),
            volume=data.get("volume"),
            issue=data.get("issue"),
            pages=data.get("pages"),
            publisher=data.get("publisher"),
        )
