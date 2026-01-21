"""Base citation formatter class."""

from abc import ABC, abstractmethod
from typing import Optional

from src.models.source import Source
from src.models.citation import Citation
from src.config import CitationStyle


class BaseCitationFormatter(ABC):
    """Base class for citation formatters."""

    style: CitationStyle = CitationStyle.APA

    @abstractmethod
    def format_in_text(self, source: Source) -> str:
        """Format an in-text citation.

        Args:
            source: The source to cite

        Returns:
            Formatted in-text citation string
        """
        pass

    @abstractmethod
    def format_bibliography(self, source: Source) -> str:
        """Format a bibliography entry.

        Args:
            source: The source to format

        Returns:
            Formatted bibliography entry
        """
        pass

    def create_citation(self, source: Source) -> Citation:
        """Create a complete Citation object from a Source.

        Args:
            source: The source to create a citation for

        Returns:
            Citation object with formatted strings
        """
        in_text = self.format_in_text(source)
        bibliography = self.format_bibliography(source)

        is_complete = all([
            source.title,
            source.authors,
            source.year,
        ])

        return Citation(
            source_id=source.id,
            style=self.style,
            in_text=in_text,
            bibliography=bibliography,
            is_complete=is_complete,
            authors=source.authors,
            year=source.year,
            title=source.title,
            source_title=source.journal_name or "",
            url=source.url,
            doi=source.doi,
            volume=source.volume,
            issue=source.issue,
            pages=source.pages,
            publisher=source.publisher,
        )

    def format_authors(
        self,
        authors: list[str],
        max_authors: int = 3,
        et_al: bool = True,
    ) -> str:
        """Format author names.

        Args:
            authors: List of author names
            max_authors: Maximum authors to show before et al.
            et_al: Whether to use et al. for many authors

        Returns:
            Formatted author string
        """
        if not authors:
            return "Unknown"

        if len(authors) == 1:
            return self._format_single_author(authors[0])

        if len(authors) == 2:
            return f"{self._format_single_author(authors[0])} & {self._format_single_author(authors[1])}"

        if len(authors) <= max_authors or not et_al:
            formatted = [self._format_single_author(a) for a in authors[:-1]]
            return ", ".join(formatted) + f", & {self._format_single_author(authors[-1])}"

        return f"{self._format_single_author(authors[0])} et al."

    def _format_single_author(self, author: str) -> str:
        """Format a single author name. Override in subclasses."""
        return author

    def _format_year(self, year: Optional[int]) -> str:
        """Format the year."""
        return str(year) if year else "n.d."
