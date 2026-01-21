"""Body Writer Agent - Research paper body generation."""

from typing import Any

from src.agents.base import BaseAgent, AgentResult
from src.models.paper import PaperOutline, PaperDraft, SectionType
from src.models.source import Source


class BodyWriterAgent(BaseAgent):
    """Agent responsible for writing the research paper body.

    This agent:
    - Writes theoretical framework section
    - Writes research methodology section
    - Writes comprehensive literature review
    - Writes analysis/findings section
    - Maintains active voice throughout
    - Generates content between 15,000-22,000 words
    - Includes proper in-text citations
    """

    name = "body_writer"

    system_prompt = """You are an expert academic writer specializing in research papers. Your writing is characterized by:

1. Clear, precise academic prose
2. Active voice (avoid passive constructions)
3. Logical flow of arguments
4. Proper integration of sources and citations
5. Critical analysis rather than mere description
6. Coherent paragraph structure
7. Smooth transitions between ideas

When writing:
- Always use in-text citations in the format (Author, Year)
- Build arguments progressively
- Support claims with evidence from sources
- Maintain objectivity while presenting analysis
- Use discipline-appropriate terminology
- Ensure each paragraph has a clear purpose"""

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the body writer's tasks.

        Kwargs:
            action: "write_section", "write_all_sections"
            section_type: Type of section to write
            outline: Paper outline
            sources: Available sources
            draft: Existing draft (for continuation)

        Returns:
            AgentResult with written content
        """
        action = kwargs.get("action", "write_all_sections")

        if action == "write_section":
            section_type = kwargs.get("section_type")
            outline = kwargs.get("outline")
            sources = kwargs.get("sources", [])
            return await self._write_section(section_type, outline, sources)
        elif action == "write_all_sections":
            outline = kwargs.get("outline")
            sources = kwargs.get("sources", [])
            target_words = kwargs.get("target_words", 18000)
            return await self._write_all_sections(outline, sources, target_words)
        else:
            return AgentResult(success=False, error=f"Unknown action: {action}")

    async def _write_section(
        self,
        section_type: SectionType,
        outline: PaperOutline,
        sources: list[Source],
    ) -> AgentResult:
        """Write a single section of the paper."""
        # Find the section in the outline
        section = next(
            (s for s in outline.sections if s.section_type == section_type),
            None
        )

        if not section:
            return AgentResult(
                success=False,
                error=f"Section {section_type} not found in outline",
            )

        self.log_info(f"Writing section: {section.title} ({section.target_words} words)")

        # Get relevant sources
        relevant_sources = self._get_relevant_sources(sources, section_type)

        sources_context = self._format_sources_for_prompt(relevant_sources)

        prompt = self._get_section_prompt(section_type, section, sources_context, outline)

        content = await self.generate(prompt, max_tokens=section.target_words * 2)

        # Update section content
        section.content = content
        section.word_count = len(content.split())

        return AgentResult(
            success=True,
            data={
                "section_type": section_type.value,
                "content": content,
                "word_count": section.word_count,
                "target_words": section.target_words,
            },
        )

    async def _write_all_sections(
        self,
        outline: PaperOutline,
        sources: list[Source],
        target_words: int,
    ) -> AgentResult:
        """Write all body sections of the paper."""
        self.log_info(f"Writing all sections (target: {target_words} words)")

        # Create draft
        draft = PaperDraft(
            session_id=self.session.id if self.session else None,
        )

        body_sections = [
            SectionType.LITERATURE_REVIEW,
            SectionType.THEORETICAL_FRAMEWORK,
            SectionType.METHODOLOGY,
            SectionType.ANALYSIS,
            SectionType.DISCUSSION,
        ]

        total_words = 0

        for section_type in body_sections:
            result = await self._write_section(section_type, outline, sources)

            if result.success and result.data:
                content = result.data.get("content", "")
                draft.set_section(section_type, content)
                total_words += result.data.get("word_count", 0)
                self.log_info(f"Completed {section_type.value}: {result.data.get('word_count', 0)} words")

        self.log_info(f"Total body words written: {total_words}")

        return AgentResult(
            success=True,
            data={
                "draft": draft,
                "total_words": total_words,
                "target_words": target_words,
                "sections_written": [s.value for s in body_sections],
            },
        )

    def _get_relevant_sources(
        self, sources: list[Source], section_type: SectionType
    ) -> list[Source]:
        """Get sources relevant to a specific section type."""
        # For now, return all sources - in production, would use mapping
        # from planner agent
        return sources

    def _format_sources_for_prompt(self, sources: list[Source]) -> str:
        """Format sources for inclusion in prompts."""
        formatted = []
        for s in sources[:15]:  # Limit to 15 sources per section
            authors = ", ".join(s.authors[:3]) if s.authors else "Unknown"
            year = s.year or "n.d."
            summary = s.summary[:300] if s.summary else s.abstract[:300] if s.abstract else ""
            formatted.append(f"- {authors} ({year}): {s.title}\n  Summary: {summary}")
        return "\n\n".join(formatted)

    def _get_section_prompt(
        self,
        section_type: SectionType,
        section,
        sources_context: str,
        outline: PaperOutline,
    ) -> str:
        """Get the writing prompt for a specific section type."""
        themes = ", ".join(outline.themes) if outline.themes else "Not specified"
        gaps = ", ".join(outline.research_gaps) if outline.research_gaps else "Not specified"

        prompts = {
            SectionType.LITERATURE_REVIEW: f"""Write a comprehensive Literature Review section for an academic research paper.

