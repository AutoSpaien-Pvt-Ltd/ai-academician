"""IEEE citation formatter."""

from src.citations.base import BaseCitationFormatter
from src.config import CitationStyle
from src.models.source import Source


class IEEEFormatter(BaseCitationFormatter):
    """IEEE citation formatter (numbered style)."""

    style = CitationStyle.IEEE

    _citation_counter = 0
    _citation_map: dict[str, int] = {}

    def format_in_text(self, source: Source) -> str:
        """Format IEEE in-text citation: [n]"""
        # Get or assign a number for this source
        source_key = str(source.id)
        if source_key not in self._citation_map:
            self._citation_counter += 1
            self._citation_map[source_key] = self._citation_counter

        return f"[{self._citation_map[source_key]}]"

    def format_bibliography(self, source: Source) -> str:
        """Format IEEE reference list entry."""
        parts = []

        # Get citation number
        source_key = str(source.id)
        if source_key in self._citation_map:
            parts.append(f"[{self._citation_map[source_key]}]")
        else:
            self._citation_counter += 1
            self._citation_map[source_key] = self._citation_counter
            parts.append(f"[{self._citation_counter}]")

        # Authors: F. M. Last, F. M. Last, and F. M. Last
        if source.authors:
            formatted_authors = self._format_authors_ieee(source.authors)
            parts.append(formatted_authors + ",")
        else:
            parts.append("")

        # Title
        if source.journal_name:
            parts.append(f'"{source.title},"')
        else:
            parts.append(f"*{source.title}*,")

        # Journal
        if source.journal_name:
            parts.append(f"*{source.journal_name}*,")

        # Volume/Issue
        if source.volume:
            vol_part = f"vol. {source.volume},"
            if source.issue:
                vol_part = f"vol. {source.volume}, no. {source.issue},"
            parts.append(vol_part)

        # Pages
        if source.pages:
            parts.append(f"pp. {source.pages},")

        # Year
        if source.year:
            parts.append(f"{source.year}.")
        else:
            parts[-1] = parts[-1].rstrip(",") + "."

        # DOI
        if source.doi:
            parts.append(f"doi: {source.doi}.")

        return " ".join(parts)

    def _format_authors_ieee(self, authors: list[str]) -> str:
        """Format authors for IEEE: F. M. Last."""
        if len(authors) == 1:
            return self._format_author_ieee(authors[0])

        if len(authors) == 2:
            return f"{self._format_author_ieee(authors[0])} and {self._format_author_ieee(authors[1])}"

        if len(authors) <= 6:
            formatted = [self._format_author_ieee(a) for a in authors[:-1]]
            return ", ".join(formatted) + f", and {self._format_author_ieee(authors[-1])}"

        # More than 6: show first author et al.
        return f"{self._format_author_ieee(authors[0])} *et al.*"

    def _format_author_ieee(self, author: str) -> str:
        """Format single author: F. M. Last."""
        parts = author.strip().split()
        if len(parts) == 0:
            return ""
        if len(parts) == 1:
            return parts[0]

        last_name = parts[-1]
        initials = " ".join(f"{p[0]}." for p in parts[:-1] if p)
        return f"{initials} {last_name}"

    def reset_counter(self) -> None:
        """Reset the citation counter for a new document."""
        self._citation_counter = 0
        self._citation_map = {}
