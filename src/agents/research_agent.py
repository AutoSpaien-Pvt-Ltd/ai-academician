"""Research Agent - User interaction and title formulation."""

from typing import Any, Optional

from src.agents.base import BaseAgent, AgentResult
from src.config import CitationStyle
from src.models.session import ResearchSession


class ResearchAgent(BaseAgent):
    """Agent responsible for user interaction and research topic formulation.

    This agent:
    - Accepts natural language research topics from users
    - Asks clarifying questions when input is ambiguous
    - Generates formal academic titles
    - Collects user preferences (citation style, word count, journal)
    """

    name = "research_agent"

    system_prompt = """You are an expert academic research consultant. Your role is to help researchers formulate precise, academically rigorous research topics and titles.

When a user provides a research topic:
1. Analyze the topic for clarity and specificity
2. If the topic is vague, ask 3-5 targeted clarifying questions about:
   - Specific scope and boundaries
   - Target demographic or population
   - Geographic or temporal focus
   - Research methodology preference
   - Specific variables or factors to study
3. Formulate a formal academic title following conventions:
   - Use clear, descriptive language
   - Include key variables/concepts
   - Consider adding subtitle for methodology or scope
   - Format: "Main Title: Subtitle with Method/Scope"

Always maintain a professional, academic tone. Focus on helping the user achieve publication-ready research."""

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the research agent's tasks.

        Kwargs:
            topic: The initial research topic from user
            user_response: Response to clarifying questions (if any)
            action: "analyze", "clarify", "formulate_title", "collect_preferences"

        Returns:
            AgentResult with analysis, questions, or title
        """
        action = kwargs.get("action", "analyze")
        topic = kwargs.get("topic", "")

        if action == "analyze":
            return await self._analyze_topic(topic)
        elif action == "clarify":
            user_response = kwargs.get("user_response", "")
            return await self._process_clarification(topic, user_response)
        elif action == "formulate_title":
            clarifications = kwargs.get("clarifications", {})
            return await self._formulate_title(topic, clarifications)
        elif action == "collect_preferences":
            return await self._collect_preferences()
        else:
            return AgentResult(success=False, error=f"Unknown action: {action}")

    async def _analyze_topic(self, topic: str) -> AgentResult:
        """Analyze a research topic and determine if clarification is needed."""
        if not topic.strip():
            return await self.request_user_input(
                "Please provide a research topic or question you'd like to explore."
            )

        prompt = f"""Analyze this research topic and determine if it needs clarification:

Topic: "{topic}"

Evaluate the topic for:
1. Specificity (is it focused enough?)
2. Clarity (are the key concepts clear?)
3. Scope (is it achievable for a research paper?)
4. Research potential (can it be researched empirically?)

If the topic is clear and specific enough, respond with:
CLEAR: [brief assessment]

If the topic needs clarification, respond with:
NEEDS_CLARIFICATION
Then list 3-5 specific questions to ask the user, formatted as:
Q1: [question]
Q2: [question]
...

Be specific in your questions - avoid generic questions."""

        response = await self.generate(prompt)

        if "NEEDS_CLARIFICATION" in response:
            # Extract questions
            lines = response.split("\n")
            questions = [
                line.split(": ", 1)[1]
                for line in lines
                if line.strip().startswith("Q")
            ]

            return AgentResult(
                success=True,
                data={
                    "status": "needs_clarification",
                    "questions": questions,
                    "original_topic": topic,
                },
                needs_input=True,
                input_prompt="Please answer the following questions to help refine your research topic:\n\n" +
                             "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)]),
            )
        else:
            return AgentResult(
                success=True,
                data={
                    "status": "clear",
                    "topic": topic,
                    "assessment": response.replace("CLEAR:", "").strip(),
                },
            )

    async def _process_clarification(
        self, original_topic: str, user_response: str
    ) -> AgentResult:
        """Process user's responses to clarifying questions."""
        prompt = f"""Based on the original topic and the user's clarifications, create a refined research topic.

Original Topic: "{original_topic}"

User's Clarifications:
{user_response}

Create a refined, specific research topic that incorporates the user's clarifications.
The topic should be:
- Specific and focused
- Researchable
- Academically rigorous

Respond with just the refined topic, nothing else."""

        refined_topic = await self.generate(prompt)

        return AgentResult(
            success=True,
            data={
                "status": "refined",
                "original_topic": original_topic,
                "refined_topic": refined_topic.strip(),
                "clarifications": user_response,
            },
        )

    async def _formulate_title(
        self, topic: str, clarifications: dict
    ) -> AgentResult:
        """Formulate formal academic titles for the research."""
        context = ""
        if clarifications:
            context = f"\n\nAdditional context from user:\n{clarifications}"

        prompt = f"""Generate 3 formal academic titles for this research topic:

Topic: "{topic}"{context}

Requirements for each title:
1. Follow academic title conventions
2. Be specific and descriptive
3. Include key concepts/variables
4. Consider including a subtitle with methodology or scope
5. Be between 10-20 words

Format:
TITLE 1: [title]
TITLE 2: [title]
TITLE 3: [title]

Also provide a brief explanation of why each title works."""

        response = await self.generate(prompt)

        # Parse titles from response
        titles = []
        for line in response.split("\n"):
            if line.strip().startswith("TITLE"):
                title = line.split(": ", 1)[1].strip() if ": " in line else ""
                if title:
                    titles.append(title)

        return AgentResult(
            success=True,
            data={
                "titles": titles[:3],
                "explanation": response,
                "topic": topic,
            },
        )

    async def _collect_preferences(self) -> AgentResult:
        """Collect user preferences for paper generation."""
        return AgentResult(
            success=True,
            needs_input=True,
            input_prompt="""Please specify your preferences for the research paper:

1. Citation Style: (APA / MLA / Chicago / IEEE / Harvard)
2. Target Word Count: (15000-22000 words recommended)
3. Target Journal (optional): Name of the journal you're targeting
4. Any specific requirements or constraints:

Please provide your preferences.""",
            data={
                "status": "collecting_preferences",
                "available_styles": [s.value for s in CitationStyle],
            },
        )

    async def finalize_topic(
        self,
        topic: str,
        title: str,
        citation_style: CitationStyle,
        word_count: int,
        target_journal: Optional[str] = None,
    ) -> AgentResult:
        """Finalize the research topic and create/update session.

        Args:
            topic: The refined research topic
            title: The selected academic title
            citation_style: Selected citation style
            word_count: Target word count
            target_journal: Optional target journal

        Returns:
            AgentResult with finalized session data
        """
        if self.session:
            self.session.topic = topic
            self.session.title = title
            self.session.citation_style = citation_style
            self.session.target_word_count = word_count
            self.session.target_journal = target_journal

        return AgentResult(
            success=True,
            data={
                "topic": topic,
                "title": title,
                "citation_style": citation_style.value,
                "word_count": word_count,
                "target_journal": target_journal,
                "status": "finalized",
            },
        )
