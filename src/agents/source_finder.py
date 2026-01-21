"""Source Finder Agent - Web and academic search."""

from typing import Any, Optional
from uuid import UUID

from src.agents.base import BaseAgent, AgentResult
from src.models.source import Source, SourceType, CredibilityRating
from src.search.google_search import GoogleSearchAPI
from src.search.arxiv_search import ArxivSearchAPI


class SourceFinderAgent(BaseAgent):
    """Agent responsible for finding academic and web sources.

    This agent:
    - Searches Google Custom Search for web sources
    - Searches arXiv for academic papers
    - Filters and ranks results by relevance and credibility
    - Returns minimum 20 sources per research topic
    - Also handles final format review and PDF generation
    """

    name = "source_finder"

    system_prompt = """You are an expert academic research librarian. Your role is to find high-quality, relevant sources for academic research.

When searching for sources:
1. Prioritize peer-reviewed academic papers
2. Include authoritative web sources (educational, governmental)
3. Consider recency and relevance to the topic
4. Evaluate source credibility critically
5. Aim for a diverse range of perspectives and methodologies

For format review:
1. Check that the paper follows academic conventions
2. Verify citation formatting matches the selected style
3. Ensure all sections are properly structured
4. Check for consistency in formatting throughout"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._google_search = GoogleSearchAPI()
        self._arxiv_search = ArxivSearchAPI()

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the source finder's tasks.

        Kwargs:
            action: "search", "expand_search", "format_review"
            topic: Research topic for searching
            sources: Existing sources (for expand_search)
            paper: Paper content (for format_review)

        Returns:
            AgentResult with found sources or review feedback
        """
        action = kwargs.get("action", "search")

        if action == "search":
            topic = kwargs.get("topic", "")
            min_sources = kwargs.get("min_sources", 20)
            return await self._search_sources(topic, min_sources)
        elif action == "expand_search":
            topic = kwargs.get("topic", "")
            existing_sources = kwargs.get("sources", [])
            return await self._expand_search(topic, existing_sources)
        elif action == "format_review":
            paper = kwargs.get("paper", "")
            citation_style = kwargs.get("citation_style", "APA")
            return await self._format_review(paper, citation_style)
        else:
            return AgentResult(success=False, error=f"Unknown action: {action}")

    async def _search_sources(
        self, topic: str, min_sources: int = 20
    ) -> AgentResult:
        """Search for sources on the given topic."""
        if not topic.strip():
            return AgentResult(
                success=False,
                error="No topic provided for search",
            )

        self.log_info(f"Searching for sources on: {topic}")

        all_sources: list[Source] = []

        # Generate search queries
        queries = await self._generate_search_queries(topic)

        # Search arXiv first (higher quality academic sources)
        for query in queries[:3]:  # Use top 3 queries for arXiv
            arxiv_sources = await self._arxiv_search.search(query, max_results=10)
            all_sources.extend(arxiv_sources)
            self.log_info(f"Found {len(arxiv_sources)} arXiv sources for: {query}")

        # Search Google for additional sources
        for query in queries:
            google_sources = await self._google_search.search_to_sources(
                query, num_results=5
            )
            all_sources.extend(google_sources)
            self.log_info(f"Found {len(google_sources)} web sources for: {query}")

        # Deduplicate sources
        unique_sources = self._deduplicate_sources(all_sources)

        # Score and rank sources
        ranked_sources = await self._rank_sources(unique_sources, topic)

        # Ensure we have minimum sources
        if len(ranked_sources) < min_sources:
            self.log_info(
                f"Only found {len(ranked_sources)} sources, expanding search..."
            )
            additional = await self._expand_search(topic, ranked_sources)
            if additional.success and additional.data:
                ranked_sources.extend(additional.data.get("sources", []))

        self.log_info(f"Total sources found: {len(ranked_sources)}")

        return AgentResult(
            success=True,
            data={
                "sources": ranked_sources,
                "total_count": len(ranked_sources),
                "arxiv_count": len([s for s in ranked_sources if s.source_type == SourceType.ARXIV]),
                "web_count": len([s for s in ranked_sources if s.source_type == SourceType.WEB]),
            },
        )

    async def _generate_search_queries(self, topic: str) -> list[str]:
        """Generate multiple search queries from the topic."""
        prompt = f"""Generate 5 different search queries for finding academic sources on this topic:

Topic: "{topic}"

Create queries that:
1. Use different phrasings and synonyms
2. Target different aspects of the topic
3. Include relevant academic keywords
4. Would work well with both academic databases and web search

Format each query on a new line, without numbering or bullets."""

        response = await self.generate(prompt)
        queries = [q.strip() for q in response.split("\n") if q.strip()]

        # Always include the original topic as a query
        if topic not in queries:
            queries.insert(0, topic)

        return queries[:5]

    def _deduplicate_sources(self, sources: list[Source]) -> list[Source]:
        """Remove duplicate sources based on title similarity and URL."""
        seen_urls = set()
        seen_titles = set()
        unique = []

        for source in sources:
            # Normalize URL and title
            url_key = source.url.lower().strip()
            title_key = source.title.lower().strip()[:50]  # First 50 chars

            if url_key not in seen_urls and title_key not in seen_titles:
                seen_urls.add(url_key)
                seen_titles.add(title_key)
                unique.append(source)

        return unique

    async def _rank_sources(
        self, sources: list[Source], topic: str
    ) -> list[Source]:
        """Rank sources by relevance to the topic."""
        if not sources:
            return []

        # Calculate relevance scores
        for source in sources:
            score = 0.0

            # Base score from credibility
            if source.credibility_rating == CredibilityRating.HIGH:
                score += 0.4
            elif source.credibility_rating == CredibilityRating.MEDIUM:
                score += 0.2

            # Bonus for arXiv sources
            if source.source_type == SourceType.ARXIV:
                score += 0.2

            # Bonus for having abstract
            if source.abstract and len(source.abstract) > 100:
                score += 0.1

            # Bonus for recent sources
            if source.year and source.year >= 2020:
                score += 0.1

            # Check keyword match (simple approach)
            topic_words = set(topic.lower().split())
            title_words = set(source.title.lower().split())
            abstract_words = set(source.abstract.lower().split()) if source.abstract else set()

            title_overlap = len(topic_words & title_words) / max(len(topic_words), 1)
            abstract_overlap = len(topic_words & abstract_words) / max(len(topic_words), 1)

            score += title_overlap * 0.2
            score += abstract_overlap * 0.1

            source.relevance_score = min(score, 1.0)

        # Sort by relevance score
        sources.sort(key=lambda s: s.relevance_score, reverse=True)

        return sources

    async def _expand_search(
        self, topic: str, existing_sources: list[Source]
    ) -> AgentResult:
        """Expand search to find more sources."""
        # Generate alternative queries based on existing sources
        prompt = f"""Based on this research topic and existing sources, suggest 3 alternative search queries to find more sources:

Topic: "{topic}"

Existing source titles:
{chr(10).join([f"- {s.title}" for s in existing_sources[:10]])}

Suggest queries that:
1. Explore related but different angles
2. Use different terminology
3. Target gaps in current sources

Format each query on a new line."""

        response = await self.generate(prompt)
        queries = [q.strip() for q in response.split("\n") if q.strip()]

        new_sources = []
        for query in queries[:3]:
            arxiv_sources = await self._arxiv_search.search(query, max_results=5)
            new_sources.extend(arxiv_sources)

        # Deduplicate against existing
        existing_urls = {s.url for s in existing_sources}
        new_sources = [s for s in new_sources if s.url not in existing_urls]

        return AgentResult(
            success=True,
            data={"sources": new_sources, "count": len(new_sources)},
        )

    async def _format_review(
        self, paper: str, citation_style: str
    ) -> AgentResult:
        """Review paper format and structure."""
        prompt = f"""Review this research paper for formatting and structure issues:

Citation Style Required: {citation_style}

Paper Content:
{paper[:5000]}...  # Truncated for analysis

Check for:
1. Proper section structure (Abstract, Introduction, Literature Review, Methodology, Analysis, Conclusion, References)
2. Citation format consistency
3. Academic writing conventions
4. Formatting consistency

Provide a structured review with:
- FORMAT_ISSUES: List any formatting problems
- STRUCTURE_ISSUES: List any structural problems
- CITATION_ISSUES: List any citation format problems
- RECOMMENDATIONS: Specific fixes needed

If the paper passes review, respond with:
APPROVED: [brief summary of quality]"""

        response = await self.generate(prompt, max_tokens=2000)

        if "APPROVED" in response:
            return AgentResult(
                success=True,
                data={
                    "status": "approved",
                    "review": response,
                },
            )
        else:
            # Parse issues from response
            issues = {
                "format_issues": [],
                "structure_issues": [],
                "citation_issues": [],
                "recommendations": [],
            }

            current_section = None
            for line in response.split("\n"):
                line = line.strip()
                if line.startswith("FORMAT_ISSUES"):
                    current_section = "format_issues"
                elif line.startswith("STRUCTURE_ISSUES"):
                    current_section = "structure_issues"
                elif line.startswith("CITATION_ISSUES"):
                    current_section = "citation_issues"
                elif line.startswith("RECOMMENDATIONS"):
                    current_section = "recommendations"
                elif current_section and line.startswith("-"):
                    issues[current_section].append(line[1:].strip())

            return AgentResult(
                success=True,
                data={
                    "status": "needs_revision",
                    "issues": issues,
                    "full_review": response,
                },
            )
