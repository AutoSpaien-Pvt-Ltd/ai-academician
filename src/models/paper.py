"""Paper draft and outline models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class SectionType(str, Enum):
    """Type of paper section."""
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    LITERATURE_REVIEW = "literature_review"
    THEORETICAL_FRAMEWORK = "theoretical_framework"
    METHODOLOGY = "methodology"
    ANALYSIS = "analysis"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"


class DraftStatus(str, Enum):
    """Status of a paper draft."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"


@dataclass
class PaperSection:
    """A section in the paper outline."""
    title: str
    section_type: SectionType
    target_words: int = 0
    source_ids: list[UUID] = field(default_factory=list)
    subsections: list["PaperSection"] = field(default_factory=list)
    content: str = ""
    word_count: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "section_type": self.section_type.value,
            "target_words": self.target_words,
            "source_ids": [str(sid) for sid in self.source_ids],
            "subsections": [s.to_dict() for s in self.subsections],
            "content": self.content,
            "word_count": self.word_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PaperSection":
        """Create from dictionary."""
        return cls(
            title=data["title"],
            section_type=SectionType(data["section_type"]),
            target_words=data.get("target_words", 0),
            source_ids=[UUID(sid) for sid in data.get("source_ids", [])],
            subsections=[cls.from_dict(s) for s in data.get("subsections", [])],
            content=data.get("content", ""),
            word_count=data.get("word_count", 0),
        )


@dataclass
class PaperOutline:
    """Structured plan for the paper."""
    id: UUID = field(default_factory=uuid4)
    session_id: Optional[UUID] = None
    sections: list[PaperSection] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    research_gaps: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def get_total_target_words(self) -> int:
        """Calculate total target word count."""
        return sum(section.target_words for section in self.sections)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id) if self.session_id else None,
            "sections": [s.to_dict() for s in self.sections],
            "themes": self.themes,
            "research_gaps": self.research_gaps,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PaperOutline":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            session_id=UUID(data["session_id"]) if data.get("session_id") else None,
            sections=[PaperSection.from_dict(s) for s in data.get("sections", [])],
            themes=data.get("themes", []),
            research_gaps=data.get("research_gaps", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )


@dataclass
class PaperDraft:
    """Working version of the paper."""
    id: UUID = field(default_factory=uuid4)
    session_id: Optional[UUID] = None
    version: int = 1
    sections: dict[str, str] = field(default_factory=dict)
    word_count: int = 0
    status: DraftStatus = DraftStatus.DRAFT
    review_cycle: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_section(self, section_type: SectionType) -> str:
        """Get content for a section."""
        return self.sections.get(section_type.value, "")

    def set_section(self, section_type: SectionType, content: str) -> None:
        """Set content for a section."""
        self.sections[section_type.value] = content
        self._update_word_count()
        self.updated_at = datetime.now()

    def _update_word_count(self) -> None:
        """Update total word count."""
        self.word_count = sum(len(content.split()) for content in self.sections.values())

    def get_full_text(self) -> str:
        """Get the complete paper text."""
        section_order = [
            SectionType.ABSTRACT,
            SectionType.INTRODUCTION,
            SectionType.LITERATURE_REVIEW,
            SectionType.THEORETICAL_FRAMEWORK,
            SectionType.METHODOLOGY,
            SectionType.ANALYSIS,
            SectionType.DISCUSSION,
            SectionType.CONCLUSION,
            SectionType.REFERENCES,
        ]
        parts = []
        for section_type in section_order:
            content = self.get_section(section_type)
            if content:
                parts.append(f"## {section_type.value.replace('_', ' ').title()}\n\n{content}")
        return "\n\n".join(parts)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "session_id": str(self.session_id) if self.session_id else None,
            "version": self.version,
            "sections": self.sections,
            "word_count": self.word_count,
            "status": self.status.value,
            "review_cycle": self.review_cycle,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PaperDraft":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]),
            session_id=UUID(data["session_id"]) if data.get("session_id") else None,
            version=data.get("version", 1),
            sections=data.get("sections", {}),
            word_count=data.get("word_count", 0),
            status=DraftStatus(data.get("status", "draft")),
            review_cycle=data.get("review_cycle", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
        )
