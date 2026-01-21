"""Text processing utilities."""

import re
from typing import Optional


def count_words(text: str) -> int:
    """Count the number of words in text."""
    if not text:
        return 0
    # Split on whitespace and filter empty strings
    words = [w for w in text.split() if w.strip()]
    return len(words)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
    """Extract keywords from text.

    Simple keyword extraction based on word frequency,
    excluding common stop words.

    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return

    Returns:
        List of keywords
    """
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "that", "this", "these", "those", "it", "its", "they", "their",
        "them", "we", "our", "us", "you", "your", "he", "she", "him", "her",
        "his", "hers", "which", "who", "whom", "whose", "what", "where",
        "when", "why", "how", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "not", "only", "same", "so",
        "than", "too", "very", "just", "also", "now", "here", "there",
    }

    # Clean and tokenize
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Count frequencies
    word_freq: dict[str, int] = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:max_keywords]]


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing."""
    if not text:
        return ""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs."""
    if not text:
        return []
    # Split on double newlines or more
    paragraphs = re.split(r'\n\s*\n', text)
    # Clean each paragraph
    return [clean_text(p) for p in paragraphs if clean_text(p)]


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    if not text:
        return []
    # Simple sentence splitting (not perfect but works for most cases)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def extract_sections(text: str) -> dict[str, str]:
    """Extract sections from markdown-formatted text.

    Args:
        text: Markdown text with ## headers

    Returns:
        Dictionary mapping section titles to content
    """
    sections: dict[str, str] = {}
    current_section = ""
    current_content: list[str] = []

    for line in text.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        elif current_section:
            current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def format_authors_apa(authors: list[str]) -> str:
    """Format author names in APA style."""
    if not authors:
        return ""
    if len(authors) == 1:
        return _format_single_author_apa(authors[0])
    if len(authors) == 2:
        return f"{_format_single_author_apa(authors[0])} & {_format_single_author_apa(authors[1])}"
    if len(authors) <= 20:
        formatted = [_format_single_author_apa(a) for a in authors[:-1]]
        return ", ".join(formatted) + f", & {_format_single_author_apa(authors[-1])}"
    # More than 20 authors: show first 19, ..., and last
    formatted = [_format_single_author_apa(a) for a in authors[:19]]
    return ", ".join(formatted) + f", ... {_format_single_author_apa(authors[-1])}"


def _format_single_author_apa(author: str) -> str:
    """Format a single author name in APA style (Last, F. M.)."""
    parts = author.strip().split()
    if len(parts) == 0:
        return ""
    if len(parts) == 1:
        return parts[0]
    # Assume last word is surname
    surname = parts[-1]
    initials = " ".join(f"{p[0]}." for p in parts[:-1] if p)
    return f"{surname}, {initials}"
