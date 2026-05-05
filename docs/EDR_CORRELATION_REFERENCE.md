# EDR Correlation Reference — SOC Analyst Guide

Version: 1.0 — Generated: 2026-05-05

Purpose
- Provide a concise, actionable reference showing how process/command detections are produced, correlated into alerts, stored, and visualized in the UI (Alerts table + Activity Timeline). This document explains each backend module's role in correlation and how analysts should read the UI.

Contents
- System flow overview
- Module responsibilities and correlation roles
- Alert data model
- Correlation example (step-by-step)
- UI mapping and how to read the screenshot visualization
- Analyst playbook / quick actions
- Tuning knobs and next steps

---

## System flow (high-level)

1. Collector/Agent normalizes telemetry and emits an `Event` (process, command, network, etc.).
2. `Dispatcher` logs the `Event` (`Storage.log_event`) and calls `DetectionEngine.evaluate(event)`.
3. `DetectionEngine` runs rules and returns one or more `Detection` objects.
4. Each `Detection` is persisted (`Storage.log_detection`).
5. `Aggregator` (correlation) examines recent alerts and either merges the detection into an existing `Alert` or creates a new one.
6. `ResponseEngine` may generate actions (log, ticket, block, kill) which are persisted (`Storage.log_action`).
7. Frontend reads alerts, detections, events and displays them in the Alerts table and Activity Timeline.

Files to inspect (code)
- Detection engine: [backend/edr/detection/engine.py](backend/edr/detection/engine.py)
- Dispatcher: [backend/edr/pipeline/dispatcher.py](backend/edr/pipeline/dispatcher.py)
- Storage: [backend/edr/database/storage.py](backend/edr/database/storage.py)
- Aggregator: [backend/edr/correlation/aggregator.py](backend/edr/correlation/aggregator.py)
- Response engine: [backend/edr/response/engine.py](backend/edr/response/engine.py)
- Models: [backend/edr/models.py](backend/edr/models.py)
- Backend API: [backend/app.py](backend/app.py)
- Frontend timeline & dashboard: [frontend/src/components/ActivityTimeline.jsx](frontend/src/components/ActivityTimeline.jsx), [frontend/src/components/SOCDashboard.jsx](frontend/src/components/SOCDashboard.jsx)

---

## Module responsibilities (correlation focus)

- Dispatcher (`backend/edr/pipeline/dispatcher.py`):
  - Central ingest point. Always persists events, invokes detections, logs detections, then sends detections to the `Aggregator` before applying responses.
  - Ensures correlation runs for every detection, so UI and actions can reference aggregated alerts.

- DetectionEngine (`backend/edr/detection/engine.py`):
  - Rule-based evaluator that produces atomic `Detection` objects (one per matching rule).
  - Keeps detections explainable and fine-grained; correlation is handled separately.

- Aggregator (`backend/edr/correlation/aggregator.py`):
  - Correlates/deduplicates detections into `Alert` records.
  - Primary algorithm (current): restrict to same host; match alerts where `last_seen` is within a time window (default 300s); merge if `rule_id` or `event_id` overlaps.
  - Merge behavior: append `rule_id`/`detection_id`, update `last_seen`, escalate `severity` to the highest of members.

- Storage (`backend/edr/database/storage.py`):
  - Persists events/detections/actions/alerts to both SQLite (queryable) and JSONL logs (append-only). Alerts are written to `alerts` table and `alerts.jsonl`.

- ResponseEngine (`backend/edr/response/engine.py`):
  - Responsible for carrying out or simulating automated responses. Actions are logged and (optionally) include references to detection/alert ids.

---

## Alert data model (fields analysts will use)

- `alert_id` — unique identifier
- `title` — human-friendly summary (e.g., "Suspicious PowerShell Command")
- `host` — endpoint name
- `rule_ids` — list of rule IDs that contributed
- `detection_ids` — list of detection IDs included
- `severity` — aggregated highest severity (low → critical)
- `description` — short text summary
- `created_at`, `last_seen` — lifecycle timestamps

