"""APA 7th Edition citation formatter."""

from typing import Optional

from src.citations.base import BaseCitationFormatter
from src.config import CitationStyle
from src.models.source import Source


class APAFormatter(BaseCitationFormatter):
    """APA 7th Edition citation formatter."""

    style = CitationStyle.APA

    def format_in_text(self, source: Source) -> str:
        """Format APA in-text citation: (Author, Year)"""
        if not source.authors:
            author_part = source.title[:20] + "..." if len(source.title) > 20 else source.title
        elif len(source.authors) == 1:
            author_part = self._get_last_name(source.authors[0])
        elif len(source.authors) == 2:
            author_part = f"{self._get_last_name(source.authors[0])} & {self._get_last_name(source.authors[1])}"
        else:
            author_part = f"{self._get_last_name(source.authors[0])} et al."

        year = self._format_year(source.year)
        return f"({author_part}, {year})"

    def format_bibliography(self, source: Source) -> str:
        """Format APA bibliography entry."""
        parts = []

        # Authors: Last, F. M., & Last, F. M.
        if source.authors:
            formatted_authors = self._format_authors_bib(source.authors)
            parts.append(formatted_authors)
        else:
            parts.append("Unknown Author")

        # Year: (2024).
        year = self._format_year(source.year)
        parts.append(f"({year}).")

        # Title (italicized for books/standalone, regular for articles)
        if source.journal_name:
            parts.append(f"{source.title}.")
        else:
            parts.append(f"*{source.title}*.")

        # Journal/Source info
        if source.journal_name:
            journal_part = f"*{source.journal_name}*"
            if source.volume:
                journal_part += f", *{source.volume}*"
            if source.issue:
                journal_part += f"({source.issue})"
            if source.pages:
                journal_part += f", {source.pages}"
            journal_part += "."
            parts.append(journal_part)

        # DOI or URL
        if source.doi:
            parts.append(f"https://doi.org/{source.doi}")
        elif source.url:
            parts.append(source.url)

        return " ".join(parts)

    def _format_authors_bib(self, authors: list[str]) -> str:
        """Format authors for bibliography."""
        if len(authors) == 1:
            return self._format_author_apa(authors[0])

        if len(authors) == 2:
            return f"{self._format_author_apa(authors[0])}, & {self._format_author_apa(authors[1])}"

        if len(authors) <= 20:
            formatted = [self._format_author_apa(a) for a in authors[:-1]]
            return ", ".join(formatted) + f", & {self._format_author_apa(authors[-1])}"

        # More than 20: first 19, ..., last
        formatted = [self._format_author_apa(a) for a in authors[:19]]
        return ", ".join(formatted) + f", ... {self._format_author_apa(authors[-1])}"

    def _format_author_apa(self, author: str) -> str:
        """Format single author: Last, F. M."""
        parts = author.strip().split()
        if len(parts) == 0:
            return ""
        if len(parts) == 1:
            return parts[0]

        last_name = parts[-1]
        initials = " ".join(f"{p[0]}." for p in parts[:-1] if p)
        return f"{last_name}, {initials}"

    def _get_last_name(self, author: str) -> str:
        """Get last name from author string."""
        parts = author.strip().split()
        return parts[-1] if parts else "Unknown"
