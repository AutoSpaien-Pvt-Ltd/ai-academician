"""Chicago citation formatter."""

from src.citations.base import BaseCitationFormatter
from src.config import CitationStyle
from src.models.source import Source


class ChicagoFormatter(BaseCitationFormatter):
    """Chicago Manual of Style citation formatter (Author-Date)."""

    style = CitationStyle.CHICAGO

    def format_in_text(self, source: Source) -> str:
        """Format Chicago in-text citation: (Author Year, page)"""
        if not source.authors:
            author_part = source.title[:20] + "..." if len(source.title) > 20 else source.title
        elif len(source.authors) == 1:
            author_part = self._get_last_name(source.authors[0])
        elif len(source.authors) == 2:
            author_part = f"{self._get_last_name(source.authors[0])} and {self._get_last_name(source.authors[1])}"
        elif len(source.authors) == 3:
            author_part = f"{self._get_last_name(source.authors[0])}, {self._get_last_name(source.authors[1])}, and {self._get_last_name(source.authors[2])}"
        else:
            author_part = f"{self._get_last_name(source.authors[0])} et al."

        year = self._format_year(source.year)

        if source.pages:
            return f"({author_part} {year}, {source.pages.split('-')[0]})"
        return f"({author_part} {year})"

    def format_bibliography(self, source: Source) -> str:
        """Format Chicago bibliography entry."""
        parts = []

        # Authors: Last, First, and First Last.
        if source.authors:
            formatted_authors = self._format_authors_chicago(source.authors)
            parts.append(formatted_authors + ".")
        else:
            parts.append("")

        # Year
        year = self._format_year(source.year)
        parts.append(f"{year}.")

        # Title
        if source.journal_name:
            parts.append(f'"{source.title}."')
        else:
            parts.append(f"*{source.title}*.")

        # Journal
        if source.journal_name:
            journal_part = f"*{source.journal_name}*"
            if source.volume:
                journal_part += f" {source.volume}"
            if source.issue:
                journal_part += f", no. {source.issue}"
            if source.pages:
                journal_part += f": {source.pages}"
            journal_part += "."
            parts.append(journal_part)

        # Publisher (for books)
        if source.publisher and not source.journal_name:
            parts.append(f"{source.publisher}.")

        # DOI or URL
        if source.doi:
            parts.append(f"https://doi.org/{source.doi}.")
        elif source.url:
            parts.append(source.url + ".")

        return " ".join(parts)

    def _format_authors_chicago(self, authors: list[str]) -> str:
        """Format authors for Chicago."""
        if len(authors) == 1:
            return self._format_first_author(authors[0])

        if len(authors) == 2:
            return f"{self._format_first_author(authors[0])}, and {authors[1]}"

        if len(authors) == 3:
            return f"{self._format_first_author(authors[0])}, {authors[1]}, and {authors[2]}"

        if len(authors) <= 10:
            formatted = [self._format_first_author(authors[0])]
            formatted.extend(authors[1:-1])
            formatted.append(f"and {authors[-1]}")
            return ", ".join(formatted)

        # More than 10
        formatted = [self._format_first_author(authors[0])]
        formatted.extend(authors[1:7])
        return ", ".join(formatted) + ", et al"

    def _format_first_author(self, author: str) -> str:
        """Format first author: Last, First."""
        parts = author.strip().split()
        if len(parts) == 0:
            return ""
        if len(parts) == 1:
            return parts[0]

        last_name = parts[-1]
        first_names = " ".join(parts[:-1])
        return f"{last_name}, {first_names}"

    def _get_last_name(self, author: str) -> str:
        """Get last name from author string."""
        parts = author.strip().split()
        return parts[-1] if parts else "Unknown"
