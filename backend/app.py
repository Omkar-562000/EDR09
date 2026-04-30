from __future__ import annotations

import asyncio
import json
import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from backend.edr.auth import create_session_token, hash_password, new_user_id, parse_session_token, verify_password
from backend.edr.config.settings import AUTH_COOKIE_NAME, BASE_DIR, COOKIE_SECURE, SESSION_TTL_SECONDS, SETTINGS_PATH, ensure_directories
from backend.edr.service import EDRService


def load_settings() -> dict[str, Any]:
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


class AuthPayload(BaseModel):
    email: str
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Enter a valid email address")
        return email


class AgentIntervalPayload(BaseModel):
    interval_seconds: float = Field(ge=5, le=3600)


class CollectorTogglePayload(BaseModel):
    enabled: bool


class FirewallIpPayload(BaseModel):
    ip_address: str
    direction: str = "both"

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, value: str) -> str:
        direction = value.strip().lower()
        if direction not in {"inbound", "outbound", "both"}:
            raise ValueError("Direction must be inbound, outbound, or both")
        return direction


settings = load_settings()
watch_path = Path(settings["watch_path"])
if not watch_path.is_absolute():
    watch_path = BASE_DIR / watch_path
edr_service = EDRService(watch_path=watch_path)
control_state: dict[str, Any] = {
    "mode": "real_time",
    "last_run": None,
}
frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "EDR_FRONTEND_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_directories()
    if settings.get("auto_start_agent", True):
        await edr_service.start()
    yield
    await edr_service.stop()


app = FastAPI(
    title="Automated EDR Backend",
    version="0.3.0",
    summary="API backend for the split React + Python Automated EDR platform",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(request: Request) -> dict[str, Any]:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    session = parse_session_token(token)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    user = edr_service.storage.get_user_by_id(session["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return user


def set_session_cookie(response: Response, user: dict[str, Any]) -> None:
    token = create_session_token(user["user_id"], user["email"])
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=SESSION_TTL_SECONDS,
    )


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "service": "automated-edr-backend",
        "status": "ok",
        "docs": "/docs",
        "frontend_origins": frontend_origins,
    }


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/signup")
async def signup(payload: AuthPayload) -> dict[str, str]:
    if edr_service.storage.get_user_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    password_hash = hash_password(payload.password)
    try:
        edr_service.storage.create_user(new_user_id(), email=payload.email, password_hash=password_hash)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists") from exc
    return {"status": "created"}


@app.post("/api/auth/login")
async def login(payload: AuthPayload, response: Response) -> dict[str, str]:
    user = edr_service.storage.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    set_session_cookie(response, user)
    return {"status": "authenticated"}


@app.post("/api/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(AUTH_COOKIE_NAME)
    return {"status": "signed_out"}


@app.get("/api/me")
async def me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {"user_id": user["user_id"], "email": user["email"], "role": user["role"]}


@app.get("/api/control")
async def get_control_state(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    return {**control_state, "agent": edr_service.agent_status()}


@app.get("/api/agent")
async def get_agent_status(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    return edr_service.agent_status()


@app.post("/api/agent/pause")
async def pause_agent(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    return edr_service.pause_agent()


@app.post("/api/agent/resume")
async def resume_agent(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    return edr_service.resume_agent()


@app.post("/api/agent/interval")
async def set_agent_interval(
    payload: AgentIntervalPayload,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    del user
    return edr_service.set_agent_interval(payload.interval_seconds)


@app.post("/api/agent/collectors/{collector_id}")
async def set_collector_enabled(
    collector_id: str,
    payload: CollectorTogglePayload,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    del user
    try:
        return edr_service.set_collector_enabled(collector_id, payload.enabled)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown collector") from exc


@app.post("/api/firewall/block-ip")
async def block_firewall_ip(
    payload: FirewallIpPayload,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    del user
    try:
        return edr_service.block_ip(payload.ip_address, payload.direction)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@app.post("/api/firewall/unblock-ip")
async def unblock_firewall_ip(
    payload: FirewallIpPayload,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    del user
    try:
        return edr_service.unblock_ip(payload.ip_address, payload.direction)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@app.post("/api/firewall/check-ip")
async def check_firewall_ip(
    payload: FirewallIpPayload,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, object]:
    del user
    try:
        return edr_service.check_ip_block(payload.ip_address, payload.direction)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@app.get("/api/status")
async def get_status(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    return {
        "summary": edr_service.storage.summary(),
        "isolated_hosts": sorted(edr_service.response_engine.isolated_hosts),
        "blocked_ips": sorted(edr_service.response_engine.blocked_ips),
        "terminated_processes": edr_service.response_engine.terminated_processes[-20:],
        "control": control_state,
        "agent": edr_service.agent_status(),
    }


@app.get("/api/events")
async def events(limit: int = 100, user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    del user
    return edr_service.storage.recent_events(limit=min(limit, 500))


@app.get("/api/detections")
async def detections(limit: int = 100, user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    del user
    return edr_service.storage.recent_detections(limit=min(limit, 500))


@app.get("/api/actions")
async def actions(limit: int = 100, user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    del user
    real_actions = [
        action
        for action in edr_service.storage.recent_actions(limit=500)
        if action.get("details", {}).get("real_action") is True
    ]
    return real_actions[: min(limit, 500)]


@app.post("/api/collect")
async def collect_once(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    del user
    control_state["mode"] = "real_time"
    await edr_service.collect_once()
    await asyncio.sleep(0.5)
    control_state["last_run"] = "completed"
    return {"status": "collection_triggered"}


@app.post("/api/reload-rules")
async def reload_rules(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    del user
    edr_service.detection_engine.reload_rules()
    edr_service.response_engine.reload_rules()
    return {"status": "reloaded"}
