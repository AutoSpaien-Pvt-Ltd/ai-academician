"""Orchestrator - Agent workflow coordination."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import UUID

from src.agents import (
    ResearchAgent,
    SourceFinderAgent,
    SummarizerAgent,
    PlannerAgent,
    BodyWriterAgent,
    IntroWriterAgent,
    ReviewerAgent,
    EditorAgent,
)
from src.config import CitationStyle, get_config
from src.models.session import ResearchSession, SessionStatus
from src.models.source import Source
from src.models.paper import PaperDraft, PaperOutline
from src.models.review import ReviewFeedback
from src.utils.logger import get_logger, ProgressTracker

logger = get_logger(__name__)


class WorkflowStage(str, Enum):
    """Stages in the paper generation workflow."""
    INIT = "init"
    TOPIC_REFINEMENT = "topic_refinement"
    SOURCE_DISCOVERY = "source_discovery"
    SOURCE_SUMMARIZATION = "source_summarization"
    RESEARCH_PLANNING = "research_planning"
    BODY_WRITING = "body_writing"
    INTRO_CONCLUSION = "intro_conclusion"
    REVIEW = "review"
    EDITING = "editing"
    FINAL_REVIEW = "final_review"
    EXPORT = "export"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowState:
    """State of the paper generation workflow."""
    session: ResearchSession
    current_stage: WorkflowStage = WorkflowStage.INIT
    sources: list[Source] = field(default_factory=list)
    outline: Optional[PaperOutline] = None
    draft: Optional[PaperDraft] = None
    feedback: Optional[ReviewFeedback] = None
    review_cycle: int = 0
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)

    def update_stage(self, stage: WorkflowStage, progress: float = 0.0) -> None:
        """Update the current stage."""
        self.current_stage = stage
        self.session.update_progress(stage.value, progress)


class Orchestrator:
    """Orchestrates the multi-agent paper generation workflow."""

    def __init__(self, session: Optional[ResearchSession] = None):
        """Initialize the orchestrator.

        Args:
            session: Optional existing session to continue
        """
        self.session = session or ResearchSession()
        self.config = get_config()
        self._progress_callback: Optional[Callable[[str, float], None]] = None
        self._user_input_callback: Optional[Callable[[str], str]] = None

        # Initialize agents
        self._research_agent = ResearchAgent(session=self.session)
        self._source_finder = SourceFinderAgent(session=self.session)
        self._summarizer = SummarizerAgent(session=self.session)
        self._planner = PlannerAgent(session=self.session)
        self._body_writer = BodyWriterAgent(session=self.session)
        self._intro_writer = IntroWriterAgent(session=self.session)
        self._reviewer = ReviewerAgent(session=self.session)
        self._editor = EditorAgent(session=self.session)

        self._state: Optional[WorkflowState] = None

    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Set a callback for progress updates."""
        self._progress_callback = callback

    def set_user_input_callback(self, callback: Callable[[str], str]) -> None:
        """Set a callback for getting user input."""
        self._user_input_callback = callback

    def _report_progress(self, stage: str, progress: float, message: str = "") -> None:
        """Report progress to the callback."""
        if self._progress_callback:
            self._progress_callback(stage, progress)
        logger.info(f"[{stage}] {progress:.0f}% - {message}")

    async def _get_user_input(self, prompt: str) -> str:
        """Get input from the user."""
        if self._user_input_callback:
            return self._user_input_callback(prompt)
        # If no callback, just return empty string (for automated testing)
        logger.warning("No user input callback set, returning empty string")
        return ""

    async def generate_paper(
        self,
        topic: str,
        citation_style: CitationStyle = CitationStyle.APA,
        target_words: int = 18000,
        target_journal: Optional[str] = None,
    ) -> WorkflowState:
        """Generate a complete research paper.

        Args:
            topic: The research topic
            citation_style: Citation style to use
            target_words: Target word count
            target_journal: Optional target journal

        Returns:
            WorkflowState with the final results
        """
        # Initialize state
        self.session.topic = topic
        self.session.citation_style = citation_style
        self.session.target_word_count = target_words
        self.session.target_journal = target_journal
        self.session.status = SessionStatus.IN_PROGRESS

        self._state = WorkflowState(session=self.session)

        try:
            # Stage 1: Topic Refinement
            await self._stage_topic_refinement(topic)

            # Stage 2: Source Discovery
            await self._stage_source_discovery()

            # Stage 3: Source Summarization
            await self._stage_source_summarization()

            # Stage 4: Research Planning
            await self._stage_research_planning()

            # Stage 5: Body Writing
            await self._stage_body_writing()

            # Stage 6: Introduction & Conclusion
            await self._stage_intro_conclusion()

            # Stage 7-9: Review-Edit Loop
            await self._stage_review_edit_loop()

            # Stage 10: Final Review and Export
            await self._stage_final_review()

            self._state.update_stage(WorkflowStage.COMPLETED, 100.0)
            self.session.mark_completed()

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            self._state.error = str(e)
            self._state.update_stage(WorkflowStage.FAILED)
            self.session.mark_failed(str(e))

        return self._state

    async def _stage_topic_refinement(self, topic: str) -> None:
        """Stage 1: Refine the research topic."""
        self._state.update_stage(WorkflowStage.TOPIC_REFINEMENT, 5.0)
        self._report_progress("topic_refinement", 5, "Analyzing research topic")

        # Analyze topic
        result = await self._research_agent.execute(action="analyze", topic=topic)

        if result.needs_input and result.data.get("status") == "needs_clarification":
            # Get user clarification
            questions = result.data.get("questions", [])
            prompt = "Please answer these questions to refine your research topic:\n"
            prompt += "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

            user_response = await self._get_user_input(prompt)

            # Process clarification
            result = await self._research_agent.execute(
                action="clarify",
                topic=topic,
                user_response=user_response,
            )
            topic = result.data.get("refined_topic", topic)

        # Formulate title
        self._report_progress("topic_refinement", 8, "Formulating academic title")
        title_result = await self._research_agent.execute(
            action="formulate_title",
            topic=topic,
            clarifications={},
        )

        titles = title_result.data.get("titles", [topic])
        selected_title = titles[0] if titles else topic

        self.session.title = selected_title
        self._report_progress("topic_refinement", 10, f"Title: {selected_title}")

    async def _stage_source_discovery(self) -> None:
        """Stage 2: Discover sources."""
        self._state.update_stage(WorkflowStage.SOURCE_DISCOVERY, 15.0)
        self._report_progress("source_discovery", 15, "Searching for sources")

        result = await self._source_finder.execute(
            action="search",
            topic=self.session.topic,
            min_sources=self.config.search.min_sources,
        )

        if result.success:
            self._state.sources = result.data.get("sources", [])
            self._report_progress(
                "source_discovery",
                25,
                f"Found {len(self._state.sources)} sources"
            )

    async def _stage_source_summarization(self) -> None:
        """Stage 3: Summarize all sources."""
        self._state.update_stage(WorkflowStage.SOURCE_SUMMARIZATION, 25.0)
        self._report_progress("summarization", 25, "Summarizing sources")

        result = await self._summarizer.execute(
            action="summarize_all",
            sources=self._state.sources,
            topic=self.session.topic,
        )

        if result.success:
            accessible = result.data.get("accessible", 0)
            self._report_progress(
                "summarization",
                35,
                f"Summarized {accessible} sources"
            )

    async def _stage_research_planning(self) -> None:
        """Stage 4: Create research plan and outline."""
        self._state.update_stage(WorkflowStage.RESEARCH_PLANNING, 35.0)
        self._report_progress("planning", 35, "Creating research plan")

        result = await self._planner.execute(
            action="create_outline",
            sources=self._state.sources,
            topic=self.session.topic,
            title=self.session.title,
            target_words=self.session.target_word_count,
        )

        if result.success:
            self._state.outline = result.data.get("outline")
            themes = result.data.get("themes", [])
            gaps = result.data.get("gaps", [])
            self._report_progress(
                "planning",
                40,
                f"Identified {len(themes)} themes and {len(gaps)} research gaps"
            )

    async def _stage_body_writing(self) -> None:
        """Stage 5: Write the paper body."""
        self._state.update_stage(WorkflowStage.BODY_WRITING, 40.0)
        self._report_progress("writing", 40, "Writing paper body")

        result = await self._body_writer.execute(
            action="write_all_sections",
            outline=self._state.outline,
            sources=self._state.sources,
            target_words=self.session.target_word_count,
        )

        if result.success:
            self._state.draft = result.data.get("draft")
            words = result.data.get("total_words", 0)
            self._report_progress("writing", 60, f"Wrote {words} words")

    async def _stage_intro_conclusion(self) -> None:
        """Stage 6: Write introduction, conclusion, and abstract."""
        self._state.update_stage(WorkflowStage.INTRO_CONCLUSION, 60.0)
        self._report_progress("intro_conclusion", 60, "Writing introduction and conclusion")

        result = await self._intro_writer.execute(
            action="write_all",
            draft=self._state.draft,
            title=self.session.title,
            topic=self.session.topic,
        )

        if result.success:
            self._state.draft = result.data.get("draft")
            self._report_progress("intro_conclusion", 70, "Completed introduction and conclusion")

    async def _stage_review_edit_loop(self) -> None:
        """Stage 7-9: Review and edit loop."""
        max_cycles = self.config.paper.max_review_cycles
        min_cycles = self.config.paper.min_review_cycles

        for cycle in range(1, max_cycles + 1):
            self._state.review_cycle = cycle

            # Review
            self._state.update_stage(WorkflowStage.REVIEW, 70.0 + cycle * 5)
            self._report_progress("review", 70 + cycle * 5, f"Review cycle {cycle}")

            review_result = await self._reviewer.execute(
                action="review",
                draft=self._state.draft,
                cycle=cycle,
            )

            if review_result.success:
                self._state.feedback = review_result.data.get("feedback")
                issue_count = review_result.data.get("issue_count", 0)

                self._report_progress(
                    "review",
                    72 + cycle * 5,
                    f"Found {issue_count} issues"
                )

                # Check if approved
                if review_result.data.get("approved") and cycle >= min_cycles:
                    self._report_progress("review", 90, "Paper approved")
                    break

                # Edit to fix issues
                self._state.update_stage(WorkflowStage.EDITING, 75.0 + cycle * 5)
                self._report_progress("editing", 75 + cycle * 5, f"Editing cycle {cycle}")

                edit_result = await self._editor.execute(
                    action="apply_all_fixes",
                    draft=self._state.draft,
                    feedback=self._state.feedback,
                )

                if edit_result.success:
                    self._state.draft = edit_result.data.get("draft")
                    fixed = edit_result.data.get("issues_fixed", 0)
                    self._report_progress("editing", 78 + cycle * 5, f"Fixed {fixed} issues")

        # If we've exhausted cycles without approval
        if not self._state.feedback or not self._state.feedback.approved:
            logger.warning("Maximum review cycles reached, proceeding with current draft")

    async def _stage_final_review(self) -> None:
        """Stage 10: Final review before export."""
        self._state.update_stage(WorkflowStage.FINAL_REVIEW, 90.0)
        self._report_progress("final_review", 90, "Performing final review")

        # Do format review
        paper_text = self._state.draft.get_full_text() if self._state.draft else ""

        result = await self._source_finder.execute(
            action="format_review",
            paper=paper_text,
            citation_style=self.session.citation_style.value,
        )

        if result.success and result.data.get("status") == "approved":
            self._report_progress("final_review", 95, "Format review passed")
        else:
            self._report_progress("final_review", 95, "Format review completed with notes")

    async def export_paper(
        self,
        output_dir: str,
        formats: list[str] = None,
    ) -> dict[str, str]:
        """Export the paper to specified formats.

        Args:
            output_dir: Directory to save exports
            formats: List of formats (pdf, docx, latex)

        Returns:
            Dictionary mapping format to file path
        """
        if formats is None:
            formats = ["pdf", "docx", "latex"]

        from src.export import PDFExporter, DocxExporter, LatexExporter

        paths = {}

        if not self._state or not self._state.draft:
            return paths

        if "pdf" in formats:
            exporter = PDFExporter()
            path = await exporter.export(self._state.draft, self.session, output_dir)
            if path:
                paths["pdf"] = path

        if "docx" in formats:
            exporter = DocxExporter()
            path = await exporter.export(self._state.draft, self.session, output_dir)
            if path:
                paths["docx"] = path

        if "latex" in formats:
            exporter = LatexExporter()
            path = await exporter.export(self._state.draft, self.session, output_dir)
            if path:
                paths["latex"] = path

        return paths
