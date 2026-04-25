from __future__ import annotations

import asyncio
import json
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response, status as http_status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.edr.auth import create_session_token, hash_password, new_user_id, parse_session_token, verify_password
from backend.edr.config.settings import AUTH_COOKIE_NAME, BASE_DIR, COOKIE_SECURE, DASHBOARD_DIR, SESSION_TTL_SECONDS, SETTINGS_PATH, STATIC_DIR, ensure_directories
from backend.edr.service import EDRService


def load_settings() -> dict[str, Any]:
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


class AuthRequest(BaseModel):
    email: str
    password: str


settings = load_settings()
watch_path = Path(settings["watch_path"])
if not watch_path.is_absolute():
    watch_path = BASE_DIR / watch_path
edr_service = EDRService(watch_path=watch_path)


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_directories()
    if settings.get("auto_start_agent", True):
        await edr_service.start()
    yield
    await edr_service.stop()


app = FastAPI(
    title="Automated EDR",
    version="0.1.0",
    summary="Real-time endpoint monitoring and automated threat response",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_current_user(request: Request) -> dict[str, Any]:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    session = parse_session_token(token)
    if not session:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    user = edr_service.storage.get_user_by_id(session["user_id"])
    if not user:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
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


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> Response:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if token and parse_session_token(token):
        return FileResponse(DASHBOARD_DIR / "index.html")
    return RedirectResponse(url="/login", status_code=http_status.HTTP_302_FOUND)


@app.get("/login", response_class=HTMLResponse)
async def login_page() -> FileResponse:
    return FileResponse(DASHBOARD_DIR / "login.html")


@app.get("/signup", response_class=HTMLResponse)
async def signup_page() -> FileResponse:
    return FileResponse(DASHBOARD_DIR / "signup.html")


@app.get("/api/me")
async def me(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {"user_id": user["user_id"], "email": user["email"], "role": user["role"]}


@app.post("/api/auth/signup")
async def signup(auth: AuthRequest) -> dict[str, str]:
    email = auth.email
    password = auth.password
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if edr_service.storage.get_user_by_email(email):
        raise HTTPException(status_code=409, detail="User already exists")
    password_hash = hash_password(password)
    try:
        edr_service.storage.create_user(new_user_id(), email=email, password_hash=password_hash)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="User already exists") from exc
    return {"status": "created"}


@app.post("/api/auth/login")
async def login(response: Response, auth: AuthRequest) -> dict[str, str]:
    email = auth.email
    password = auth.password
    user = edr_service.storage.get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    set_session_cookie(response, user)
    return {"status": "authenticated"}


@app.post("/api/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(AUTH_COOKIE_NAME)
    return {"status": "signed_out"}


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/status")
async def status(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    del user
    return {
        "summary": edr_service.storage.summary(),
        "isolated_hosts": sorted(edr_service.response_engine.isolated_hosts),
        "blocked_ips": sorted(edr_service.response_engine.blocked_ips),
        "terminated_processes": edr_service.response_engine.terminated_processes[-20:],
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
    await edr_service.collect_once()
    await asyncio.sleep(0.5)
    return {"status": "collection_triggered"}


@app.post("/api/ingest")
async def ingest(event: dict[str, Any], user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    del user
    try:
        await edr_service.ingest_event(event)
        await asyncio.sleep(0.2)
    except Exception as exc:  # pragma: no cover - FastAPI exception boundary
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ingested"}


@app.post("/api/reload-rules")
async def reload_rules(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, str]:
    del user
    edr_service.detection_engine.reload_rules()
    edr_service.response_engine.reload_rules()
    return {"status": "reloaded"}


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(_: dict[str, Any] = Depends(get_current_user)) -> FileResponse:
    return FileResponse(DASHBOARD_DIR / "index.html")
