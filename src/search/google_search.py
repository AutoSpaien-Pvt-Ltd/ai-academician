"""Google Custom Search API implementation."""

from dataclasses import dataclass
from typing import Optional

import aiohttp

from src.config import get_config
from src.models.source import Source, SourceType, CredibilityRating
from src.utils.logger import get_logger
from src.utils.retry import retry_async

logger = get_logger(__name__)


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    display_url: str = ""


class GoogleSearchAPI:
    """Google Custom Search API client."""

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self):
        """Initialize the Google Search API client."""
        config = get_config()
        self.api_key = config.search.google_api_key
        self.cse_id = config.search.google_cse_id
        self.max_results = config.search.max_results_per_query

    async def search(
        self,
        query: str,
        num_results: int = 10,
        start_index: int = 1,
    ) -> list[SearchResult]:
        """Search Google for the given query.

        Args:
            query: Search query
            num_results: Number of results to return (max 10 per request)
            start_index: Starting index for pagination

        Returns:
            List of search results
        """
        if not self.api_key or not self.cse_id:
            logger.warning("Google Search API not configured")
            return []

        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(num_results, 10),
            "start": start_index,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            results = []
            for item in data.get("items", []):
                results.append(SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    display_url=item.get("displayLink", ""),
                ))

            return results

        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []

    async def search_academic(
        self,
        query: str,
        num_results: int = 10,
    ) -> list[SearchResult]:
        """Search for academic content.

        Adds academic search modifiers to the query.

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            List of search results
        """
        # Add academic site restrictions
        academic_query = f"{query} site:scholar.google.com OR site:researchgate.net OR site:academia.edu OR site:jstor.org OR site:sciencedirect.com"
        return await self.search(academic_query, num_results)

    async def search_to_sources(
        self,
        query: str,
        num_results: int = 10,
    ) -> list[Source]:
        """Search and convert results to Source objects.

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            List of Source objects
        """
        results = await self.search(query, num_results)
        sources = []

        for result in results:
            # Determine credibility based on domain
            credibility = self._assess_credibility(result.display_url)

            source = Source(
                title=result.title,
                url=result.url,
                abstract=result.snippet,
                source_type=SourceType.WEB,
                credibility_rating=credibility,
                is_accessible=True,
            )
            sources.append(source)

        return sources

    def _assess_credibility(self, domain: str) -> CredibilityRating:
        """Assess the credibility of a source based on its domain."""
        high_credibility_domains = [
            "edu", "gov", "scholar.google.com", "researchgate.net",
            "academia.edu", "jstor.org", "sciencedirect.com", "springer.com",
            "nature.com", "science.org", "ieee.org", "acm.org", "nih.gov",
            "ncbi.nlm.nih.gov", "pubmed.gov",
        ]

        medium_credibility_domains = [
            "wikipedia.org", "britannica.com", "news", "reuters.com",
            "bbc.com", "nytimes.com", "theguardian.com",
        ]

        domain_lower = domain.lower()

        for hc in high_credibility_domains:
            if hc in domain_lower:
                return CredibilityRating.HIGH

        for mc in medium_credibility_domains:
            if mc in domain_lower:
                return CredibilityRating.MEDIUM

        return CredibilityRating.LOW
