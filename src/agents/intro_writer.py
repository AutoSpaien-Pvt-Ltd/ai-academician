"""Intro Writer Agent - Introduction, conclusion, and abstract generation."""

from typing import Any

from src.agents.base import BaseAgent, AgentResult
from src.models.paper import PaperDraft, SectionType


class IntroWriterAgent(BaseAgent):
    """Agent responsible for writing introduction, conclusion, and abstract.

    This agent:
    - Writes introduction that contextualizes the research
    - Writes conclusion summarizing findings and implications
    - Writes abstract (150-300 words) capturing key points
    - Ensures introduction/conclusion align with body content
    """

    name = "intro_writer"

    system_prompt = """You are an expert academic writer specializing in research paper introductions, conclusions, and abstracts.

For Introductions:
- Hook the reader with a compelling opening
- Establish the context and significance
- Present the research problem clearly
- State the research questions/objectives
- Preview the paper's structure
- Use active voice and engaging prose

For Conclusions:
- Summarize key findings without introducing new information
- Connect findings to the research questions
- Discuss implications and significance
- Acknowledge limitations briefly
- Suggest future research
- End with a strong closing statement

For Abstracts:
- Include background, methods, results, and conclusions
- Be concise (150-300 words)
- Use clear, accessible language
- Include keywords for searchability
- Avoid citations in the abstract"""

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the intro writer's tasks.

        Kwargs:
            action: "write_introduction", "write_conclusion", "write_abstract", "write_all"
            draft: The paper draft with body content
            topic: Research topic
            title: Research title

        Returns:
            AgentResult with written content
        """
        action = kwargs.get("action", "write_all")

        if action == "write_introduction":
            draft = kwargs.get("draft")
            title = kwargs.get("title", "")
            topic = kwargs.get("topic", "")
            return await self._write_introduction(draft, title, topic)
        elif action == "write_conclusion":
            draft = kwargs.get("draft")
            return await self._write_conclusion(draft)
        elif action == "write_abstract":
            draft = kwargs.get("draft")
            title = kwargs.get("title", "")
            return await self._write_abstract(draft, title)
        elif action == "write_all":
            draft = kwargs.get("draft")
            title = kwargs.get("title", "")
            topic = kwargs.get("topic", "")
            return await self._write_all(draft, title, topic)
        else:
            return AgentResult(success=False, error=f"Unknown action: {action}")

    async def _write_introduction(
        self, draft: PaperDraft, title: str, topic: str
    ) -> AgentResult:
        """Write the introduction section."""
        self.log_info("Writing introduction")

        # Get body content for context
        body_preview = self._get_body_preview(draft)

        prompt = f"""Write a compelling Introduction for this research paper:

Title: {title}
Topic: {topic}

Paper Body Preview:
{body_preview}

Target Length: 1500-2000 words

Requirements:
1. Start with a hook that captures reader attention
2. Establish the broader context of the research area
3. Narrow down to the specific research problem
4. Clearly state the research gap this paper addresses
5. Present the research questions or objectives
6. Briefly describe the methodology
7. Outline the paper's structure
8. Use active voice throughout
9. Include relevant citations (Author, Year) format

Structure:
- Opening hook and context (2-3 paragraphs)
- Background and significance (2-3 paragraphs)
- Research problem and gap (2-3 paragraphs)
- Research questions/objectives (1 paragraph)
- Methodology overview (1 paragraph)
- Paper structure preview (1 paragraph)"""

        content = await self.generate(prompt, max_tokens=3000)

        draft.set_section(SectionType.INTRODUCTION, content)

        return AgentResult(
            success=True,
            data={
                "section": "introduction",
                "content": content,
                "word_count": len(content.split()),
            },
        )

    async def _write_conclusion(self, draft: PaperDraft) -> AgentResult:
        """Write the conclusion section."""
        self.log_info("Writing conclusion")

        # Get key content from other sections
        analysis = draft.get_section(SectionType.ANALYSIS)[:2000]
        discussion = draft.get_section(SectionType.DISCUSSION)[:2000]
        intro = draft.get_section(SectionType.INTRODUCTION)[:1000]

        prompt = f"""Write a comprehensive Conclusion for this research paper:

Introduction Preview:
{intro}

Analysis Summary:
{analysis}

Discussion Summary:
{discussion}

Target Length: 1000-1500 words

Requirements:
1. Summarize the key findings (without introducing new information)
2. Answer the research questions posed in the introduction
3. Discuss the theoretical contributions
4. Discuss the practical implications
5. Acknowledge key limitations
6. Suggest directions for future research
7. End with a strong, memorable closing statement
8. Use active voice throughout

Structure:
- Restatement of research purpose (1 paragraph)
- Summary of key findings (2-3 paragraphs)
- Theoretical contributions (1-2 paragraphs)
- Practical implications (1-2 paragraphs)
- Limitations (1 paragraph)
- Future research (1 paragraph)
- Closing statement (1 paragraph)"""

        content = await self.generate(prompt, max_tokens=2500)

        draft.set_section(SectionType.CONCLUSION, content)

        return AgentResult(
            success=True,
            data={
                "section": "conclusion",
                "content": content,
                "word_count": len(content.split()),
            },
        )

    async def _write_abstract(self, draft: PaperDraft, title: str) -> AgentResult:
        """Write the abstract."""
        self.log_info("Writing abstract")

        # Get key content from all sections
        intro = draft.get_section(SectionType.INTRODUCTION)[:500]
        methodology = draft.get_section(SectionType.METHODOLOGY)[:500]
        analysis = draft.get_section(SectionType.ANALYSIS)[:500]
        conclusion = draft.get_section(SectionType.CONCLUSION)[:500]

        prompt = f"""Write an Abstract for this research paper:

Title: {title}

Introduction Summary:
{intro}

Methodology Summary:
{methodology}

Findings Summary:
{analysis}

Conclusion Summary:
{conclusion}

Target Length: 250-300 words

Requirements:
1. Include background/context (1-2 sentences)
2. State the research purpose/objectives (1-2 sentences)
3. Describe the methodology briefly (1-2 sentences)
4. Present key findings (3-4 sentences)
5. State conclusions and implications (2-3 sentences)
6. Do NOT include citations
7. Do NOT use first person
8. Be concise and clear
9. Include 4-6 keywords at the end

Format:
[Abstract text]

Keywords: keyword1, keyword2, keyword3, keyword4, keyword5"""

        content = await self.generate(prompt, max_tokens=500)

        draft.set_section(SectionType.ABSTRACT, content)

        return AgentResult(
            success=True,
            data={
                "section": "abstract",
                "content": content,
                "word_count": len(content.split()),
            },
        )

    async def _write_all(
        self, draft: PaperDraft, title: str, topic: str
    ) -> AgentResult:
        """Write introduction, conclusion, and abstract."""
        self.log_info("Writing introduction, conclusion, and abstract")

        # Write introduction first (uses body preview)
        intro_result = await self._write_introduction(draft, title, topic)

        # Write conclusion (uses analysis and discussion)
        conclusion_result = await self._write_conclusion(draft)

        # Write abstract last (uses all sections)
        abstract_result = await self._write_abstract(draft, title)

        total_words = (
            intro_result.data.get("word_count", 0) +
            conclusion_result.data.get("word_count", 0) +
            abstract_result.data.get("word_count", 0)
        )

        return AgentResult(
            success=True,
            data={
                "draft": draft,
                "sections_written": ["introduction", "conclusion", "abstract"],
                "total_words": total_words,
                "introduction_words": intro_result.data.get("word_count", 0),
                "conclusion_words": conclusion_result.data.get("word_count", 0),
                "abstract_words": abstract_result.data.get("word_count", 0),
            },
        )

    def _get_body_preview(self, draft: PaperDraft) -> str:
        """Get a preview of the body content for context."""
        previews = []

        sections = [
            (SectionType.LITERATURE_REVIEW, "Literature Review"),
            (SectionType.THEORETICAL_FRAMEWORK, "Theoretical Framework"),
            (SectionType.METHODOLOGY, "Methodology"),
            (SectionType.ANALYSIS, "Analysis"),
            (SectionType.DISCUSSION, "Discussion"),
        ]

        for section_type, name in sections:
            content = draft.get_section(section_type)
            if content:
                preview = content[:500] + "..." if len(content) > 500 else content
                previews.append(f"**{name}:**\n{preview}")

        return "\n\n".join(previews)
