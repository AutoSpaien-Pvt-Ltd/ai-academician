"""arXiv API implementation."""

import asyncio
from datetime import datetime
from typing import Optional

import arxiv

from src.models.source import Source, SourceType, CredibilityRating
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ArxivSearchAPI:
    """arXiv API client for academic paper search."""

    def __init__(self):
        """Initialize the arXiv API client."""
        self._client = arxiv.Client()

    async def search(
        self,
        query: str,
        max_results: int = 20,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
    ) -> list[Source]:
        """Search arXiv for papers matching the query.

        Args:
            query: Search query
            max_results: Maximum number of results
            sort_by: Sort criterion

        Returns:
            List of Source objects
        """
        try:
            # arXiv library is synchronous, run in executor
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_sync,
                query,
                max_results,
                sort_by,
            )
            return results

        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return []

    def _search_sync(
        self,
        query: str,
        max_results: int,
        sort_by: arxiv.SortCriterion,
    ) -> list[Source]:
        """Synchronous search implementation."""
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
        )

        sources = []
        for result in self._client.results(search):
            source = self._result_to_source(result)
            sources.append(source)

        return sources

    def _result_to_source(self, result: arxiv.Result) -> Source:
        """Convert an arXiv result to a Source object."""
        # Extract year from published date
        year = result.published.year if result.published else None

        # Get authors
        authors = [author.name for author in result.authors]

        # Get DOI if available
        doi = None
        if result.doi:
            doi = result.doi

        return Source(
            title=result.title,
            authors=authors,
            year=year,
            url=result.entry_id,
            doi=doi,
            abstract=result.summary,
            source_type=SourceType.ARXIV,
            credibility_rating=CredibilityRating.HIGH,  # arXiv is peer-reviewed
            is_accessible=True,
            # Additional metadata
            journal_name="arXiv",
        )

    async def get_paper_by_id(self, arxiv_id: str) -> Optional[Source]:
        """Get a specific paper by its arXiv ID.

        Args:
            arxiv_id: The arXiv paper ID (e.g., "2301.00001")

        Returns:
            Source object or None if not found
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._get_paper_sync,
                arxiv_id,
            )
            return result

        except Exception as e:
            logger.error(f"Failed to get arXiv paper {arxiv_id}: {e}")
            return None

    def _get_paper_sync(self, arxiv_id: str) -> Optional[Source]:
        """Synchronous implementation of get_paper_by_id."""
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(self._client.results(search))

        if results:
            return self._result_to_source(results[0])
        return None

    async def search_by_category(
        self,
        query: str,
        categories: list[str],
        max_results: int = 20,
    ) -> list[Source]:
        """Search arXiv within specific categories.

        Args:
            query: Search query
            categories: List of arXiv categories (e.g., ["cs.AI", "cs.CL"])
            max_results: Maximum number of results

        Returns:
            List of Source objects
        """
        # Build category query
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        full_query = f"({query}) AND ({cat_query})"

        return await self.search(full_query, max_results)

    async def get_recent_papers(
        self,
        query: str,
        max_results: int = 20,
    ) -> list[Source]:
        """Get recent papers matching the query.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of Source objects sorted by submission date
        """
        return await self.search(
            query,
            max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

    async def download_pdf(self, source: Source, output_dir: str) -> Optional[str]:
        """Download the PDF for a paper.

        Args:
            source: The Source object
            output_dir: Directory to save the PDF

        Returns:
            Path to the downloaded PDF or None if failed
        """
        try:
            # Extract arXiv ID from URL
            arxiv_id = source.url.split("/")[-1]

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._download_pdf_sync,
                arxiv_id,
                output_dir,
            )
            return result

        except Exception as e:
            logger.error(f"Failed to download PDF: {e}")
            return None

    def _download_pdf_sync(self, arxiv_id: str, output_dir: str) -> Optional[str]:
        """Synchronous PDF download."""
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(self._client.results(search))

        if results:
            paper = results[0]
            path = paper.download_pdf(dirpath=output_dir)
            return str(path)
        return None
