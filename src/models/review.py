"""Review feedback models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class IssueType(str, Enum):
    """Type of review issue."""
    MISSING_CITATION = "missing_citation"
    INCONSISTENCY = "inconsistency"
    VAGUE_CLAIM = "vague_claim"
    FORMAT_ERROR = "format_error"
    STYLE_ISSUE = "style_issue"
    GRAMMAR_ERROR = "grammar_error"
    LOGIC_ERROR = "logic_error"
    INCOMPLETE_ARGUMENT = "incomplete_argument"


class IssueSeverity(str, Enum):
    """Severity of a review issue."""
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class IssueLocation:
    """Location of an issue in the paper."""
    section: str
    paragraph: int = 0
    text_excerpt: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "section": self.section,
            "paragraph": self.paragraph,
            "text_excerpt": self.text_excerpt,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IssueLocation":
        """Create from dictionary."""
        return cls(
            section=data["section"],
            paragraph=data.get("paragraph", 0),
            text_excerpt=data.get("text_excerpt", ""),
        )


@dataclass
class ReviewIssue:
    """A single issue found during review."""
    id: UUID = field(default_factory=uuid4)
    issue_type: IssueType = IssueType.VAGUE_CLAIM
    severity: IssueSeverity = IssueSeverity.MINOR
    location: IssueLocation = field(default_factory=lambda: IssueLocation(section=""))
    description: str = ""
    suggested_fix: str = ""
    resolved: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "location": self.location.to_dict(),
            "description": self.description,
            "suggested_fix": self.suggested_fix,
            "resolved": self.resolved,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewIssue":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]) if data.get("id") else uuid4(),
            issue_type=IssueType(data.get("issue_type", "vague_claim")),
            severity=IssueSeverity(data.get("severity", "minor")),
            location=IssueLocation.from_dict(data.get("location", {"section": ""})),
            description=data.get("description", ""),
            suggested_fix=data.get("suggested_fix", ""),
            resolved=data.get("resolved", False),
        )


@dataclass
class ReviewFeedback:
    """Complete feedback from a review cycle."""
    id: UUID = field(default_factory=uuid4)
    draft_id: Optional[UUID] = None
    cycle: int = 1
    issues: list[ReviewIssue] = field(default_factory=list)
    overall_assessment: str = ""
    approved: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def get_critical_issues(self) -> list[ReviewIssue]:
        """Get all critical issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.CRITICAL]

    def get_major_issues(self) -> list[ReviewIssue]:
        """Get all major issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.MAJOR]

    def get_unresolved_issues(self) -> list[ReviewIssue]:
        """Get all unresolved issues."""
        return [i for i in self.issues if not i.resolved]

    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return any(i.severity == IssueSeverity.CRITICAL and not i.resolved for i in self.issues)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "draft_id": str(self.draft_id) if self.draft_id else None,
            "cycle": self.cycle,
            "issues": [i.to_dict() for i in self.issues],
            "overall_assessment": self.overall_assessment,
            "approved": self.approved,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewFeedback":
        """Create from dictionary."""
        return cls(
            id=UUID(data["id"]) if data.get("id") else uuid4(),
            draft_id=UUID(data["draft_id"]) if data.get("draft_id") else None,
            cycle=data.get("cycle", 1),
            issues=[ReviewIssue.from_dict(i) for i in data.get("issues", [])],
            overall_assessment=data.get("overall_assessment", ""),
            approved=data.get("approved", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )
