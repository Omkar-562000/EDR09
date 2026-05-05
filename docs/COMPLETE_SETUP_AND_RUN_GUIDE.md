# 🚀 Complete EDR System Setup & Run Guide

**Complete step-by-step instructions to clone, setup, and run the Automated EDR System from scratch.**

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Clone the Repository](#clone-the-repository)
3. [Initial Setup (One-Time)](#initial-setup-one-time)
4. [Running the Project](#running-the-project)
5. [How Everything Works](#how-everything-works)
6. [Accessing the Dashboard](#accessing-the-dashboard)
7. [Testing the System](#testing-the-system)
8. [Troubleshooting](#troubleshooting)

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.11 or higher
- **RAM**: 4 GB minimum
- **Disk Space**: 2 GB minimum
- **Node.js**: 18+ (optional, for frontend development)

### Verify Installation
```bash
# Check Python version
python --version  # Should be 3.11+

# Check if pip is installed
pip --version
```

---

## 🔗 Clone the Repository

### Step 1: Choose a Directory
Open your terminal/PowerShell and navigate to where you want the project:

```powershell
# Windows PowerShell
cd C:\Users\YourUsername\Projects
# OR any directory you prefer
```

```bash
# Linux/macOS
cd ~/projects
# OR any directory you prefer
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/Omkar-562000/EDR09.git
cd EDR09
```

### Step 3: Verify the Structure
```bash
# List the contents to verify
ls  # On Linux/macOS
dir # On Windows PowerShell
```

You should see:
```
backend/
frontend/
docs/
main.py
setup.bat          (Windows)
setup.sh           (Linux/macOS)
docker-compose.yml
requirements.txt
README.md
```

---

## ⚙️ Initial Setup (One-Time)

### **Windows Users** (PowerShell)

Run the automated setup script:

```powershell
# Step 1: Navigate to project directory
cd e:\EDR09

# Step 2: Run setup script
.\setup.bat

# What this does:
# - Creates virtual environment (.venv)
# - Installs Python dependencies
# - Sets up directory structure
# - Creates necessary configuration files
```

### **Linux/macOS Users**

Run the automated setup script:

```bash
# Step 1: Navigate to project directory
cd /path/to/EDR09

# Step 2: Make script executable
chmod +x setup.sh

# Step 3: Run setup script
./setup.sh

# What this does:
# - Creates virtual environment (.venv)
# - Installs Python dependencies
# - Sets up directory structure
# - Creates necessary configuration files
```

### **Manual Setup (If Automated Fails)**

#### Windows PowerShell:
```powershell
# Step 1: Create virtual environment
python -m venv .venv

# Step 2: Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Step 3: Install dependencies
pip install -r backend/requirements.txt

# Step 4: Set session secret (generate random)
$env:EDR_SESSION_SECRET = "$(openssl rand -hex 32)"
```

#### Linux/macOS:
```bash
# Step 1: Create virtual environment
python3 -m venv .venv

# Step 2: Activate virtual environment
source .venv/bin/activate

# Step 3: Install dependencies
pip install -r backend/requirements.txt

# Step 4: Set session secret (generate random)
export EDR_SESSION_SECRET="$(openssl rand -hex 32)"
```

---

## 🎯 Running the Project

### **Option 1: Backend Only (Recommended for Testing)**

#### Windows PowerShell:
```powershell
# Step 1: Navigate to project
cd e:\EDR09

# Step 2: Activate virtual environment (if not already activated)
.\.venv\Scripts\Activate.ps1

# Step 3: Run backend
python main.py

# Expected output:
# [INFO] EDR System Starting...
# [INFO] Session secret initialized
# [INFO] Database initialized
# [INFO] Event pipeline started
# [INFO] Detection rules loaded
# [INFO] Uvicorn running on http://127.0.0.1:8000
```

#### Linux/macOS:
```bash
# Step 1: Navigate to project
cd /path/to/EDR09

# Step 2: Activate virtual environment
source .venv/bin/activate

# Step 3: Run backend
python main.py

# Expected output:
# [INFO] EDR System Starting...
# [INFO] Session secret initialized
# [INFO] Database initialized
# [INFO] Event pipeline started
# [INFO] Detection rules loaded
# [INFO] Uvicorn running on http://127.0.0.1:8000
```

---

### **Option 2: Full Stack (Backend + Frontend Dashboard)**

#### Windows PowerShell:
```powershell
# Terminal 1 - Backend
cd e:\EDR09
.\.venv\Scripts\Activate.ps1
python main.py --frontend

# Terminal 2 - Frontend (Open new PowerShell)
cd e:\EDR09\frontend
npm install    # First time only
npm run dev    # Starts at http://localhost:5173
```

#### Linux/macOS:
```bash
# Terminal 1 - Backend
cd /path/to/EDR09
source .venv/bin/activate
python main.py --frontend

# Terminal 2 - Frontend (Open new terminal)
cd /path/to/EDR09/frontend
npm install    # First time only
npm run dev    # Starts at http://localhost:5173
```

---

### **Option 3: Using Docker Compose (All-in-One)**

```bash
# Step 1: Navigate to project
cd e:\EDR09
# Or: cd /path/to/EDR09

# Step 2: Build and start containers
docker-compose up -d

# Step 3: Check if services are running
docker-compose ps

# Step 4: View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Step 5: Stop services
docker-compose down
```

---

## 🏗️ How Everything Works

### **System Architecture Overview**

```
┌──────────────────────────────────────────────────────┐
│           Web Browser (You)                          │
│  http://localhost:5173 (Frontend)                    │
│  http://localhost:8000 (API)                         │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼─────────────────────────────────┐
│         FastAPI Backend (Python)                     │
│         Running on port 8000                         │
├──────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────┐   │
│  │ 1. EVENT COLLECTION (Collectors)             │   │
│  │    - Process Collector                       │   │
│  │    - Network Collector                       │   │
│  │    - File Collector                          │   │
│  │    - System Events Collector                 │   │
│  └─────────────────┬──────────────────────────┬─┘   │
│                    │                          │      │
│  ┌─────────────────▼────────────────────┐   │      │
│  │ 2. EVENT PIPELINE (Processing)       │   │      │
│  │    - Event Queue                     │   │      │
│  │    - Normalizer (standardize data)   │   │      │
│  │    - Dispatcher (route to modules)   │   │      │
│  └─────────────────┬────────────────────┘   │      │
│                    │                          │      │
│  ┌─────────────────▼────────────────────┐   │      │
│  │ 3. DETECTION ENGINE (Analysis)       │   │      │
│  │    - Rule Engine                     │   │      │
│  │    - Pattern Matching                │   │      │
│  │    - Severity Scoring                │   │      │
│  │    - Creates Detections/Alerts       │   │      │
│  └─────────────────┬────────────────────┘   │      │
│                    │                          │      │
│  ┌─────────────────▼──────┐   ┌──────────────▼──┐  │
│  │ 4. RESPONSE ENGINE     │   │ 5. DATABASE    │  │
│  │    - Process Killer    │   │    - SQLite    │  │
│  │    - IP Blocker        │   │    - JSONL     │  │
│  │    - Host Isolation    │   │    - Events    │  │
│  │    - Action Logging    │   │    - Alerts    │  │
│  └────────────────────────┘   └────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ 6. REST API (Your Access Point)              │  │
│  │    - GET  /api/events                        │  │
│  │    - GET  /api/detections (alerts)           │  │
│  │    - GET  /api/status                        │  │
│  │    - POST /api/collect (trigger scan)        │  │
│  │    - POST /api/control/simulate (test)       │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### **Step-by-Step How It Works**

#### **Phase 1: Data Collection**
When `python main.py` starts:
1. **Process Collector** - Scans all running processes on your system
2. **Network Collector** - Monitors active network connections
3. **File Collector** - Tracks file access patterns
4. **System Collector** - Captures authentication and system events

**What gets collected**: Process names, command lines, network IPs, ports, file paths, user actions

---

#### **Phase 2: Event Pipeline Processing**
Collected data flows through processing pipeline:

```
Raw Event (e.g., "powershell.exe -enc ABC123...")
    ↓
[Event Queue] - Stores events temporarily
    ↓
[Normalizer] - Converts to standard format
    ├─ Windows format → Standard JSON
    ├─ Add timestamps
    └─ Extract key fields (command, user, source IP, etc)
    ↓
[Dispatcher] - Routes to appropriate modules
    ├─ Send to Detection Engine
    ├─ Send to Response Engine
    └─ Store in Database
    ↓
Processed Event
```

---

#### **Phase 3: Detection (Threat Analysis)**
The Detection Engine runs configured rules:

```
Input: "powershell.exe -enc JABzAD0A..."

Rule Check #1: Encoded PowerShell Execution
  ✓ MATCH → Suspicious behavior detected
  - Severity: HIGH
  - Confidence: 95%
  - MITRE ATT&CK: Obfuscated Code (T1027)

Creates Alert/Detection:
  {
    "alert_id": "ALERT-2024-001",
    "threat_type": "Encoded PowerShell",
    "severity": "HIGH",
    "confidence": 95,
    "event": {...event data...},
    "timestamp": "2024-05-04T10:30:00Z"
  }
```

**Detection Rules**: Pre-loaded from `backend/config/rules.json`
- Suspicious commands (mimikatz, PSExec, etc)
- Encoded/obfuscated scripts
- Unauthorized network connections
- Privilege escalation attempts
- Lateral movement indicators

---

#### **Phase 4: Automated Response**
When a threat is detected, the Response Engine acts:

```
Alert Triggered: Suspicious IP Connection

Response Engine:
  1. Identify the source IP
  2. Add IP to blocklist
  3. Create Windows Firewall rule (if enabled)
  4. Log the action
  5. Send notification

Creates Action Record:
  {
    "action_id": "ACTION-001",
    "type": "IP_BLOCKED",
    "target": "192.168.1.100",
    "status": "SUCCESS",
    "timestamp": "2024-05-04T10:30:01Z"
  }
```

**Possible Actions**:
- ⚡ Kill malicious process
- 🔒 Block suspicious IP address
- 🚫 Isolate host/endpoint
- 📢 Generate alert/notification

---

#### **Phase 5: Storage & Persistence**
All data stored in:

1. **SQLite Database** (`backend/data/edr.db`)
   - User accounts
   - Detection rules
   - Alerts
   - Actions history

2. **JSONL Log Files** (human-readable)
   - `backend/data/logs/events.jsonl` - All events
   - `backend/data/logs/detections.jsonl` - Alerts
   - `backend/data/logs/actions.jsonl` - Response actions

---

#### **Phase 6: API & Dashboard Display**
Data accessible via REST API:

```bash
# Get recent events
curl http://127.0.0.1:8000/api/events?limit=10

# Get active alerts
curl http://127.0.0.1:8000/api/detections

# Get system status
curl http://127.0.0.1:8000/api/status

# Get response history
curl http://127.0.0.1:8000/api/actions
```

Dashboard displays:
- 📊 Real-time alerts
- 📈 Event timeline
- 🎯 System metrics
- ⚙️ Response history
- 🔍 Advanced search/filter

---

## 🌐 Accessing the Dashboard

### **After Starting Backend**

#### Option 1: Direct API Access
```
http://localhost:8000/api/events
http://localhost:8000/api/detections
http://localhost:8000/api/status
```

#### Option 2: Web Dashboard (Full Interface)
```
http://localhost:5173
```

### **First Login**

1. **Create an account**:
   - Email: `admin@example.com`
   - Password: `SecurePassword123!`

2. **Login**:
   - Use same credentials
   - Session persists with secure cookie

3. **View Dashboard**:
   - Summary cards (threats, alerts, health)
   - Alert table (sortable, filterable)
   - Event timeline (chronological)

### **Dashboard Navigation**

| Icon | Section | Purpose |
|------|---------|---------|
| 📊 | Dashboard | Overview & summary |
| ⚠️ | Alerts | All detections/threats |
| 📋 | Activity | Event timeline |
| 📝 | Logs | Detailed log viewer |
| 💻 | Endpoints | System status |
| ⚡ | Responses | Action history |
| ⚙️ | Settings | Configuration |

---

## 🧪 Testing the System

The system works automatically as you use it. All events are captured and analyzed in real-time.

### **Verify Everything is Working**

Simply open the dashboard and check:

```bash
# 1. Backend running: python main.py --frontend
# 2. Open: http://localhost:5173
# 3. Dashboard shows real events and any detected threats
```

### **Optional: Run Full Test Suite**

If you want to verify all system components:

```bash
cd e:\EDR09
python test_edr_comprehensive.py
```

This comprehensive test verifies:
- ✓ Real command collection from system
- ✓ Threat detection accuracy
- ✓ Network monitoring
- ✓ End-to-end pipeline
- ✓ Real system audit

**Expected Output**: All 8 tests pass ✓

---

## 🐛 Troubleshooting

### **Issue 1: Python not found**

```bash
# Error: 'python' is not recognized

# Solution 1: Use python3
python3 main.py

# Solution 2: Add Python to PATH
# Windows: https://www.python.org/downloads/ → Check "Add Python to PATH"
# Then reinstall Python

# Verify:
python --version
```

---

### **Issue 2: Port 8000 already in use**

```bash
# Error: Address already in use
# Solution: Use different port
EDR_BACKEND_PORT=9000 python main.py
```

---

### **Issue 3: Virtual environment not activating**

```powershell
# Windows PowerShell Error: Script not allowed
# Solution: Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

---

### **Issue 4: Dashboard shows no data**

```bash
# No alerts displayed
# Solution: Wait 10-15 seconds for data collection
# Or manually trigger collection:
curl -X POST http://127.0.0.1:8000/api/collect
```

---

## ✅ You're Ready!

Your EDR system is now running. The platform will:
- 🔍 Monitor all system events in real-time
- 🚨 Detect suspicious activities using rules
- ⚡ Automatically respond to threats
- 📊 Display findings in professional dashboard
- 💾 Persist all data for analysis

**Start using it by**:
1. Opening the dashboard: `http://localhost:5173`
2. Navigating through alerts and events
3. Testing detection capabilities
4. Customizing rules for your environment

Happy threat hunting! 🛡️

---

**Last Updated**: May 4, 2026  
**Version**: 1.0  
**Status**: Production Ready
