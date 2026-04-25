from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from backend.edr.config.settings import SESSION_SECRET, SESSION_TTL_SECONDS


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000)
    return f"{base64.urlsafe_b64encode(salt).decode()}:{base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt_encoded, digest_encoded = password_hash.split(":", 1)
    salt = base64.urlsafe_b64decode(salt_encoded.encode())
    expected = hash_password(password, salt)
    return hmac.compare_digest(expected, password_hash)


def create_session_token(user_id: str, email: str) -> str:
    expires_at = int((datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)).timestamp())
    payload = f"{user_id}|{email}|{expires_at}"
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    token = f"{payload}|{signature}"
    return base64.urlsafe_b64encode(token.encode("utf-8")).decode("utf-8")


def parse_session_token(token: str) -> dict[str, str] | None:
    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        user_id, email, expires_at, signature = decoded.split("|", 3)
        payload = f"{user_id}|{email}|{expires_at}"
        expected = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        if int(expires_at) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return {"user_id": user_id, "email": email}
    except Exception:
        return None


def new_user_id() -> str:
    return str(uuid4())
