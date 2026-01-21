"""LaTeX exporter."""

from pathlib import Path
from typing import Optional
import re

from src.export.base import BaseExporter
from src.models.paper import PaperDraft
from src.models.session import ResearchSession


class LatexExporter(BaseExporter):
    """Export papers to LaTeX format."""

    format_name = "latex"
    file_extension = "tex"

    async def export(
        self,
        draft: PaperDraft,
        session: ResearchSession,
        output_dir: str,
    ) -> Optional[str]:
        """Export the paper to LaTeX format."""
        try:
            output_path = self._get_output_path(session, output_dir)
            self._logger.info(f"Exporting to LaTeX: {output_path}")

            # Generate LaTeX content
            latex_content = self._generate_latex(draft, session)

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)

            # Also generate BibTeX file
            bib_path = output_path.with_suffix('.bib')
            bib_content = self._generate_bibtex(draft, session)
            with open(bib_path, 'w', encoding='utf-8') as f:
                f.write(bib_content)

            self._logger.info(f"LaTeX exported successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            self._logger.error(f"LaTeX export failed: {e}")
            return None

    def _generate_latex(self, draft: PaperDraft, session: ResearchSession) -> str:
        """Generate LaTeX document content."""
        # Escape special characters
        title = self._escape_latex(session.title)

        sections_latex = []

        # Abstract
        if "abstract" in draft.sections:
            abstract = self._escape_latex(draft.sections["abstract"])
            sections_latex.append(f"""
\\begin{{abstract}}
{abstract}
\\end{{abstract}}
""")

        # Main sections
        section_order = [
            ("introduction", "Introduction"),
            ("literature_review", "Literature Review"),
            ("theoretical_framework", "Theoretical Framework"),
            ("methodology", "Methodology"),
            ("analysis", "Analysis and Findings"),
            ("discussion", "Discussion"),
            ("conclusion", "Conclusion"),
        ]

        for key, sec_title in section_order:
            content = draft.sections.get(key, "")
            if content:
                escaped_content = self._escape_latex(content)
                # Convert paragraphs
                paragraphs = escaped_content.split('\n\n')
                formatted_content = '\n\n'.join(p.strip() for p in paragraphs if p.strip())
                sections_latex.append(f"""
\\section{{{sec_title}}}
{formatted_content}
""")

        latex = f"""\\documentclass[12pt,a4paper]{{article}}

% Packages
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{times}}
\\usepackage{{setspace}}
\\usepackage{{geometry}}
\\usepackage{{natbib}}
\\usepackage{{hyperref}}

% Page setup
\\geometry{{margin=2.5cm}}
\\doublespacing

% Citation style based on session
% {session.citation_style.value}
\\bibliographystyle{{{self._get_bib_style(session.citation_style.value)}}}

\\title{{{title}}}
\\author{{}}
\\date{{}}

\\begin{{document}}

\\maketitle

{"".join(sections_latex)}

\\bibliography{{references}}

\\end{{document}}
"""

        return latex

    def _generate_bibtex(self, draft: PaperDraft, session: ResearchSession) -> str:
        """Generate BibTeX bibliography file."""
        # In a full implementation, this would extract citations from the draft
        # and format them properly. For now, return a placeholder.
        bib = """% Bibliography for the research paper
% Add your references here in BibTeX format

% Example:
% @article{example2024,
%   author = {Author, A. and Writer, B.},
%   title = {Example Paper Title},
%   journal = {Journal of Examples},
%   year = {2024},
%   volume = {1},
%   pages = {1--10}
% }
"""
        return bib

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        # Characters that need escaping in LaTeX
        replacements = [
            ('\\', '\\textbackslash{}'),
            ('&', '\\&'),
            ('%', '\\%'),
            ('$', '\\$'),
            ('#', '\\#'),
            ('_', '\\_'),
            ('{', '\\{'),
            ('}', '\\}'),
            ('~', '\\textasciitilde{}'),
            ('^', '\\textasciicircum{}'),
        ]

        for old, new in replacements:
            text = text.replace(old, new)

        return text

    def _get_bib_style(self, citation_style: str) -> str:
        """Get the BibTeX style name for a citation style."""
        style_map = {
            "APA": "apalike",
            "MLA": "plain",
            "CHICAGO": "chicago",
            "IEEE": "IEEEtran",
            "HARVARD": "agsm",
        }
        return style_map.get(citation_style, "plain")
