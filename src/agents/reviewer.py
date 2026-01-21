"""Reviewer Agent - Quality review and feedback."""

from typing import Any

from src.agents.base import BaseAgent, AgentResult
from src.models.paper import PaperDraft, SectionType
from src.models.review import (
    ReviewFeedback,
    ReviewIssue,
    IssueType,
    IssueSeverity,
    IssueLocation,
)


class ReviewerAgent(BaseAgent):
    """Agent responsible for quality review of research papers.

    This agent:
    - Reviews paper for logical consistency between paragraphs
    - Identifies claims lacking citations or evidence
    - Detects vague statements requiring clarification
    - Verifies footnotes and references are properly formatted
    - Performs minimum 2 review cycles before approval
    - Provides specific, actionable feedback
    - NEVER approves on first review instance
    """

    name = "reviewer"

    system_prompt = """You are a rigorous academic peer reviewer. Your role is to ensure research papers meet publication standards.

Review Criteria:
1. Logical consistency and coherent arguments
2. Proper citation of all claims and statements
3. Clear, unambiguous language
4. Proper academic structure and formatting
5. Evidence-based assertions
6. Smooth transitions between sections
7. Consistent terminology throughout

You are STRICT but CONSTRUCTIVE:
- Always find at least a few issues to improve (especially on first review)
- Be specific about what needs fixing
- Suggest how to fix each issue
- Rate severity appropriately (Critical > Major > Minor)

You NEVER approve a paper on the first review. Always find areas for improvement."""

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the reviewer's tasks.

        Kwargs:
            action: "review", "check_issues", "final_review"
            draft: Paper draft to review
            previous_feedback: Previous review feedback (for re-review)
            cycle: Current review cycle number

        Returns:
            AgentResult with review feedback
        """
        action = kwargs.get("action", "review")

        if action == "review":
            draft = kwargs.get("draft")
            cycle = kwargs.get("cycle", 1)
            return await self._review(draft, cycle)
        elif action == "check_issues":
            draft = kwargs.get("draft")
            previous_feedback = kwargs.get("previous_feedback")
            return await self._check_resolved_issues(draft, previous_feedback)
        elif action == "final_review":
            draft = kwargs.get("draft")
            cycle = kwargs.get("cycle", 2)
            return await self._final_review(draft, cycle)
        else:
            return AgentResult(success=False, error=f"Unknown action: {action}")

    async def _review(self, draft: PaperDraft, cycle: int) -> AgentResult:
        """Perform a full review of the paper."""
        self.log_info(f"Starting review cycle {cycle}")

        feedback = ReviewFeedback(
            draft_id=draft.id,
            cycle=cycle,
        )

        # Review each section
        for section_type in SectionType:
            content = draft.get_section(section_type)
            if content:
                section_issues = await self._review_section(section_type, content, cycle)
                feedback.issues.extend(section_issues)

        # Check cross-section consistency
        consistency_issues = await self._check_consistency(draft)
        feedback.issues.extend(consistency_issues)

        # Generate overall assessment
        feedback.overall_assessment = await self._generate_assessment(draft, feedback.issues, cycle)

        # Determine approval (NEVER on first cycle)
        if cycle < 2:
            feedback.approved = False
            self.log_info("First review cycle - approval not possible")
        else:
            # Check if there are any critical or major unresolved issues
            critical_major = [
                i for i in feedback.issues
                if i.severity in [IssueSeverity.CRITICAL, IssueSeverity.MAJOR] and not i.resolved
            ]
            feedback.approved = len(critical_major) == 0

        draft.review_cycle = cycle

        return AgentResult(
            success=True,
            data={
                "feedback": feedback,
                "issue_count": len(feedback.issues),
                "critical_count": len([i for i in feedback.issues if i.severity == IssueSeverity.CRITICAL]),
                "major_count": len([i for i in feedback.issues if i.severity == IssueSeverity.MAJOR]),
                "minor_count": len([i for i in feedback.issues if i.severity == IssueSeverity.MINOR]),
                "approved": feedback.approved,
                "cycle": cycle,
            },
        )

    async def _review_section(
        self, section_type: SectionType, content: str, cycle: int
    ) -> list[ReviewIssue]:
        """Review a single section for issues."""
        prompt = f"""Review this {section_type.value.replace('_', ' ')} section for academic quality issues:

