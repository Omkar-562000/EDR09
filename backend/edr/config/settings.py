from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
LOG_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "edr.db"
RULES_PATH = BASE_DIR / "config" / "rules.json"
SETTINGS_PATH = BASE_DIR / "config" / "settings.json"
DASHBOARD_DIR = BASE_DIR / "dashboard"
STATIC_DIR = DASHBOARD_DIR / "static"
AUTH_COOKIE_NAME = "edr_session"
SESSION_TTL_SECONDS = int(os.getenv("EDR_SESSION_TTL_SECONDS", "43200"))
SESSION_SECRET = os.getenv("EDR_SESSION_SECRET", "change-this-secret-in-production")
COOKIE_SECURE = os.getenv("EDR_COOKIE_SECURE", "false").lower() == "true"

QUEUE_POLL_TIMEOUT = 0.5
DEFAULT_AGENT_INTERVAL = 2.0
FAILED_LOGIN_WINDOW_SECONDS = 300


def ensure_directories() -> None:
    for path in (DATA_DIR, LOG_DIR, DASHBOARD_DIR, STATIC_DIR):
        path.mkdir(parents=True, exist_ok=True)
