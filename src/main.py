"""CLI entry point for AI Academician."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from src.config import CitationStyle, get_config, Config, set_config
from src.orchestrator import Orchestrator
from src.utils.logger import setup_logging, get_logger

console = Console()
logger = get_logger(__name__)


def print_banner():
    """Print the application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     █████╗ ██╗    █████╗  ██████╗ █████╗ ██████╗ ███████╗    ║
    ║    ██╔══██╗██║   ██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝    ║
    ║    ███████║██║   ███████║██║     ███████║██║  ██║█████╗      ║
    ║    ██╔══██║██║   ██╔══██║██║     ██╔══██║██║  ██║██╔══╝      ║
    ║    ██║  ██║██║   ██║  ██║╚██████╗██║  ██║██████╔╝███████╗    ║
    ║    ╚═╝  ╚═╝╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝    ║
    ║                                                               ║
    ║           AI Academician - Research Paper Generator           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug: bool):
    """AI Academician - Multi-agent research paper writing system."""
    import logging
    setup_logging(level=logging.DEBUG if debug else logging.INFO)


@cli.command()
@click.option('--topic', '-t', help='Research topic')
@click.option('--style', '-s', type=click.Choice(['APA', 'MLA', 'CHICAGO', 'IEEE', 'HARVARD']),
              default='APA', help='Citation style')
@click.option('--words', '-w', type=int, default=18000, help='Target word count')
@click.option('--output', '-o', default='./output', help='Output directory')
@click.option('--format', '-f', multiple=True, default=['pdf', 'docx'],
              help='Export formats (pdf, docx, latex)')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
def generate(topic: Optional[str], style: str, words: int, output: str,
             format: tuple, interactive: bool):
    """Generate a research paper."""
    print_banner()

    if interactive or not topic:
        topic = _interactive_setup()
        if not topic:
            console.print("[red]No topic provided. Exiting.[/red]")
            return

    citation_style = CitationStyle(style)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    console.print(Panel(
        f"[bold]Topic:[/bold] {topic}\n"
        f"[bold]Citation Style:[/bold] {citation_style.value}\n"
        f"[bold]Target Words:[/bold] {words}\n"
        f"[bold]Output:[/bold] {output_path}",
        title="Research Paper Configuration",
    ))

    if not Confirm.ask("Proceed with paper generation?", default=True):
        console.print("[yellow]Generation cancelled.[/yellow]")
        return

    # Run the async generation
    asyncio.run(_run_generation(topic, citation_style, words, output_path, list(format)))


async def _run_generation(topic: str, citation_style: CitationStyle,
                          target_words: int, output_path: Path, formats: list):
    """Run the paper generation process."""
    orchestrator = Orchestrator()

    # Set up progress callback
    def progress_callback(stage: str, progress: float):
        console.print(f"[cyan][{stage}][/cyan] {progress:.0f}% complete")

    # Set up user input callback
    def user_input_callback(prompt: str) -> str:
        console.print(f"\n[yellow]{prompt}[/yellow]\n")
        return Prompt.ask("Your response")

    orchestrator.set_progress_callback(progress_callback)
    orchestrator.set_user_input_callback(user_input_callback)

    console.print("\n[bold green]Starting paper generation...[/bold green]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating research paper...", total=None)

        try:
            state = await orchestrator.generate_paper(
                topic=topic,
                citation_style=citation_style,
                target_words=target_words,
            )

            if state.error:
                console.print(f"\n[red]Error: {state.error}[/red]")
                return

            progress.update(task, description="Exporting paper...")

            # Export to requested formats
            export_paths = await orchestrator.export_paper(
                output_dir=str(output_path),
                formats=formats,
            )

            progress.update(task, description="Complete!")

            console.print("\n[bold green]Paper generation complete![/bold green]\n")

            if export_paths:
                console.print("[bold]Exported files:[/bold]")
                for fmt, path in export_paths.items():
                    console.print(f"  - {fmt.upper()}: {path}")

            # Summary
            if state.draft:
                console.print(f"\n[bold]Total words:[/bold] {state.draft.word_count}")
            if state.sources:
                console.print(f"[bold]Sources used:[/bold] {len(state.sources)}")
            if state.review_cycle:
                console.print(f"[bold]Review cycles:[/bold] {state.review_cycle}")

        except Exception as e:
            console.print(f"\n[red]Error during generation: {e}[/red]")
            logger.exception("Generation failed")


def _interactive_setup() -> Optional[str]:
    """Interactive setup for paper generation."""
    console.print("\n[bold]Welcome to AI Academician![/bold]\n")
    console.print("Let's set up your research paper.\n")

    topic = Prompt.ask("Enter your research topic or question")

    if not topic.strip():
        return None

    console.print(f"\n[green]Topic:[/green] {topic}\n")

    return topic


@cli.command()
def config():
    """Show current configuration."""
    cfg = get_config()

    console.print(Panel(
        f"[bold]Default LLM Provider:[/bold] {cfg.default_provider.value}\n"
        f"[bold]Configured Providers:[/bold] {', '.join(p.value for p in cfg.llm_configs.keys())}\n"
        f"[bold]Min Sources:[/bold] {cfg.search.min_sources}\n"
        f"[bold]Max Sources:[/bold] {cfg.search.max_sources}\n"
        f"[bold]Default Word Count:[/bold] {cfg.paper.default_word_count}\n"
        f"[bold]Default Citation Style:[/bold] {cfg.paper.default_citation_style.value}\n"
        f"[bold]Min Review Cycles:[/bold] {cfg.paper.min_review_cycles}\n"
        f"[bold]Max Review Cycles:[/bold] {cfg.paper.max_review_cycles}",
        title="Configuration",
    ))


@cli.command()
def version():
    """Show version information."""
    from src import __version__
    console.print(f"AI Academician v{__version__}")


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