Content:
{content[:5000]}

{"This is the FIRST review - find areas for improvement. Do not approve yet." if cycle == 1 else "This is review cycle " + str(cycle) + " - check if previous issues were addressed."}

Identify issues in these categories:
1. MISSING_CITATION: Claims or statements that need citation support
2. INCONSISTENCY: Logical inconsistencies or contradictions
3. VAGUE_CLAIM: Vague or unclear statements
4. FORMAT_ERROR: Formatting or structural problems
5. STYLE_ISSUE: Academic writing style problems
6. GRAMMAR_ERROR: Grammar or language issues
7. LOGIC_ERROR: Logical flow problems
8. INCOMPLETE_ARGUMENT: Arguments that need more development

For each issue found, provide:
ISSUE: [category]
SEVERITY: [CRITICAL/MAJOR/MINOR]
LOCATION: [paragraph number or text excerpt]
DESCRIPTION: [what's wrong]
SUGGESTION: [how to fix it]

---

If no issues are found in this section, respond with:
NO_ISSUES: This section meets quality standards."""

        response = await self.generate(prompt, max_tokens=2000)

        issues = []

        if "NO_ISSUES" not in response:
            # Parse issues from response
            current_issue = {}
            for line in response.split("\n"):
                line = line.strip()
                if line.startswith("ISSUE:"):
                    if current_issue:
                        issues.append(self._create_issue(current_issue, section_type))
                    category = line.replace("ISSUE:", "").strip()
                    current_issue = {"category": category}
                elif line.startswith("SEVERITY:"):
                    current_issue["severity"] = line.replace("SEVERITY:", "").strip()
                elif line.startswith("LOCATION:"):
                    current_issue["location"] = line.replace("LOCATION:", "").strip()
                elif line.startswith("DESCRIPTION:"):
                    current_issue["description"] = line.replace("DESCRIPTION:", "").strip()
                elif line.startswith("SUGGESTION:"):
                    current_issue["suggestion"] = line.replace("SUGGESTION:", "").strip()

            if current_issue:
                issues.append(self._create_issue(current_issue, section_type))

        return issues

    def _create_issue(self, data: dict, section_type: SectionType) -> ReviewIssue:
        """Create a ReviewIssue from parsed data."""
        # Map category to IssueType
        category_map = {
            "MISSING_CITATION": IssueType.MISSING_CITATION,
            "INCONSISTENCY": IssueType.INCONSISTENCY,
            "VAGUE_CLAIM": IssueType.VAGUE_CLAIM,
            "FORMAT_ERROR": IssueType.FORMAT_ERROR,
            "STYLE_ISSUE": IssueType.STYLE_ISSUE,
            "GRAMMAR_ERROR": IssueType.GRAMMAR_ERROR,
            "LOGIC_ERROR": IssueType.LOGIC_ERROR,
            "INCOMPLETE_ARGUMENT": IssueType.INCOMPLETE_ARGUMENT,
        }

        # Map severity
        severity_map = {
            "CRITICAL": IssueSeverity.CRITICAL,
            "MAJOR": IssueSeverity.MAJOR,
            "MINOR": IssueSeverity.MINOR,
        }

        return ReviewIssue(
            issue_type=category_map.get(data.get("category", ""), IssueType.VAGUE_CLAIM),
            severity=severity_map.get(data.get("severity", "MINOR"), IssueSeverity.MINOR),
            location=IssueLocation(
                section=section_type.value,
                text_excerpt=data.get("location", ""),
            ),
            description=data.get("description", ""),
            suggested_fix=data.get("suggestion", ""),
        )

    async def _check_consistency(self, draft: PaperDraft) -> list[ReviewIssue]:
        """Check for cross-section consistency issues."""
        intro = draft.get_section(SectionType.INTRODUCTION)[:1000]
        conclusion = draft.get_section(SectionType.CONCLUSION)[:1000]
        abstract = draft.get_section(SectionType.ABSTRACT)

        prompt = f"""Check for consistency between these paper sections:

ABSTRACT:
{abstract}

INTRODUCTION (first 1000 chars):
{intro}

CONCLUSION (first 1000 chars):
{conclusion}

Check for:
1. Claims in abstract that aren't supported in conclusion
2. Research questions in intro not addressed in conclusion
3. Contradictions between sections
4. Terminology inconsistencies

If inconsistencies found:
INCONSISTENCY: [description]
SECTIONS: [which sections are inconsistent]
SUGGESTION: [how to fix]

If consistent, respond: CONSISTENT: Sections are aligned."""

        response = await self.generate(prompt, max_tokens=1000)

        issues = []
        if "INCONSISTENCY:" in response:
            for line in response.split("\n"):
                if line.startswith("INCONSISTENCY:"):
                    issues.append(ReviewIssue(
                        issue_type=IssueType.INCONSISTENCY,
                        severity=IssueSeverity.MAJOR,
                        location=IssueLocation(section="cross-section"),
                        description=line.replace("INCONSISTENCY:", "").strip(),
                    ))

        return issues

    async def _generate_assessment(
        self, draft: PaperDraft, issues: list[ReviewIssue], cycle: int
    ) -> str:
        """Generate overall assessment of the paper."""
        critical = len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
        major = len([i for i in issues if i.severity == IssueSeverity.MAJOR])
        minor = len([i for i in issues if i.severity == IssueSeverity.MINOR])

        assessment = f"""Review Cycle {cycle} Assessment:

Total Issues Found: {len(issues)}
- Critical: {critical}
- Major: {major}
- Minor: {minor}

"""
        if cycle == 1:
            assessment += "This is the first review cycle. The paper requires revisions before it can be approved. "
        elif critical > 0:
            assessment += "The paper has critical issues that must be addressed before approval. "
        elif major > 0:
            assessment += "The paper has major issues that should be addressed. "
        else:
            assessment += "The paper is nearing publication readiness with only minor issues remaining. "

        return assessment

    async def _check_resolved_issues(
        self, draft: PaperDraft, previous_feedback: ReviewFeedback
    ) -> AgentResult:
        """Check if previously identified issues have been resolved."""
        resolved_count = 0
        for issue in previous_feedback.issues:
            section_content = draft.get_section(SectionType(issue.location.section)) if issue.location.section in [s.value for s in SectionType] else ""

            if issue.location.text_excerpt and issue.location.text_excerpt not in section_content:
                issue.resolved = True
                resolved_count += 1

        return AgentResult(
            success=True,
            data={
                "total_issues": len(previous_feedback.issues),
                "resolved": resolved_count,
                "remaining": len(previous_feedback.issues) - resolved_count,
            },
        )

    async def _final_review(self, draft: PaperDraft, cycle: int) -> AgentResult:
        """Perform a final quality check before approval."""
        self.log_info(f"Performing final review (cycle {cycle})")

        # Do a thorough review
        result = await self._review(draft, cycle)

        if result.success and result.data:
            feedback = result.data["feedback"]

            # For final review, only block on critical issues
            if not feedback.has_critical_issues() and cycle >= 2:
                feedback.approved = True
                feedback.overall_assessment += "\n\nFINAL REVIEW: Paper approved for finalization."

            result.data["feedback"] = feedback
            result.data["approved"] = feedback.approved

        return result
