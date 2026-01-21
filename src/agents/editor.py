"""Editor Agent - Content editing based on review feedback."""

from typing import Any

from src.agents.base import BaseAgent, AgentResult
from src.models.paper import PaperDraft, SectionType
from src.models.review import ReviewFeedback, ReviewIssue, IssueSeverity


class EditorAgent(BaseAgent):
    """Agent responsible for editing the paper based on reviewer feedback.

    This agent:
    - Addresses all issues flagged by Agent 6 (Reviewer)
    - Maintains academic writing style during edits
    - Preserves citations and references during editing
    - Tracks changes between edit iterations
    - Sends edited content back to reviewer for re-review
    """

    name = "editor"

    system_prompt = """You are an expert academic editor. Your role is to improve research papers based on reviewer feedback while maintaining academic integrity.

Editing Guidelines:
1. Address each issue systematically
2. Maintain the author's voice and style
3. Preserve all citations and references
4. Ensure smooth transitions after edits
5. Use active voice
6. Keep academic tone throughout
7. Do not introduce new content not related to fixes
8. Ensure edits don't create new issues

For each edit:
- Fix the specific issue identified
- Ensure the surrounding context still flows well
- Maintain consistency with the rest of the paper"""

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Execute the editor's tasks.

        Kwargs:
            action: "edit", "edit_section", "apply_all_fixes"
            draft: Paper draft to edit
            feedback: Review feedback with issues to address
            issue: Specific issue to address (for single edits)

        Returns:
            AgentResult with edited content
        """
        action = kwargs.get("action", "apply_all_fixes")

        if action == "edit":
            draft = kwargs.get("draft")
            issue = kwargs.get("issue")
            return await self._edit_issue(draft, issue)
        elif action == "edit_section":
            draft = kwargs.get("draft")
            section_type = kwargs.get("section_type")
            issues = kwargs.get("issues", [])
            return await self._edit_section(draft, section_type, issues)
        elif action == "apply_all_fixes":
            draft = kwargs.get("draft")
            feedback = kwargs.get("feedback")
            return await self._apply_all_fixes(draft, feedback)
        else:
            return AgentResult(success=False, error=f"Unknown action: {action}")

    async def _edit_issue(self, draft: PaperDraft, issue: ReviewIssue) -> AgentResult:
        """Edit a single issue in the paper."""
        if not issue.location.section:
            return AgentResult(success=False, error="Issue has no section specified")

        try:
            section_type = SectionType(issue.location.section)
        except ValueError:
            return AgentResult(success=False, error=f"Invalid section: {issue.location.section}")

        content = draft.get_section(section_type)
        if not content:
            return AgentResult(success=False, error=f"Section {section_type.value} is empty")

        prompt = f"""Edit this section to address the following issue:

ISSUE TYPE: {issue.issue_type.value}
SEVERITY: {issue.severity.value}
DESCRIPTION: {issue.description}
LOCATION: {issue.location.text_excerpt}
SUGGESTED FIX: {issue.suggested_fix}

CURRENT CONTENT:
{content}

INSTRUCTIONS:
1. Find and fix the specific issue described
2. Maintain the academic writing style
3. Preserve all existing citations
4. Ensure the edit flows naturally with surrounding text
5. Do not change content unrelated to this issue

Return the COMPLETE edited section."""

        edited_content = await self.generate(prompt, max_tokens=len(content.split()) * 2)

        # Update the draft
        draft.set_section(section_type, edited_content)

        # Mark issue as resolved
        issue.resolved = True

        return AgentResult(
            success=True,
            data={
                "section": section_type.value,
                "issue_id": str(issue.id),
                "edited": True,
                "word_count": len(edited_content.split()),
            },
        )

    async def _edit_section(
        self,
        draft: PaperDraft,
        section_type: SectionType,
        issues: list[ReviewIssue],
    ) -> AgentResult:
        """Edit all issues in a specific section."""
        self.log_info(f"Editing {len(issues)} issues in {section_type.value}")

        content = draft.get_section(section_type)
        if not content:
            return AgentResult(success=False, error=f"Section {section_type.value} is empty")

        # Format all issues for the prompt
        issues_text = "\n\n".join([
            f"""ISSUE {i+1}:
Type: {issue.issue_type.value}
Severity: {issue.severity.value}
Description: {issue.description}
Location: {issue.location.text_excerpt}
Suggested Fix: {issue.suggested_fix}"""
            for i, issue in enumerate(issues)
        ])

        prompt = f"""Edit this section to address ALL of the following issues:

