"""Planner Agent - Research planning and outline creation."""

from typing import Any
from uuid import UUID

from src.agents.base import BaseAgent, AgentResult
from src.models.paper import PaperOutline, PaperSection, SectionType
from src.models.source import Source


class PlannerAgent(BaseAgent):
    """Agent responsible for research planning and paper structure.

    This agent:
    - Analyzes summaries to identify research themes
    - Identifies gaps in existing research
    - Creates structured outline for the research paper
    - Maps sources to relevant sections
    - Prioritizes information based on relevance
    """

    name = "planner"

    system_prompt = """You are an expert research methodology and planning specialist. Your role is to analyze existing research and plan comprehensive research papers.

When planning a research paper:
1. Identify major themes across the literature
2. Find gaps and opportunities for contribution
3. Create a logical structure that builds arguments progressively
4. Ensure balanced coverage of topics
5. Map sources to appropriate sections
6. Consider the target word count for each section

Your outlines should be:
- Logically structured and coherent
- Comprehensive yet focused
- Well-supported by available sources
- Following academic conventions for the discipline"""

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the planner's tasks.

        Kwargs:
            action: "identify_themes", "find_gaps", "create_outline", "map_sources"
            sources: List of summarized sources
            topic: Research topic
            title: Research title
            target_words: Target word count

        Returns:
            AgentResult with themes, gaps, or outline
        """
        action = kwargs.get("action", "create_outline")

        if action == "identify_themes":
            sources = kwargs.get("sources", [])
            return await self._identify_themes(sources)
        elif action == "find_gaps":
            sources = kwargs.get("sources", [])
            topic = kwargs.get("topic", "")
            return await self._find_gaps(sources, topic)
        elif action == "create_outline":
            sources = kwargs.get("sources", [])
            topic = kwargs.get("topic", "")
            title = kwargs.get("title", "")
            target_words = kwargs.get("target_words", 18000)
            return await self._create_outline(sources, topic, title, target_words)
        elif action == "map_sources":
            sources = kwargs.get("sources", [])
            outline = kwargs.get("outline")
            return await self._map_sources_to_sections(sources, outline)
        else:
            return AgentResult(success=False, error=f"Unknown action: {action}")

    async def _identify_themes(self, sources: list[Source]) -> AgentResult:
        """Identify major themes across sources."""
        if not sources:
            return AgentResult(success=False, error="No sources provided")

        summaries = "\n\n".join([
            f"**{s.title}**\n{s.summary[:500]}..."
            for s in sources if s.summary
        ])

        prompt = f"""Analyze these source summaries and identify major themes:

{summaries[:8000]}

Identify 5-7 major themes that emerge across the literature. For each theme:

THEME 1: [Theme Name]
- Description: [Brief description of this theme]
- Key sources: [List 2-3 source titles that address this theme]
- Significance: [Why this theme is important]

THEME 2: ...

Be specific and cite source titles."""

        response = await self.generate(prompt, max_tokens=1500)

        # Parse themes from response
        themes = []
        current_theme = None
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("THEME"):
                if current_theme:
                    themes.append(current_theme)
                theme_name = line.split(":", 1)[1].strip() if ":" in line else ""
                current_theme = {"name": theme_name, "description": "", "sources": [], "significance": ""}
            elif current_theme:
                if line.startswith("- Description:"):
                    current_theme["description"] = line.replace("- Description:", "").strip()
                elif line.startswith("- Key sources:"):
                    current_theme["sources"] = line.replace("- Key sources:", "").strip()
                elif line.startswith("- Significance:"):
                    current_theme["significance"] = line.replace("- Significance:", "").strip()

        if current_theme:
            themes.append(current_theme)

        return AgentResult(
            success=True,
            data={
                "themes": themes,
                "raw_analysis": response,
            },
        )

    async def _find_gaps(
        self, sources: list[Source], topic: str
    ) -> AgentResult:
        """Find research gaps in the literature."""
        summaries = "\n\n".join([
            f"**{s.title}** ({s.year or 'n.d.'})\n{s.summary[:500]}..."
            for s in sources if s.summary
        ])

        prompt = f"""Analyze these sources on "{topic}" and identify research gaps:

{summaries[:8000]}

Identify 3-5 significant research gaps. For each gap:

GAP 1: [Brief title of the gap]
- Current State: What does existing research cover?
- Missing Element: What is not adequately addressed?
- Research Opportunity: How could new research fill this gap?
- Potential Contribution: What value would addressing this gap provide?

GAP 2: ...

