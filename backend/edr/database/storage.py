from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.edr.config.settings import DB_PATH, LOG_DIR, ensure_directories
from backend.edr.models import Detection, Event, ResponseAction


class Storage:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        ensure_directories()
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    host TEXT NOT NULL,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    payload TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS detections (
                    detection_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    confidence INTEGER NOT NULL,
                    tactics TEXT NOT NULL,
                    techniques TEXT NOT NULL,
                    event_id TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS actions (
                    action_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    target TEXT NOT NULL,
                    detection_id TEXT NOT NULL,
                    details TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def log_event(self, event: Event) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO events
                (event_id, timestamp, host, source, event_type, title, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.timestamp,
                    event.host,
                    event.source,
                    event.event_type.value,
                    event.title,
                    json.dumps(event.payload),
                ),
            )
        self._append_jsonl("events.jsonl", event.to_dict())

    def log_detection(self, detection: Detection) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO detections
                (detection_id, timestamp, rule_id, rule_name, severity, description,
                 confidence, tactics, techniques, event_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    detection.detection_id,
                    detection.timestamp,
                    detection.rule_id,
                    detection.rule_name,
                    detection.severity.value,
                    detection.description,
                    detection.confidence,
                    json.dumps(detection.tactics),
                    json.dumps(detection.techniques),
                    detection.event.event_id,
                ),
            )
        self._append_jsonl("detections.jsonl", detection.to_dict())

    def log_action(self, action: ResponseAction) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO actions
                (action_id, timestamp, action_type, status, target, detection_id, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    action.action_id,
                    action.timestamp,
                    action.action_type,
                    action.status,
                    action.target,
                    action.detection_id,
                    json.dumps(action.details),
                ),
            )
        self._append_jsonl("actions.jsonl", action.to_dict())

    def recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def recent_detections(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT d.*, e.timestamp AS event_timestamp, e.host, e.source, e.event_type,
                       e.title, e.payload
                FROM detections d
                JOIN events e ON e.event_id = d.event_id
                ORDER BY d.timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        items: list[dict[str, Any]] = []
        for row in rows:
            items.append(
                {
                    "detection_id": row["detection_id"],
                    "timestamp": row["timestamp"],
                    "rule_id": row["rule_id"],
                    "rule_name": row["rule_name"],
                    "severity": row["severity"],
                    "description": row["description"],
                    "confidence": row["confidence"],
                    "tactics": json.loads(row["tactics"]),
                    "techniques": json.loads(row["techniques"]),
                    "event": {
                        "event_id": row["event_id"],
                        "timestamp": row["event_timestamp"],
                        "host": row["host"],
                        "source": row["source"],
                        "event_type": row["event_type"],
                        "title": row["title"],
                        "payload": json.loads(row["payload"]),
                    },
                }
            )
        return items

    def recent_actions(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM actions ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_action(row) for row in rows]

    def summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            counts = {
                "events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                "detections": conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0],
                "actions": conn.execute("SELECT COUNT(*) FROM actions").fetchone()[0],
                "critical_alerts": conn.execute(
                    "SELECT COUNT(*) FROM detections WHERE severity = 'critical'"
                ).fetchone()[0],
                "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            }
        return counts

    def create_user(self, user_id: str, email: str, password_hash: str, role: str = "analyst") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (user_id, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    email.lower(),
                    password_hash,
                    role,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.lower(),),
            ).fetchone()
        if not row:
            return None
        return dict(row)

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        if not row:
            return None
        return dict(row)

    def _append_jsonl(self, filename: str, payload: dict[str, Any]) -> None:
        path = LOG_DIR / filename
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")

    def _row_to_event(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "event_id": row["event_id"],
            "timestamp": row["timestamp"],
            "host": row["host"],
            "source": row["source"],
            "event_type": row["event_type"],
            "title": row["title"],
            "payload": json.loads(row["payload"]),
        }

    def _row_to_action(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "action_id": row["action_id"],
            "timestamp": row["timestamp"],
            "action_type": row["action_type"],
            "status": row["status"],
            "target": row["target"],
            "detection_id": row["detection_id"],
            "details": json.loads(row["details"]),
        }