{issues_text}

CURRENT CONTENT:
{content}

INSTRUCTIONS:
1. Address EACH issue listed above
2. Maintain the academic writing style
3. Preserve all existing citations and references
4. Ensure edits flow naturally with surrounding text
5. Do not change content unrelated to these issues
6. Number of issues to fix: {len(issues)}

Return the COMPLETE edited section with all issues addressed."""

        edited_content = await self.generate(prompt, max_tokens=len(content.split()) * 2)

        # Update the draft
        draft.set_section(section_type, edited_content)

        # Mark all issues as resolved
        for issue in issues:
            issue.resolved = True

        return AgentResult(
            success=True,
            data={
                "section": section_type.value,
                "issues_fixed": len(issues),
                "word_count": len(edited_content.split()),
            },
        )

    async def _apply_all_fixes(
        self, draft: PaperDraft, feedback: ReviewFeedback
    ) -> AgentResult:
        """Apply all fixes from the review feedback."""
        self.log_info(f"Applying fixes for {len(feedback.issues)} issues")

        # Group issues by section
        issues_by_section: dict[str, list[ReviewIssue]] = {}
        for issue in feedback.issues:
            if not issue.resolved:
                section = issue.location.section
                if section not in issues_by_section:
                    issues_by_section[section] = []
                issues_by_section[section].append(issue)

        # Sort by severity (critical first, then major, then minor)
        for section_issues in issues_by_section.values():
            section_issues.sort(
                key=lambda x: {
                    IssueSeverity.CRITICAL: 0,
                    IssueSeverity.MAJOR: 1,
                    IssueSeverity.MINOR: 2,
                }.get(x.severity, 3)
            )

        # Edit each section
        sections_edited = []
        total_issues_fixed = 0

        for section_str, issues in issues_by_section.items():
            try:
                section_type = SectionType(section_str)
                result = await self._edit_section(draft, section_type, issues)

                if result.success:
                    sections_edited.append(section_str)
                    total_issues_fixed += len(issues)

            except ValueError:
                self.log_error(f"Unknown section type: {section_str}")
                continue

        # Increment draft version
        draft.version += 1

        return AgentResult(
            success=True,
            data={
                "draft": draft,
                "sections_edited": sections_edited,
                "issues_fixed": total_issues_fixed,
                "draft_version": draft.version,
                "ready_for_review": True,
            },
        )

    async def add_citations(
        self, draft: PaperDraft, section_type: SectionType, citations_to_add: list[dict]
    ) -> AgentResult:
        """Add missing citations to a section."""
        content = draft.get_section(section_type)

        citations_text = "\n".join([
            f"- Near '{c.get('location', '')}': Add citation for {c.get('claim', '')} - suggested: {c.get('citation', '')}"
            for c in citations_to_add
        ])

        prompt = f"""Add the following citations to this section:

CITATIONS TO ADD:
{citations_text}

CURRENT CONTENT:
{content}

INSTRUCTIONS:
1. Add each citation in the appropriate location
2. Use (Author, Year) format
3. Ensure citations fit naturally in the text
4. Do not change content except to add citations

Return the COMPLETE section with citations added."""

        edited_content = await self.generate(prompt, max_tokens=len(content.split()) * 2)

        draft.set_section(section_type, edited_content)

        return AgentResult(
            success=True,
            data={
                "section": section_type.value,
                "citations_added": len(citations_to_add),
            },
        )

    async def improve_clarity(
        self, draft: PaperDraft, section_type: SectionType
    ) -> AgentResult:
        """Improve clarity and readability of a section."""
        content = draft.get_section(section_type)

        prompt = f"""Improve the clarity and readability of this section:

CURRENT CONTENT:
{content}

INSTRUCTIONS:
1. Simplify complex sentences while maintaining academic tone
2. Improve paragraph transitions
3. Clarify vague or ambiguous statements
4. Ensure active voice is used
5. Preserve all citations and references
6. Maintain the original meaning and arguments

Return the COMPLETE improved section."""

        edited_content = await self.generate(prompt, max_tokens=len(content.split()) * 2)

        draft.set_section(section_type, edited_content)

        return AgentResult(
            success=True,
            data={
                "section": section_type.value,
                "improved": True,
                "word_count": len(edited_content.split()),
            },
        )
