"""Harvard citation formatter."""

from src.citations.base import BaseCitationFormatter
from src.config import CitationStyle
from src.models.source import Source


class HarvardFormatter(BaseCitationFormatter):
    """Harvard citation formatter (author-date style)."""

    style = CitationStyle.HARVARD

    def format_in_text(self, source: Source) -> str:
        """Format Harvard in-text citation: (Author Year) or Author (Year)"""
        if not source.authors:
            author_part = source.title[:20] + "..." if len(source.title) > 20 else source.title
        elif len(source.authors) == 1:
            author_part = self._get_last_name(source.authors[0])
        elif len(source.authors) == 2:
            author_part = f"{self._get_last_name(source.authors[0])} and {self._get_last_name(source.authors[1])}"
        else:
            author_part = f"{self._get_last_name(source.authors[0])} et al."

        year = self._format_year(source.year)
        return f"({author_part} {year})"

    def format_bibliography(self, source: Source) -> str:
        """Format Harvard reference list entry."""
        parts = []

        # Authors: Last, F.M.
        if source.authors:
            formatted_authors = self._format_authors_harvard(source.authors)
            parts.append(formatted_authors)
        else:
            parts.append("")

        # Year
        year = self._format_year(source.year)
        parts.append(f"({year})")

        # Title
        if source.journal_name:
            parts.append(f"'{source.title}',")
        else:
            parts.append(f"*{source.title}*,")

        # Journal
        if source.journal_name:
            journal_part = f"*{source.journal_name}*"
            if source.volume:
                journal_part += f", vol. {source.volume}"
            if source.issue:
                journal_part += f", no. {source.issue}"
            if source.pages:
                journal_part += f", pp. {source.pages}"
            parts.append(journal_part + ".")

        # Publisher (for books)
        if source.publisher and not source.journal_name:
            parts.append(f"{source.publisher}.")

        # Availability (DOI or URL)
        if source.doi:
            parts.append(f"Available at: https://doi.org/{source.doi}")
        elif source.url:
            parts.append(f"Available at: {source.url}")

        return " ".join(parts)

    def _format_authors_harvard(self, authors: list[str]) -> str:
        """Format authors for Harvard: Last, F.M."""
        if len(authors) == 1:
            return self._format_author_harvard(authors[0])

        if len(authors) == 2:
            return f"{self._format_author_harvard(authors[0])} and {self._format_author_harvard(authors[1])}"

        if len(authors) == 3:
            return f"{self._format_author_harvard(authors[0])}, {self._format_author_harvard(authors[1])} and {self._format_author_harvard(authors[2])}"

        # More than 3: first author et al.
        return f"{self._format_author_harvard(authors[0])} et al."

    def _format_author_harvard(self, author: str) -> str:
        """Format single author: Last, F.M."""
        parts = author.strip().split()
        if len(parts) == 0:
            return ""
        if len(parts) == 1:
            return parts[0]

        last_name = parts[-1]
        initials = "".join(f"{p[0]}." for p in parts[:-1] if p)
        return f"{last_name}, {initials}"

    def _get_last_name(self, author: str) -> str:
        """Get last name from author string."""
        parts = author.strip().split()
        return parts[-1] if parts else "Unknown"