Target Length: {section.target_words} words
Research Themes: {themes}
Research Gaps: {gaps}

Available Sources:
{sources_context}

Requirements:
1. Organize the review thematically, not chronologically
2. Synthesize sources - don't just summarize each one separately
3. Identify patterns, agreements, and disagreements in the literature
4. Build toward the research gaps that justify this study
5. Use in-text citations (Author, Year) format
6. Write in active voice
7. End with a clear transition to the theoretical framework

Structure:
- Opening paragraph introducing the scope of the review
- Thematic subsections exploring key concepts
- Critical analysis of methodological approaches
- Identification of gaps and need for current research
- Transition paragraph to next section""",

            SectionType.THEORETICAL_FRAMEWORK: f"""Write a Theoretical Framework section for an academic research paper.

Target Length: {section.target_words} words
Research Themes: {themes}

Available Sources:
{sources_context}

Requirements:
1. Identify and explain the main theories guiding this research
2. Show how theories relate to the research questions
3. Justify the theoretical choices with citations
4. Create a conceptual model if appropriate
5. Use in-text citations (Author, Year) format
6. Write in active voice
7. Connect theory to methodology

Structure:
- Introduction to theoretical approach
- Detailed explanation of primary theory/theories
- Application of theory to current research
- Conceptual framework or model
- Link to methodology""",

            SectionType.METHODOLOGY: f"""Write a Methodology section for an academic research paper.

Target Length: {section.target_words} words

Available Sources:
{sources_context}

Requirements:
1. Describe the research design and approach
2. Explain data collection methods
3. Describe the sample or data sources
4. Explain analytical methods
5. Address validity and reliability
6. Discuss limitations
7. Use active voice
8. Cite methodological sources

Structure:
- Research design overview
- Population and sampling
- Data collection procedures
- Data analysis approach
- Ethical considerations
- Limitations""",

            SectionType.ANALYSIS: f"""Write the Analysis and Findings section for an academic research paper.

Target Length: {section.target_words} words
Research Themes: {themes}

Available Sources:
{sources_context}

Requirements:
1. Present findings systematically
2. Use evidence from sources to support analysis
3. Connect findings to research questions
4. Include critical interpretation
5. Use in-text citations where appropriate
6. Write in active voice
7. Maintain objectivity while providing insight

Structure:
- Overview of findings
- Detailed analysis organized by theme or research question
- Supporting evidence and interpretation
- Unexpected findings or anomalies
- Summary of key findings""",

            SectionType.DISCUSSION: f"""Write the Discussion section for an academic research paper.

Target Length: {section.target_words} words
Research Themes: {themes}
Research Gaps Addressed: {gaps}

Available Sources:
{sources_context}

Requirements:
1. Interpret the significance of findings
2. Compare findings to existing literature
3. Address the research gaps identified earlier
4. Discuss theoretical and practical implications
5. Acknowledge limitations
6. Suggest future research directions
7. Use active voice
8. Use citations to contextualize findings

Structure:
- Summary of key findings
- Interpretation and meaning
- Comparison with existing research
- Implications (theoretical and practical)
- Limitations of the study
- Future research directions""",
        }

        return prompts.get(section_type, f"Write the {section.title} section with {section.target_words} words.")
