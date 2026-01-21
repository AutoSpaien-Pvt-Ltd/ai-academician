"""SQLite database for session persistence."""

import json
from pathlib import Path
from typing import Optional
from uuid import UUID

import aiosqlite

from src.config import get_config
from src.models.session import ResearchSession
from src.models.source import Source
from src.models.paper import PaperDraft, PaperOutline
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database manager for AI Academician."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the database.

        Args:
            db_path: Path to the database file
        """
        if db_path is None:
            config = get_config()
            db_path = config.storage.database_path

        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Connect to the database and create tables."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = await aiosqlite.connect(str(self.db_path))
        await self._create_tables()

    async def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def _create_tables(self) -> None:
        """Create database tables."""
        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );

            CREATE TABLE IF NOT EXISTS drafts (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );

            CREATE TABLE IF NOT EXISTS outlines (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );

            CREATE INDEX IF NOT EXISTS idx_sources_session ON sources(session_id);
            CREATE INDEX IF NOT EXISTS idx_drafts_session ON drafts(session_id);
        """)
        await self._connection.commit()

    async def save_session(self, session: ResearchSession) -> None:
        """Save a research session."""
        data = json.dumps(session.to_dict())
        await self._connection.execute(
            """
            INSERT OR REPLACE INTO sessions (id, data, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (str(session.id), data, session.created_at.isoformat(), session.updated_at.isoformat())
        )
        await self._connection.commit()

    async def get_session(self, session_id: UUID) -> Optional[ResearchSession]:
        """Get a research session by ID."""
        async with self._connection.execute(
            "SELECT data FROM sessions WHERE id = ?",
            (str(session_id),)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                data = json.loads(row[0])
                return ResearchSession.from_dict(data)
        return None

    async def list_sessions(self, limit: int = 10) -> list[ResearchSession]:
        """List recent sessions."""
        sessions = []
        async with self._connection.execute(
            "SELECT data FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        ) as cursor:
            async for row in cursor:
                data = json.loads(row[0])
                sessions.append(ResearchSession.from_dict(data))
        return sessions

    async def save_source(self, source: Source) -> None:
        """Save a source."""
        data = json.dumps(source.to_dict())
        await self._connection.execute(
            """
            INSERT OR REPLACE INTO sources (id, session_id, data)
            VALUES (?, ?, ?)
            """,
            (str(source.id), str(source.session_id), data)
        )
        await self._connection.commit()

    async def get_sources(self, session_id: UUID) -> list[Source]:
        """Get all sources for a session."""
        sources = []
        async with self._connection.execute(
            "SELECT data FROM sources WHERE session_id = ?",
            (str(session_id),)
        ) as cursor:
            async for row in cursor:
                data = json.loads(row[0])
                sources.append(Source.from_dict(data))
        return sources

    async def save_draft(self, draft: PaperDraft) -> None:
        """Save a paper draft."""
        data = json.dumps(draft.to_dict())
        await self._connection.execute(
            """
            INSERT OR REPLACE INTO drafts (id, session_id, version, data)
            VALUES (?, ?, ?, ?)
            """,
            (str(draft.id), str(draft.session_id), draft.version, data)
        )
        await self._connection.commit()

    async def get_draft(self, session_id: UUID, version: Optional[int] = None) -> Optional[PaperDraft]:
        """Get a paper draft."""
        if version is not None:
            query = "SELECT data FROM drafts WHERE session_id = ? AND version = ?"
            params = (str(session_id), version)
        else:
            query = "SELECT data FROM drafts WHERE session_id = ? ORDER BY version DESC LIMIT 1"
            params = (str(session_id),)

        async with self._connection.execute(query, params) as cursor:
            row = await cursor.fetchone()
            if row:
                data = json.loads(row[0])
                return PaperDraft.from_dict(data)
        return None

    async def delete_session(self, session_id: UUID) -> None:
        """Delete a session and all related data."""
        await self._connection.execute(
            "DELETE FROM sources WHERE session_id = ?",
            (str(session_id),)
        )
        await self._connection.execute(
            "DELETE FROM drafts WHERE session_id = ?",
            (str(session_id),)
        )
        await self._connection.execute(
            "DELETE FROM outlines WHERE session_id = ?",
            (str(session_id),)
        )
        await self._connection.execute(
            "DELETE FROM sessions WHERE id = ?",
            (str(session_id),)
        )
        await self._connection.commit()
