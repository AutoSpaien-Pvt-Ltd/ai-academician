"""Base exporter class."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from src.models.paper import PaperDraft
from src.models.session import ResearchSession
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseExporter(ABC):
    """Base class for paper exporters."""

    format_name: str = "base"
    file_extension: str = ""

    def __init__(self):
        """Initialize the exporter."""
        self._logger = get_logger(f"export.{self.format_name}")

    @abstractmethod
    async def export(
        self,
        draft: PaperDraft,
        session: ResearchSession,
        output_dir: str,
    ) -> Optional[str]:
        """Export the paper to the target format.

        Args:
            draft: The paper draft to export
            session: The research session with metadata
            output_dir: Directory to save the export

        Returns:
            Path to the exported file, or None if export failed
        """
        pass

    def _get_output_path(self, session: ResearchSession, output_dir: str) -> Path:
        """Generate the output file path."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create filename from title
        safe_title = "".join(
            c if c.isalnum() or c in " -_" else "_"
            for c in session.title[:50]
        ).strip()
        safe_title = safe_title.replace(" ", "_")

        filename = f"{safe_title}.{self.file_extension}"
        return output_path / filename

    def _format_paper_content(self, draft: PaperDraft, session: ResearchSession) -> str:
        """Format the paper content for export."""
        sections = []

        # Title
        sections.append(f"# {session.title}\n")

        # Abstract
        abstract = draft.get_section(draft.sections.get("abstract", ""))
        if "abstract" in draft.sections:
            sections.append(f"## Abstract\n\n{draft.sections['abstract']}\n")

        # Main sections
        section_order = [
            ("introduction", "Introduction"),
            ("literature_review", "Literature Review"),
            ("theoretical_framework", "Theoretical Framework"),
            ("methodology", "Methodology"),
            ("analysis", "Analysis and Findings"),
            ("discussion", "Discussion"),
            ("conclusion", "Conclusion"),
            ("references", "References"),
        ]

        for key, title in section_order:
            content = draft.sections.get(key, "")
            if content:
                sections.append(f"## {title}\n\n{content}\n")

        return "\n".join(sections)
