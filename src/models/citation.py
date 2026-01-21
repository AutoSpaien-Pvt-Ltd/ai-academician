"""Citation model."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4

from src.config import CitationStyle


@dataclass
class Citation:
    """A formatted citation reference."""
    id: UUID = field(default_factory=uuid4)
    source_id: Optional[UUID] = None
    style: CitationStyle = CitationStyle.APA
    in_text: str = ""
    bibliography: str = ""
    is_complete: bool = True

    # Raw data for re-formatting
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    title: str = ""
    source_title: str = ""  # Journal name, book title, etc.
    url: Optional[str] = None
    doi: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    publisher: Optional[str] = None
    access_date: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "source_id": str(self.source_id) if self.source_id else None,
            "style": self.style.value,
            "in_text": self.in_text,
            "bibliography": self.bibliography,
            "is_complete": self.is_complete,
            "authors": self.authors,
            "year": self.year,
            "title": self.title,
            "source_title": self.source_title,
            "url": self.url,
            "doi": self.doi,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "publisher": self.publisher,
            "access_date": self.access_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Citation":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]) if data.get("id") else uuid4(),
            source_id=UUID(data["source_id"]) if data.get("source_id") else None,
            style=CitationStyle(data.get("style", "APA")),
            in_text=data.get("in_text", ""),
            bibliography=data.get("bibliography", ""),
            is_complete=data.get("is_complete", True),
            authors=data.get("authors", []),
            year=data.get("year"),
            title=data.get("title", ""),
            source_title=data.get("source_title", ""),
            url=data.get("url"),
            doi=data.get("doi"),
            volume=data.get("volume"),
            issue=data.get("issue"),
            pages=data.get("pages"),
            publisher=data.get("publisher"),
            access_date=data.get("access_date"),
        )
