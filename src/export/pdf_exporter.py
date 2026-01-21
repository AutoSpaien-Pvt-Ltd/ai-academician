"""PDF exporter using WeasyPrint."""

from pathlib import Path
from typing import Optional

from src.export.base import BaseExporter
from src.models.paper import PaperDraft
from src.models.session import ResearchSession


class PDFExporter(BaseExporter):
    """Export papers to PDF format."""

    format_name = "pdf"
    file_extension = "pdf"

    async def export(
        self,
        draft: PaperDraft,
        session: ResearchSession,
        output_dir: str,
    ) -> Optional[str]:
        """Export the paper to PDF."""
        try:
            from weasyprint import HTML, CSS

            output_path = self._get_output_path(session, output_dir)
            self._logger.info(f"Exporting to PDF: {output_path}")

            # Generate HTML content
            html_content = self._generate_html(draft, session)

            # Create PDF
            html = HTML(string=html_content)
            css = CSS(string=self._get_css())
            html.write_pdf(str(output_path), stylesheets=[css])

            self._logger.info(f"PDF exported successfully: {output_path}")
            return str(output_path)

        except ImportError:
            self._logger.error("WeasyPrint not installed. Install with: pip install weasyprint")
            return None
        except Exception as e:
            self._logger.error(f"PDF export failed: {e}")
            return None

    def _generate_html(self, draft: PaperDraft, session: ResearchSession) -> str:
        """Generate HTML content for PDF conversion."""
        sections_html = []

        # Title page
        sections_html.append(f"""
        <div class="title-page">
            <h1 class="title">{session.title}</h1>
            <p class="metadata">Citation Style: {session.citation_style.value}</p>
            <p class="metadata">Word Count: {draft.word_count}</p>
        </div>
        <div class="page-break"></div>
        """)

        # Abstract
        if "abstract" in draft.sections:
            sections_html.append(f"""
            <section class="abstract">
                <h2>Abstract</h2>
                {self._markdown_to_html(draft.sections["abstract"])}
            </section>
            <div class="page-break"></div>
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
            ("references", "References"),
        ]

        for key, title in section_order:
            content = draft.sections.get(key, "")
            if content:
                sections_html.append(f"""
                <section class="{key}">
                    <h2>{title}</h2>
                    {self._markdown_to_html(content)}
                </section>
                """)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{session.title}</title>
        </head>
        <body>
            {"".join(sections_html)}
        </body>
        </html>
        """

        return html

    def _markdown_to_html(self, text: str) -> str:
        """Convert basic markdown to HTML."""
        import re

        # Convert headers
        text = re.sub(r'^### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)

        # Convert bold and italic
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

        # Convert paragraphs
        paragraphs = text.split('\n\n')
        text = ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())

        return text

    def _get_css(self) -> str:
        """Get CSS styles for the PDF."""
        return """
        @page {
            margin: 2.5cm;
            @bottom-center {
                content: counter(page);
            }
        }

        body {
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 2;
            text-align: justify;
        }

        .title-page {
            text-align: center;
            padding-top: 30%;
        }

        .title {
            font-size: 18pt;
            font-weight: bold;
            margin-bottom: 2em;
        }

        .metadata {
            font-size: 12pt;
            margin: 0.5em 0;
        }

        .page-break {
            page-break-after: always;
        }

        h2 {
            font-size: 14pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }

        h3 {
            font-size: 12pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }

        h4 {
            font-size: 12pt;
            font-style: italic;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }

        p {
            text-indent: 0.5in;
            margin: 0 0 0.5em 0;
        }

        .abstract p {
            text-indent: 0;
        }

        .references p {
            text-indent: -0.5in;
            padding-left: 0.5in;
        }
        """
