"""Logging configuration for AI Academician."""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

# Global console for rich output
console = Console()


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    rich_output: bool = True,
) -> None:
    """Set up logging configuration."""
    handlers: list[logging.Handler] = []

    if rich_output:
        rich_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
        )
        rich_handler.setLevel(level)
        handlers.append(rich_handler)
    else:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        handlers.append(stream_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


class ProgressTracker:
    """Track and display progress for long-running operations."""

    def __init__(self, description: str = "Processing"):
        self.description = description
        self.current = 0
        self.total = 100
        self._logger = get_logger("progress")

    def update(self, current: int, total: int, message: str = "") -> None:
        """Update progress."""
        self.current = current
        self.total = total
        percentage = (current / total * 100) if total > 0 else 0
        display_msg = f"{self.description}: {percentage:.1f}%"
        if message:
            display_msg += f" - {message}"
        self._logger.info(display_msg)

    def complete(self, message: str = "Complete") -> None:
        """Mark progress as complete."""
        self._logger.info(f"{self.description}: {message}")
