"""Local Discord memory store with an optional discord.py-compatible backfill.

The module deliberately has no Discord dependency.  It accepts normalized
message dictionaries, which keeps tests offline and lets a connector supply
messages only after the server/channel permissions and consent are configured.
"""
from __future__ import annotations

import asyncio
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterable, Iterable


def _timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        stamp = value
    elif isinstance(value, str) and value.strip():
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        stamp = datetime.now(timezone.utc)
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc).isoformat()


def _message_dict(message: Any) -> dict:
    if isinstance(message, dict):
        return message
    return {
        "id": str(getattr(message, "id", "")),
        "channel_id": str(getattr(getattr(message, "channel", None), "id", "")),
        "author_id": str(getattr(getattr(message, "author", None), "id", "")),
        "author_name": str(getattr(getattr(message, "author", None), "display_name", "")),
        "content": str(getattr(message, "content", "")),
        "timestamp": getattr(message, "created_at", None),
        "reply_to": str(getattr(getattr(message, "reference", None), "message_id", "") or ""),
        "attachments": len(getattr(message, "attachments", ()) or ()),
        "reactions": len(getattr(message, "reactions", ()) or ()),
    }


class DiscordMemory:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS messages (
                    discord_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL,
                    author_id TEXT NOT NULL, author_name TEXT NOT NULL,
                    content TEXT NOT NULL, timestamp TEXT NOT NULL,
                    reply_to TEXT NOT NULL DEFAULT '', attachments INTEGER NOT NULL DEFAULT 0,
                    reactions INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX IF NOT EXISTS idx_discord_channel ON messages(channel_id);
                CREATE INDEX IF NOT EXISTS idx_discord_author ON messages(author_id);
                CREATE INDEX IF NOT EXISTS idx_discord_time ON messages(timestamp);
            """)

    def ingest(self, messages: Iterable[dict | Any], *, consent: bool = False) -> int:
        if not consent:
            raise PermissionError("Confirme consentimento e escopo do canal antes da ingestão")
        count = 0
        with self._connect() as conn:
            for raw in messages:
                item = _message_dict(raw)
                content = str(item.get("content", "")).strip()
                ident = str(item.get("id", "")).strip()
                channel = str(item.get("channel_id", "")).strip()
                author = str(item.get("author_id", "")).strip()
                if not ident or not channel or not author or not content or len(content) > 32000:
                    continue
                conn.execute("""INSERT OR REPLACE INTO messages
                    (discord_id,channel_id,author_id,author_name,content,timestamp,reply_to,attachments,reactions)
                    VALUES (?,?,?,?,?,?,?,?,?)""", (ident, channel, author,
                    str(item.get("author_name", author))[:200], content, _timestamp(item.get("timestamp")),
                    str(item.get("reply_to", "")), int(item.get("attachments", 0) or 0),
                    int(item.get("reactions", 0) or 0)))
                count += 1
        return count

    async def backfill_channel(self, channel: Any, *, limit: int = 5000, consent: bool = False) -> int:
        """Backfill a discord.py TextChannel without importing discord.py."""
        if not consent:
            raise PermissionError("Confirme consentimento e escopo do canal antes da ingestão")
        if not isinstance(limit, int) or not 1 <= limit <= 100000:
            raise ValueError("limit deve estar entre 1 e 100000")
        rows = []
        async for message in channel.history(limit=limit):
            rows.append(_message_dict(message))
        return self.ingest(rows, consent=True)

    def search(self, query: str, *, limit: int = 20, channel_id: str | None = None) -> dict:
        if not isinstance(query, str) or not 1 <= len(query.strip()) <= 200:
            raise ValueError("query deve ter entre 1 e 200 caracteres")
        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit deve estar entre 1 e 100")
        like = "%" + query.strip().replace("%", "\\%").replace("_", "\\_") + "%"
        sql = "SELECT * FROM messages WHERE content LIKE ? ESCAPE '\\'"
        args: list[Any] = [like]
        if channel_id:
            sql += " AND channel_id = ?"
            args.append(str(channel_id))
        sql += " ORDER BY timestamp DESC LIMIT ?"
        args.append(limit)
        with self._connect() as conn:
            rows = [dict(row) for row in conn.execute(sql, args)]
        return {"query": query.strip(), "count": len(rows), "entries": rows}

    def summary(self, channel_id: str | None = None) -> dict:
        with self._connect() as conn:
            where, args = (" WHERE channel_id = ?", [channel_id]) if channel_id else ("", [])
            total = conn.execute("SELECT COUNT(*) FROM messages" + where, args).fetchone()[0]
            channels = conn.execute("SELECT channel_id, COUNT(*) count FROM messages" + where + " GROUP BY channel_id ORDER BY count DESC", args).fetchall()
            authors = conn.execute("SELECT author_id, author_name, COUNT(*) count FROM messages" + where + " GROUP BY author_id, author_name ORDER BY count DESC LIMIT 20", args).fetchall()
            latest = conn.execute("SELECT timestamp FROM messages" + where + " ORDER BY timestamp DESC LIMIT 1", args).fetchone()
        return {"messages": total, "channels": [dict(row) for row in channels],
                "top_authors": [dict(row) for row in authors], "last_activity": latest[0] if latest else None}

    def context(self, query: str, *, limit: int = 8) -> str:
        data = self.search(query, limit=limit)
        lines = ["Resumo de memória Discord (dados locais, não verificados):"]
        lines.extend(f"- {row['author_name']} [{row['timestamp']}]: {row['content']}" for row in data["entries"])
        return "\n".join(lines)


def load_json(path: str | Path) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise ValueError("O arquivo precisa conter uma lista JSON de mensagens")
    return data
