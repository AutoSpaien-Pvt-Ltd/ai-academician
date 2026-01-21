"""MLA citation formatter."""

from src.citations.base import BaseCitationFormatter
from src.config import CitationStyle
from src.models.source import Source


class MLAFormatter(BaseCitationFormatter):
    """MLA 9th Edition citation formatter."""

    style = CitationStyle.MLA

    def format_in_text(self, source: Source) -> str:
        """Format MLA in-text citation: (Author Page) or (Author)"""
        if not source.authors:
            author_part = f'"{source.title[:30]}..."' if len(source.title) > 30 else f'"{source.title}"'
        elif len(source.authors) == 1:
            author_part = self._get_last_name(source.authors[0])
        elif len(source.authors) == 2:
            author_part = f"{self._get_last_name(source.authors[0])} and {self._get_last_name(source.authors[1])}"
        else:
            author_part = f"{self._get_last_name(source.authors[0])} et al."

        # MLA uses page numbers if available
        if source.pages:
            return f"({author_part} {source.pages.split('-')[0]})"
        return f"({author_part})"

    def format_bibliography(self, source: Source) -> str:
        """Format MLA Works Cited entry."""
        parts = []

        # Authors: Last, First, and First Last.
        if source.authors:
            formatted_authors = self._format_authors_mla(source.authors)
            parts.append(formatted_authors + ".")
        else:
            parts.append("")  # MLA omits author if unknown

        # Title (in quotes for articles, italicized for books)
        if source.journal_name:
            parts.append(f'"{source.title}."')
        else:
            parts.append(f"*{source.title}*.")

        # Container (journal name)
        if source.journal_name:
            parts.append(f"*{source.journal_name}*,")

        # Version/Volume
        if source.volume:
            vol_part = f"vol. {source.volume}"
            if source.issue:
                vol_part += f", no. {source.issue}"
            vol_part += ","
            parts.append(vol_part)

        # Year
        if source.year:
            parts.append(f"{source.year},")

        # Pages
        if source.pages:
            parts.append(f"pp. {source.pages}.")
        else:
            parts[-1] = parts[-1].rstrip(",") + "."

        # DOI or URL
        if source.doi:
            parts.append(f"doi:{source.doi}.")
        elif source.url:
            parts.append(source.url + ".")

        return " ".join(parts)

    def _format_authors_mla(self, authors: list[str]) -> str:
        """Format authors for MLA."""
        if len(authors) == 1:
            return self._format_first_author_mla(authors[0])

        if len(authors) == 2:
            return f"{self._format_first_author_mla(authors[0])}, and {authors[1]}"

        if len(authors) == 3:
            return f"{self._format_first_author_mla(authors[0])}, {authors[1]}, and {authors[2]}"

        # More than 3: first author et al.
        return f"{self._format_first_author_mla(authors[0])}, et al"

    def _format_first_author_mla(self, author: str) -> str:
        """Format first author: Last, First Middle."""
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
