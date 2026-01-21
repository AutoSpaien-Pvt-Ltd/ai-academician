"""File manager for artifact storage."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from src.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """Manages file artifacts for AI Academician."""

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize the file manager.

        Args:
            base_dir: Base directory for file storage
        """
        if base_dir is None:
            config = get_config()
            base_dir = config.storage.output_dir

        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_session_dir(self, session_id: UUID) -> Path:
        """Get the directory for a session's files."""
        session_dir = self.base_dir / str(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def save_json(self, session_id: UUID, filename: str, data: dict) -> Path:
        """Save data as JSON.

        Args:
            session_id: Session ID
            filename: Filename (without extension)
            data: Data to save

        Returns:
            Path to the saved file
        """
        session_dir = self.get_session_dir(session_id)
        filepath = session_dir / f"{filename}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.debug(f"Saved JSON: {filepath}")
        return filepath

    def load_json(self, session_id: UUID, filename: str) -> Optional[dict]:
        """Load JSON data.

        Args:
            session_id: Session ID
            filename: Filename (without extension)

        Returns:
            Loaded data or None if not found
        """
        session_dir = self.get_session_dir(session_id)
        filepath = session_dir / f"{filename}.json"

        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_text(self, session_id: UUID, filename: str, content: str) -> Path:
        """Save text content.

        Args:
            session_id: Session ID
            filename: Filename with extension
            content: Text content

        Returns:
            Path to the saved file
        """
        session_dir = self.get_session_dir(session_id)
        filepath = session_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.debug(f"Saved text: {filepath}")
        return filepath

    def load_text(self, session_id: UUID, filename: str) -> Optional[str]:
        """Load text content.

        Args:
            session_id: Session ID
            filename: Filename with extension

        Returns:
            Text content or None if not found
        """
        session_dir = self.get_session_dir(session_id)
        filepath = session_dir / filename

        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def save_binary(self, session_id: UUID, filename: str, data: bytes) -> Path:
        """Save binary data.

        Args:
            session_id: Session ID
            filename: Filename with extension
            data: Binary data

        Returns:
            Path to the saved file
        """
        session_dir = self.get_session_dir(session_id)
        filepath = session_dir / filename

        with open(filepath, 'wb') as f:
            f.write(data)

        logger.debug(f"Saved binary: {filepath}")
        return filepath

    def list_files(self, session_id: UUID, pattern: str = "*") -> list[Path]:
        """List files in a session directory.

        Args:
            session_id: Session ID
            pattern: Glob pattern

        Returns:
            List of file paths
        """
        session_dir = self.get_session_dir(session_id)
        return list(session_dir.glob(pattern))

    def delete_file(self, session_id: UUID, filename: str) -> bool:
        """Delete a file.

        Args:
            session_id: Session ID
            filename: Filename

        Returns:
            True if deleted, False if not found
        """
        session_dir = self.get_session_dir(session_id)
        filepath = session_dir / filename

        if filepath.exists():
            filepath.unlink()
            logger.debug(f"Deleted: {filepath}")
            return True
        return False

    def delete_session_files(self, session_id: UUID) -> bool:
        """Delete all files for a session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        session_dir = self.base_dir / str(session_id)

        if session_dir.exists():
            shutil.rmtree(session_dir)
            logger.debug(f"Deleted session directory: {session_dir}")
            return True
        return False

    def get_export_path(self, session_id: UUID, format: str, title: str) -> Path:
        """Get the export path for a paper.

        Args:
            session_id: Session ID
            format: Export format (pdf, docx, tex)
            title: Paper title

        Returns:
            Path for the export file
        """
        session_dir = self.get_session_dir(session_id)

        # Sanitize title for filename
        safe_title = "".join(
            c if c.isalnum() or c in " -_" else "_"
            for c in title[:50]
        ).strip().replace(" ", "_")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.{format}"

        return session_dir / filename

    def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """Clean up old session directories.

        Args:
            max_age_days: Maximum age in days

        Returns:
            Number of sessions deleted
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=max_age_days)
        deleted = 0

        for session_dir in self.base_dir.iterdir():
            if session_dir.is_dir():
                # Check modification time
                mtime = datetime.fromtimestamp(session_dir.stat().st_mtime)
                if mtime < cutoff:
                    shutil.rmtree(session_dir)
                    deleted += 1
                    logger.info(f"Cleaned up old session: {session_dir.name}")

        return deleted