Focus on gaps that represent genuine opportunities for contribution."""

        response = await self.generate(prompt, max_tokens=1500)

        # Parse gaps
        gaps = []
        current_gap = None
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("GAP"):
                if current_gap:
                    gaps.append(current_gap)
                gap_name = line.split(":", 1)[1].strip() if ":" in line else ""
                current_gap = {"name": gap_name, "current_state": "", "missing": "", "opportunity": "", "contribution": ""}
            elif current_gap:
                if "Current State" in line:
                    current_gap["current_state"] = line.split(":", 1)[1].strip() if ":" in line else ""
                elif "Missing Element" in line:
                    current_gap["missing"] = line.split(":", 1)[1].strip() if ":" in line else ""
                elif "Research Opportunity" in line:
                    current_gap["opportunity"] = line.split(":", 1)[1].strip() if ":" in line else ""
                elif "Potential Contribution" in line:
                    current_gap["contribution"] = line.split(":", 1)[1].strip() if ":" in line else ""

        if current_gap:
            gaps.append(current_gap)

        return AgentResult(
            success=True,
            data={
                "gaps": gaps,
                "raw_analysis": response,
            },
        )

    async def _create_outline(
        self,
        sources: list[Source],
        topic: str,
        title: str,
        target_words: int,
    ) -> AgentResult:
        """Create a comprehensive paper outline."""
        # First identify themes and gaps
        themes_result = await self._identify_themes(sources)
        gaps_result = await self._find_gaps(sources, topic)

        themes = themes_result.data.get("themes", []) if themes_result.success else []
        gaps = gaps_result.data.get("gaps", []) if gaps_result.success else []

        themes_text = "\n".join([f"- {t['name']}: {t['description']}" for t in themes])
        gaps_text = "\n".join([f"- {g['name']}: {g['missing']}" for g in gaps])

        prompt = f"""Create a detailed paper outline for this research:

Title: {title}
Topic: {topic}
Target Words: {target_words}

Identified Themes:
{themes_text}

Identified Gaps:
{gaps_text}

Create a structured outline with the following sections. For each section, specify:
- Target word count (totaling approximately {target_words} words)
- Key points to cover
- Relevant sources to cite

ABSTRACT (250-300 words)
- Key points: [list main points]

INTRODUCTION (1500-2000 words)
- Key points: [list main points]

LITERATURE REVIEW (4000-5000 words)
- Subsections based on themes
- Key points for each subsection

THEORETICAL FRAMEWORK (2000-2500 words)
- Key points: [list main points]

METHODOLOGY (2000-2500 words)
- Key points: [list main points]

ANALYSIS AND FINDINGS (4000-5000 words)
- Key points: [list main points]

DISCUSSION (2000-2500 words)
- Key points: [list main points]

CONCLUSION (1000-1500 words)
- Key points: [list main points]

REFERENCES
- Estimated count: [number]"""

        response = await self.generate(prompt, max_tokens=3000)

        # Create outline object
        outline = PaperOutline(
            session_id=self.session.id if self.session else None,
            themes=[t["name"] for t in themes],
            research_gaps=[g["name"] for g in gaps],
        )

        # Parse sections from response and create PaperSection objects
        section_configs = [
            (SectionType.ABSTRACT, "Abstract", 300),
            (SectionType.INTRODUCTION, "Introduction", 1750),
            (SectionType.LITERATURE_REVIEW, "Literature Review", 4500),
            (SectionType.THEORETICAL_FRAMEWORK, "Theoretical Framework", 2250),
            (SectionType.METHODOLOGY, "Methodology", 2250),
            (SectionType.ANALYSIS, "Analysis and Findings", 4500),
            (SectionType.DISCUSSION, "Discussion", 2250),
            (SectionType.CONCLUSION, "Conclusion", 1250),
            (SectionType.REFERENCES, "References", 0),
        ]

        for section_type, title, target in section_configs:
            section = PaperSection(
                title=title,
                section_type=section_type,
                target_words=target,
            )
            outline.sections.append(section)

        return AgentResult(
            success=True,
            data={
                "outline": outline,
                "themes": themes,
                "gaps": gaps,
                "detailed_outline": response,
            },
        )

    async def _map_sources_to_sections(
        self, sources: list[Source], outline: PaperOutline
    ) -> AgentResult:
        """Map sources to relevant sections of the outline."""
        source_info = "\n".join([
            f"- {s.id}: {s.title} - {s.summary[:200]}..."
            for s in sources if s.summary
        ])

        sections_info = "\n".join([
            f"- {s.section_type.value}: {s.title}"
            for s in outline.sections
        ])

        prompt = f"""Map these sources to the appropriate sections of the paper:

Sources:
{source_info[:5000]}

Sections:
{sections_info}

For each section, list the source IDs that should be cited there.

Format:
SECTION_NAME: source_id1, source_id2, source_id3

Only include sources that are truly relevant to each section."""

        response = await self.generate(prompt, max_tokens=1500)

        # Parse mappings (simplified - in production would be more robust)
        mappings = {}
        for line in response.split("\n"):
            if ":" in line:
                parts = line.split(":")
                section = parts[0].strip().lower()
                source_ids = [s.strip() for s in parts[1].split(",") if s.strip()]
                mappings[section] = source_ids

        return AgentResult(
            success=True,
            data={
                "mappings": mappings,
                "raw_response": response,
            },
        )
