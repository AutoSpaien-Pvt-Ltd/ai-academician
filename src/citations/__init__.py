"""Citation formatting for AI Academician."""

from src.citations.base import BaseCitationFormatter
from src.citations.apa import APAFormatter
from src.citations.mla import MLAFormatter
from src.citations.chicago import ChicagoFormatter
from src.citations.ieee import IEEEFormatter
from src.citations.harvard import HarvardFormatter
from src.config import CitationStyle

__all__ = [
    "BaseCitationFormatter",
    "APAFormatter",
    "MLAFormatter",
    "ChicagoFormatter",
    "IEEEFormatter",
    "HarvardFormatter",
    "get_formatter",
]


def get_formatter(style: CitationStyle) -> BaseCitationFormatter:
    """Get a citation formatter for the specified style.

    Args:
        style: The citation style to use

    Returns:
        A citation formatter instance
    """
    formatters = {
        CitationStyle.APA: APAFormatter,
        CitationStyle.MLA: MLAFormatter,
        CitationStyle.CHICAGO: ChicagoFormatter,
        CitationStyle.IEEE: IEEEFormatter,
        CitationStyle.HARVARD: HarvardFormatter,
    }

    formatter_class = formatters.get(style, APAFormatter)
    return formatter_class()
