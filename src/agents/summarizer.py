"""Summarizer Agent - Content reading and summarization."""

from typing import Any
import aiohttp

from src.agents.base import BaseAgent, AgentResult
from src.models.source import Source


class SummarizerAgent(BaseAgent):
    """Agent responsible for reading and summarizing sources.

    This agent:
    - Reads and processes content from discovered sources
    - Generates detailed summaries (500-1000 words) for each source
    - Identifies key findings, methodologies, and conclusions
    - Flags sources that are inaccessible
    """

    name = "summarizer"

    system_prompt = """You are an expert academic research analyst. Your role is to read and summarize academic sources with precision and depth.

When summarizing a source:
1. Identify the main thesis or research question
2. Describe the methodology used
3. Highlight key findings and evidence
4. Note limitations or gaps acknowledged by the authors
5. Identify how this source relates to the broader research topic

Your summaries should be:
- Comprehensive (500-1000 words)
- Objective and accurate
- Focused on extractable insights
- Written in academic prose
- Include key quotes where relevant (with page numbers if available)"""

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the summarizer's tasks.

        Kwargs:
            action: "summarize_source", "summarize_all", "identify_findings"
            source: Single source to summarize
            sources: List of sources to summarize
            topic: Research topic for context

        Returns:
            AgentResult with summaries
        """
        action = kwargs.get("action", "summarize_all")

        if action == "summarize_source":
            source = kwargs.get("source")
            topic = kwargs.get("topic", "")
            return await self._summarize_source(source, topic)
        elif action == "summarize_all":
            sources = kwargs.get("sources", [])
            topic = kwargs.get("topic", "")
            return await self._summarize_all(sources, topic)
        elif action == "identify_findings":
            sources = kwargs.get("sources", [])
            return await self._identify_key_findings(sources)
        else:
            return AgentResult(success=False, error=f"Unknown action: {action}")

    async def _summarize_source(
        self, source: Source, topic: str
    ) -> AgentResult:
        """Summarize a single source."""
        if not source:
            return AgentResult(success=False, error="No source provided")

        self.log_info(f"Summarizing: {source.title}")

        # Try to get full content if not available
        content = source.full_text or source.abstract or ""

        if not content:
            # Try to fetch content from URL
            content = await self._fetch_content(source.url)

            if not content:
                source.is_accessible = False
                return AgentResult(
                    success=True,
                    data={
                        "source_id": str(source.id),
                        "title": source.title,
                        "summary": f"[Source inaccessible - only metadata available]\n\nTitle: {source.title}\nAuthors: {', '.join(source.authors)}\nYear: {source.year}",
                        "accessible": False,
                    },
                )

        prompt = f"""Summarize this academic source in 500-1000 words:

Research Topic Context: {topic}

Source Title: {source.title}
Authors: {', '.join(source.authors) if source.authors else 'Unknown'}
Year: {source.year or 'Unknown'}

Content:
{content[:8000]}  # Limit content length

Provide a comprehensive summary that includes:
1. **Main Thesis/Research Question**: What is the primary focus?
2. **Methodology**: How was the research conducted?
3. **Key Findings**: What are the main discoveries or arguments?
4. **Evidence**: What data or examples support the findings?
5. **Limitations**: What gaps or limitations are acknowledged?
6. **Relevance**: How does this relate to the research topic?

Write in academic prose, maintaining objectivity."""

        summary = await self.generate(prompt, max_tokens=1500)

        source.summary = summary

        return AgentResult(
            success=True,
            data={
                "source_id": str(source.id),
                "title": source.title,
                "summary": summary,
                "accessible": True,
            },
        )

    async def _summarize_all(
        self, sources: list[Source], topic: str
    ) -> AgentResult:
        """Summarize all provided sources."""
        if not sources:
            return AgentResult(success=False, error="No sources provided")

        self.log_info(f"Summarizing {len(sources)} sources")

        summaries = []
        accessible_count = 0
        inaccessible_count = 0

        for source in sources:
            result = await self._summarize_source(source, topic)

            if result.success and result.data:
                summaries.append(result.data)
                if result.data.get("accessible", True):
                    accessible_count += 1
                else:
                    inaccessible_count += 1

        return AgentResult(
            success=True,
            data={
                "summaries": summaries,
                "total": len(sources),
                "accessible": accessible_count,
                "inaccessible": inaccessible_count,
            },
        )

    async def _identify_key_findings(
        self, sources: list[Source]
    ) -> AgentResult:
        """Identify key findings across all sources."""
        if not sources:
            return AgentResult(success=False, error="No sources provided")

        # Compile summaries
        summaries_text = "\n\n---\n\n".join([
            f"**{s.title}** ({s.year or 'n.d.'})\n{s.summary}"
            for s in sources if s.summary
        ])

        prompt = f"""Analyze these source summaries and identify key findings across the literature:

{summaries_text[:10000]}

Identify and categorize:

1. **CONSENSUS FINDINGS**: Points where multiple sources agree
2. **CONFLICTING FINDINGS**: Areas of disagreement or debate
3. **METHODOLOGICAL PATTERNS**: Common research approaches used
4. **KEY THEMES**: Recurring topics or concepts
5. **RESEARCH GAPS**: Areas identified as needing more research
6. **EMERGING TRENDS**: New directions or recent developments

For each finding, cite the relevant sources by title."""

        response = await self.generate(prompt, max_tokens=2000)

        return AgentResult(
            success=True,
            data={
                "analysis": response,
                "sources_analyzed": len([s for s in sources if s.summary]),
            },
        )

    async def _fetch_content(self, url: str) -> str:
        """Attempt to fetch content from a URL."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        # Basic HTML stripping (simple approach)
                        import re
                        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
                        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                        text = re.sub(r'<[^>]+>', ' ', text)
                        text = re.sub(r'\s+', ' ', text)
                        return text[:10000]  # Limit content
            return ""
        except Exception as e:
            self.log_debug(f"Failed to fetch {url}: {e}")
            return ""