Alerts are available via `GET /api/alerts` on the backend.

---

## Correlation example (concrete scenario)

1. A Sysmon process-create event reports `powershell.exe` launched with `-enc` flag and writes to `%TEMP%`.
2. Detection rules fire:
   - `process_injection_detector` → `Detection A` (severity=high)
   - `command_line_detector` → `Detection B` (severity=medium)
3. Dispatcher logs both detections.
4. Aggregator receives `Detection A` and creates `Alert #X` (since no recent alert exists for that host).
5. Aggregator then receives `Detection B` (same host, within window): it appends `rule_id` and `detection_id` to `Alert #X`, updates `last_seen`, and escalates severity to `high` if needed.
6. UI shows one alert row (left panel) representing both detections, and the Activity Timeline (right) shows two chronological entries (process create then command activity) linked by `alert_id` in detail view.

Why this reduces noise: instead of N rows for many related detections, analysts see one incident (alert) with constituent signals.

---

## How to read the UI (screenshot guidance)

Left — Alerts table:
- Each row represents an aggregated Alert. Use the `View` action to expand and see constituent detections and related events. Columns of interest:
  - `THREAT TYPE` / `DESCRIPTION`: quick summary of why alert was created.
  - `SEVERITY`: highest severity of contained detections (prioritize these first).
  - `TIMESTAMP`: `last_seen` — when the last contributing detection occurred.

Right — Activity Timeline:
- Shows chronological events and detections (raw occurrences). Use the timeline to reconstruct sequence of actions:
  - Expand items to inspect `payload.command_line`, `parent_name`, `pid`, `hashes`, `remote_ip`.
  - Look for parent → child process relationships and network callbacks following process activity.

Interpretation tips
- If the Alerts table shows many items but timeline shows repeated similar events, check whether the aggregator window is too short (causing over-splitting) or too long (causing over-aggregation).
- A critical alert with many detection_ids likely indicates an ongoing incident — open the alert, review timeline items for lateral movement and network callbacks.

---

## SOC analyst quick playbook

1. Triage rules:
   - Always start with `critical` → `high` alerts.
   - Expand alert to view `detection_ids`. For each detection, expand timeline entries to capture `command_line` and `parent_name`.
2. Containment steps (if confirmed malicious):
   - Block observed external IPs in network devices and in `EDR Tool` firewall controls.
   - Terminate suspicious processes (record PID and command line first).
   - Collect forensic artifacts from host (event logs, memory image if needed).
3. Post-incident:
   - Add allowlist/denylist entries to reduce noise.
   - Tune detection rules or aggregator window to adjust grouping behavior.

---

## Tuning knobs & recommended improvements

- Aggregation window (`Aggregator.window_seconds`) — shorter values reduce grouping; longer values group long-running incidents.
- Correlation keys — current logic uses `host + rule_id/event_id`. Consider adding:
  - `command_line` normalized hash
  - `parent_pid` chain or process lineage fingerprint
  - `remote_ip` / domain grouping
- Enrichment — add IP/domain reputation and file-hash lookups to improve scoring and classification.
- UI: display `alert_id` on timeline entries and add a button to highlight timeline entries for a selected alert.

---

## Commands & quick checks

Start backend (dev):
```
set EDR_BACKEND_HOST=0.0.0.0
python main.py --backend-only
```

Start frontend (Vite dev):
```
cd frontend
npm run dev -- --host
```

API checks (use authenticated session):
```
curl --cookie cookies.txt http://localhost:8000/api/alerts
curl --cookie cookies.txt http://localhost:8000/api/detections?limit=50
```

---

If you want, I can:
- Export this Markdown to PDF and attach it,
- Or augment the doc with a worked example from your actual `data/logs/detections.jsonl` and `alerts.jsonl` to show a real incident trace.

File created: `docs/EDR_CORRELATION_REFERENCE.md`
