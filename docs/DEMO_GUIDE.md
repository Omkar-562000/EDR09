# EDR System - User Demonstration Guide

A complete step-by-step walkthrough to demonstrate the Automated EDR system from a user's perspective.

---

## 📋 Table of Contents

1. [Prerequisites Check](#prerequisites-check)
2. [Initial Setup (First Time Only)](#initial-setup-first-time-only)
3. [Starting the System](#starting-the-system)
4. [Login & Dashboard Access](#login--dashboard-access)
5. [Core Features Walkthrough](#core-features-walkthrough)
6. [Demonstration Scenarios](#demonstration-scenarios)
7. [API Testing](#api-testing)
8. [Cleanup & Troubleshooting](#cleanup--troubleshooting)

---

## Prerequisites Check

Before starting, verify your environment:

### Windows (PowerShell)
```powershell
# Check Python version
python --version
# Expected: Python 3.11+ (e.g., Python 3.11.0)

# Check if virtual environment exists
ls .venv
# If not found, you'll need to create it

# Check Node.js for frontend (optional)
node --version
npm --version
```

### Linux/macOS (Terminal)
```bash
# Check Python version
python3 --version
# Expected: Python 3.11+ 

# Check virtual environment
ls -la .venv
# If not found, you'll need to create it

# Check Node.js
node --version
npm --version
```

---

## Initial Setup (First Time Only)

### Option A: Automatic Setup (Recommended)

#### Windows (PowerShell)
```powershell
# Navigate to project
cd E:\EDR09

# Run setup script
.\setup.bat

# This will:
# ✓ Create virtual environment
# ✓ Install Python dependencies
# ✓ Optionally install frontend dependencies
# ✓ Validate configuration

# When prompted, choose:
# - Backend only (fast, ~2 min)
# - Backend + Frontend (complete, ~5 min)
```

#### Linux/macOS (Terminal)
```bash
# Navigate to project
cd ~/automated-edr

# Make script executable
chmod +x setup.sh

# Run setup script
./setup.sh

# Optionally add frontend
./setup.sh --frontend

# Wait for completion (2-5 minutes)
```

### Option B: Manual Setup

#### Windows (PowerShell)
```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r backend/requirements.txt

# Set session secret
$env:EDR_SESSION_SECRET = "your-secure-secret-here"

# (Optional) Install frontend dependencies
cd frontend
npm install
cd ..
```

#### Linux/macOS (Terminal)
```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Set session secret
export EDR_SESSION_SECRET="your-secure-secret-here"

# (Optional) Install frontend dependencies
cd frontend && npm install && cd ..
```

---

## Starting the System

### Quick Start - Backend Only

This is the fastest way to get started:

#### Windows (PowerShell)
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start the EDR system
python main.py
```

**Expected Output:**
```
INFO | edr.main | Validating environment...
INFO | edr.main | ✓ Python version: 3.11.x
INFO | edr.main | ✓ Backend directory found
INFO | edr.main | ✓ Requirements file found
INFO | edr.main | ✓ Rules file found
INFO | edr.main | ✓ Settings file found
INFO | edr.main | ✓ Loaded 4 detection rules
INFO | edr.main | Starting backend server...
INFO | edr.main | ✓ Backend started (PID: 12345)
INFO | edr.main | → API available at http://127.0.0.1:8000
INFO | edr.main | → Docs available at http://127.0.0.1:8000/docs
======================================================================
INFO | edr.main | EDR System Started Successfully!
======================================================================
INFO | edr.main | 🔍 Backend API
INFO | edr.main | → URL: http://127.0.0.1:8000
INFO | edr.main | → Docs: http://127.0.0.1:8000/docs
INFO | edr.main |
INFO | edr.main | 📋 Default Credentials
INFO | edr.main | → Email: admin@edr.local
INFO | edr.main | → Password: SecurePassword123!
======================================================================
```

#### Linux/macOS (Terminal)
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the EDR system
python main.py
```

**✅ System is running!** Leave this terminal open.

---

### Full Stack - Backend + Frontend

For complete demonstration experience:

#### Terminal 1: Backend
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python main.py
```

```bash
# Linux/macOS
source .venv/bin/activate
python main.py
```

#### Terminal 2: Frontend
```powershell
# Windows PowerShell (New terminal)
cd E:\EDR09\frontend
npm run dev
```

```bash
# Linux/macOS (New terminal)
cd ~/automated-edr/frontend
npm run dev
```

**Expected Frontend Output:**
```
  VITE v7.1.12  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  Press h to show help
```

---

## Login & Dashboard Access

### Access the System

#### Backend API Only
Open your browser and go to:
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/api/health

#### With Frontend
Open your browser and go to:
- **Dashboard**: http://localhost:5173
- **API Documentation**: http://127.0.0.1:8000/docs

### Step 1: Login

**Using Frontend Dashboard:**
1. Open http://localhost:5173
2. You'll see the login page
3. Enter credentials:
   - Email: `admin@edr.local`
   - Password: `SecurePassword123!`
4. Click "Login"
5. Dashboard loads with system status

**Using API Directly (curl):**

```bash
# Login and save cookies
curl -c cookies.txt -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@edr.local",
    "password": "SecurePassword123!"
  }'

# Expected response:
# {"status":"authenticated"}
```

### Step 2: View Dashboard

Once logged in, you'll see:
- **Summary Cards**: Total events, detections, actions, critical alerts
- **Recent Events**: List of collected system events
- **Recent Detections**: Triggered security alerts
- **Control Panel**: Manual trigger options
- **Statistics**: Visual charts of activity

---

## Core Features Walkthrough

### Feature 1: Real-Time Monitoring

**What it does:** Continuously collects events from your system

**See it in action:**

#### Via API
```bash
# Trigger a collection cycle
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/collect

# Response:
# {"status":"collection_triggered"}

# View collected events
curl -b cookies.txt http://127.0.0.1:8000/api/events?limit=10
```

**Expected Output:**
```json
[
  {
    "event_id": "uuid-here",
    "timestamp": "2026-04-24T10:30:45.123456+00:00",
    "host": "endpoint-01",
    "source": "process_collector",
    "event_type": "process",
    "title": "process_observed",
    "payload": {
      "pid": 1234,
      "process_name": "python.exe",
      "cmdline": "python main.py",
      "username": "DESKTOP\\User"
    }
  },
  ...
]
```

#### Via Dashboard
1. Click "Collect" button in Control Panel
2. Wait 2-3 seconds
3. See events appear in "Recent Events" section
4. Scroll to see process, network, and file events

### Feature 2: Rule-Based Detection

**What it does:** Evaluates events against detection rules to identify threats

**Current Rules:**
1. **PROC-001** - Suspicious reverse shell processes
2. **AUTH-001** - Failed login attempts (brute force)
3. **NET-001** - Unauthorized outbound connections
4. **FILE-001** - Sensitive file modifications

**View Rules:**
```bash
# See loaded rules
cat backend/config/rules.json

# Look for:
# - rule_id
# - name
# - event_type
# - condition
# - severity
# - response_actions
```

### Feature 3: Threat Simulation

**What it does:** Simulate threats to test the system without real malware

**Simulation Scenarios:**

#### Scenario 1: Brute Force Attack
```bash
# API call
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"auth_burst"}'

# Or via dashboard: Controls → "Simulate Brute Force"

# What happens:
# - 5 failed login events injected
# - AUTH-001 rule triggers
# - Critical alert generated
# - Host isolation action suggested
```

#### Scenario 2: Malicious Connection
```bash
# API call
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"outbound"}'

# What happens:
# - Network connection to 203.0.113.44:4444 injected
# - NET-001 rule triggers
# - High alert generated
# - IP blocking action suggested
```

#### Scenario 3: Reverse Shell Process
```bash
# API call
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"process"}'

# What happens:
# - Process "nc.exe" (netcat) event injected
# - PROC-001 rule triggers
# - Critical alert generated
# - Process termination action triggered
```

#### Scenario 4: Auto (Random)
```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"auto"}'

# Randomly picks one of the above scenarios
```

### Feature 4: View Detections

**See all triggered alerts:**

#### Via API
```bash
# Get recent detections
curl -b cookies.txt http://127.0.0.1:8000/api/detections?limit=20

# Response includes:
# - detection_id
# - rule_id, rule_name
# - severity (critical/high/medium/low)
# - confidence (0-100)
# - tactics and techniques (MITRE ATT&CK)
# - triggering event details
```

#### Via Dashboard
1. Log in to dashboard
2. Look at "Recent Detections" section
3. Each row shows:
   - Detection time
   - Rule name
   - Severity (color-coded)
   - Event details

### Feature 5: Automated Response Actions

**See what actions were taken:**

#### Via API
```bash
# Get response actions
curl -b cookies.txt http://127.0.0.1:8000/api/actions?limit=20

# Shows:
# - action_id
# - action_type (kill_process, block_ip, isolate_host)
# - status (simulated_success)
# - target (process name or IP)
# - timestamp
```

#### Via Dashboard
1. Check "Recent Actions" section
2. View automatically triggered responses
3. See blocked IPs and terminated processes

### Feature 6: System Status

**Monitor overall health:**

#### Via API
```bash
# Get comprehensive status
curl -b cookies.txt http://127.0.0.1:8000/api/status

# Response shows:
# - Total events collected
# - Total detections triggered
# - Total response actions
# - Critical alerts count
# - Blocked IPs
# - Isolated hosts
# - Terminated processes
```

#### Via Dashboard
1. Top of dashboard shows summary cards:
   - Events: 127
   - Detections: 8
   - Actions: 5
   - Critical: 2
2. Real-time updates as events occur

---

## Demonstration Scenarios

### Complete Demonstration Flow (15 minutes)

#### Part 1: Setup & Login (2 minutes)

```powershell
# Terminal 1: Start backend
cd E:\EDR09
.\.venv\Scripts\Activate.ps1
python main.py

# Wait for startup message
# Copy URL: http://127.0.0.1:8000/docs
```

```powershell
# Terminal 2: Start frontend
cd E:\EDR09\frontend
npm run dev

# Wait for "ready in X ms"
# Copy URL: http://localhost:5173
```

1. Open http://localhost:5173 in browser
2. Login with credentials
3. See blank dashboard (no data yet)

#### Part 2: Collect Events (2 minutes)

**Via Dashboard:**
1. Click "Collect" button
2. Wait 2-3 seconds
3. Observe events appearing in "Recent Events"

**Explain what's happening:**
- "We're scanning your system for processes, network connections, and files"
- "Events are being collected and normalized"
- "Each event is evaluated against our detection rules"

#### Part 3: Simulate Threat #1 (3 minutes)

**Simulate Brute Force Attack:**

```bash
# Terminal 3 (or use dashboard Controls)
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"auth_burst"}'
```

**Watch the dashboard:**
1. New events appear for failed logins
2. Red "Critical" detection appears
3. "Host Isolation" action auto-triggered
4. Summary card updates (now shows 1 critical alert)

**Explain:**
- "The system detected 5 failed login attempts in 300 seconds"
- "This matches AUTH-001 rule: Multiple Failed Login Attempts"
- "Automated response: System recommends isolating this host"

#### Part 4: Simulate Threat #2 (3 minutes)

**Simulate Malicious Connection:**

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"outbound"}'
```

**Watch the dashboard:**
1. New network event appears
2. "High" severity detection appears
3. "Block IP" action triggered automatically
4. IP 203.0.113.44 added to blocklist

**Explain:**
- "An outbound connection to suspicious IP detected"
- "This matches NET-001 rule: Unauthorized Outbound Connection"
- "Automated response: IP has been blocked"

#### Part 5: Simulate Threat #3 (3 minutes)

**Simulate Reverse Shell:**

```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"process"}'
```

**Watch the dashboard:**
1. Process event appears (nc.exe)
2. "Critical" detection appears
3. "Kill Process" action triggered
4. Process added to terminated list

**Explain:**
- "Netcat (nc.exe) process detected - commonly used for reverse shells"
- "This matches PROC-001 rule: Suspicious Reverse Shell Process"
- "Automated response: Malicious process has been terminated"

#### Part 6: Review Findings (2 minutes)

**Show API Dashboard (http://127.0.0.1:8000/docs):**

1. Try `GET /api/events`
   - Show collected events
   - Explain event structure

2. Try `GET /api/detections`
   - Show all triggered rules
   - Point out severity levels
   - Show MITRE ATT&CK mapping

3. Try `GET /api/actions`
   - Show automatic responses
   - Explain action types

4. Try `GET /api/status`
   - Show summary statistics
   - Point out blocked IPs and processes

---

## API Testing

### Using OpenAPI/Swagger Interface

1. Go to http://127.0.0.1:8000/docs
2. See all available endpoints
3. Click on any endpoint to expand
4. Click "Try it out"
5. Click "Execute"
6. See response

### Manual API Testing with curl

#### Test 1: Health Check (No auth needed)
```bash
curl http://127.0.0.1:8000/api/health

# Response:
# {"status":"ok"}
```

#### Test 2: Get Current User
```bash
curl -b cookies.txt http://127.0.0.1:8000/api/me

# Response:
# {"user_id":"uuid","email":"admin@edr.local","role":"analyst"}
```

#### Test 3: Ingest Custom Event
```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source": "custom_test",
    "event_type": "process",
    "title": "test_event",
    "payload": {
      "process_name": "suspicious.exe",
      "pid": 9999,
      "cmdline": "suspicious.exe -malware",
      "username": "testuser"
    }
  }'

# Response:
# {"status":"ingested"}

# Then check events:
curl -b cookies.txt http://127.0.0.1:8000/api/events?limit=1
```

#### Test 4: Reload Rules (after modifying rules.json)
```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/reload-rules

# Response:
# {"status":"reloaded"}
```

---

## Cleanup & Troubleshooting

### Stopping the System

#### Graceful Shutdown
```powershell
# In terminal with running system, press:
Ctrl + C

# Expected output:
# Shutting down EDR system...
# [OK] Backend stopped
# [OK] Frontend stopped
# EDR system stopped
```

### Reset Everything

#### Keep running and just clear data
```bash
# Keep system running in Terminal 1

# In Terminal 3, reset database:
rm backend/data/edr.db

# System will recreate database on next event collection
```

#### Full reset
```powershell
# Stop all terminals (Ctrl+C)

# Remove database
Remove-Item backend/data/edr.db -Force

# Remove logs
Remove-Item backend/data/logs -Recurse -Force

# Start again
python main.py
```

### Common Issues

#### Port Already in Use
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
$env:EDR_BACKEND_PORT = "9000"
python main.py
```

#### Virtual Environment Issues
```powershell
# Deactivate
deactivate

# Remove venv
Remove-Item .venv -Recurse -Force

# Recreate
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

#### Rules Not Reloading
```bash
# Validate rules.json
python -c "import json; json.load(open('backend/config/rules.json')); print('✓ Valid')"

# Check for syntax errors
cat backend/config/rules.json | python -m json.tool

# Reload via API
curl -X POST http://127.0.0.1:8000/api/reload-rules
```

---

## Tips for Impressive Demo

### ✨ Demo Tips

1. **Start Fresh**
   - Begin with empty database
   - Shows real-time capabilities

2. **Explain Each Step**
   - "We're collecting system events..."
   - "Rule matching in progress..."
   - "Automated response triggered..."

3. **Use Both Interfaces**
   - Start with Dashboard (visual)
   - Show API Docs (technical)
   - Switch back to Dashboard for impact

4. **Use Different Scenarios**
   - First scenario: Auth attack (common)
   - Second scenario: Network threat (visible)
   - Third scenario: Process threat (dramatic)

5. **Highlight Automation**
   - Point out rules triggered automatically
   - Show responses executed without user action
   - Emphasize speed (milliseconds)

6. **Mention Architecture**
   - Multiple collectors (process, network, file)
   - Rule-based engine with 4+ rules
   - Automatic response actions
   - Persistent logging with SQLite

---

## Quick Reference Commands

### Start System
```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

### Frontend (separate terminal)
```powershell
cd frontend
npm run dev
```

### Access Points
```
Dashboard: http://localhost:5173
API Docs:  http://127.0.0.1:8000/docs
Health:    http://127.0.0.1:8000/api/health
```

### Credentials
```
Email:    admin@edr.local
Password: SecurePassword123!
```

### Quick API Commands
```bash
# Collect events
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/collect

# Simulate auth attack
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"auth_burst"}'

# View events
curl -b cookies.txt http://127.0.0.1:8000/api/events

# View detections
curl -b cookies.txt http://127.0.0.1:8000/api/detections
```

---

**Ready to demonstrate! Good luck! 🚀**
