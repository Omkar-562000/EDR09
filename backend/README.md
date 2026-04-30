# Automated EDR

This repository is now structured as a split application:

- `backend/` - Python FastAPI API
- `frontend/` - React + Vite user interface

The backend keeps the EDR engine, telemetry collection, detection logic, automated response simulation, SQLite persistence, and authentication. The frontend is a separate React app with a stronger product-style interface for login, dashboard monitoring, search, filtering, and simulation workflows.

## Architecture

### Backend

The backend is built with Python and FastAPI and is responsible for:

- endpoint telemetry collection
- event normalization and dispatch
- rule-based detections
- automated response simulation
- SQLite storage
- cookie-based authentication
- REST APIs for dashboard data

### Frontend

The frontend is built with React and Vite and is responsible for:

- login and signup flows
- session-aware routing
- live dashboard experience
- severity analytics and activity views
- event search and detection filtering
- simulation controls for threat scenarios

## Folder Structure

- `backend/app.py` split backend API entrypoint
- `backend/edr/` shared Python EDR core modules
- `backend/config/` rules and runtime settings
- `backend/watched/` monitored folder for file events
- `backend/data/` generated database and logs
- `backend/tests/` backend verification
- `frontend/` React application

## Requirements

- Python 3.11+
- Node.js 20+
- npm 10+

## Run Locally

You need two terminals: one for backend and one for frontend.

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd automated-edr
```

### 2. Set up the backend

#### Windows PowerShell

Use these commands exactly in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
$env:EDR_SESSION_SECRET = "replace-this-with-a-long-random-secret"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Important notes for Windows:

- use `python -m pip`, not plain `pip`
- use `$env:EDR_SESSION_SECRET = "..."`, not `export ...`
- if the project folder was moved or renamed, the old `.venv` may break because `pip.exe` can still point to the old path

If your virtual environment is broken after moving the folder, rebuild it:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
$env:EDR_SESSION_SECRET = "replace-this-with-a-long-random-secret"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
export EDR_SESSION_SECRET="replace-this-with-a-long-random-secret"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

The backend runs at:

```text
http://127.0.0.1:8000
```

### 3. Set up the frontend

In a second terminal:

#### Windows PowerShell

```powershell
cd frontend
npm install
npm run dev
```

#### Linux / macOS

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://127.0.0.1:5173
```

Open that URL in your browser.

## First Run

1. start the backend
2. start the frontend
3. open `http://127.0.0.1:5173`
4. create an account
5. log in
6. enter the dashboard

## Dashboard Features

The React dashboard includes:

- simplified manual and autonomous control flow
- overview, alerts, and activity views
- login and signup screens
- clear response posture summary
- recent alerts and recent actions
- one-click scan and threat simulation controls
- autonomous run mode for guided backend execution

## Control Flow

The interface now supports two modes.

### Manual Mode

In manual mode, the user can:

- click `Scan`
- choose a threat scenario
- click `Simulate Threat`
- click `Reload Rules`

This mode is useful when you want direct control over what the backend does.

### Autonomous Mode

In autonomous mode, the user can:

- choose a scenario or let the app auto-pick one
- click `Run Autonomous Cycle`

The active backend uses real local endpoint telemetry only. Simulation and custom event injection endpoints are not part of the runtime API.

## Authentication

The backend uses signed HTTP-only cookies for session management.

Main auth routes:

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/me`

## Main Backend APIs

- `GET /api/health`
- `GET /api/status`
- `GET /api/control`
- `GET /api/agent`
- `POST /api/agent/pause`
- `POST /api/agent/resume`
- `POST /api/agent/interval`
- `POST /api/agent/collectors/{collector_id}`
- `GET /api/events`
- `GET /api/detections`
- `GET /api/actions`
- `POST /api/collect`
- `POST /api/reload-rules`
- `POST /api/firewall/block-ip`
- `POST /api/firewall/unblock-ip`
- `POST /api/firewall/check-ip`

## Rule Configuration

Rules are defined in:

```text
backend/config/rules.json
```

You can edit that file and then use `Reload Rules` from the frontend.

## Storage

Runtime data is stored in:

- `backend/data/edr.db`
- `backend/data/logs/events.jsonl`
- `backend/data/logs/detections.jsonl`
- `backend/data/logs/actions.jsonl`

## Docker

The backend container definition now lives at `backend/Dockerfile`.

Build:

```bash
docker build -f backend/Dockerfile -t automated-edr-backend .
```

Run:

```bash
docker run -p 8000:8000 -e EDR_SESSION_SECRET="replace-this-secret" automated-edr-backend
```

For local development, the frontend should still be run separately from `frontend/`.

## Notes

- the backend and frontend are intentionally separated now
- the older static `dashboard/` implementation is no longer the primary UI
- detections are calculated from real telemetry
- resolved response actions are real manual firewall operations
- the backend continues using SQLite for portability and easier local use

## Verified Status

The following were verified after the split:

- backend imports successfully
- frontend dependencies install successfully
- frontend production build completes successfully

## Next Recommended Upgrades

- WebSocket live updates instead of polling
- PostgreSQL support
- separate deployment manifests for frontend and backend hosting
- role-based access control
- packaged scripts for one-command local startup
