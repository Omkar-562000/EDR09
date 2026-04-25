# 🔒 Automated EDR (Endpoint Detection and Response)

A **lightweight, web-based EDR tool** designed for real-time threat monitoring, detection, and automated response. Clone and run locally with minimal configuration.

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-green)
![License](https://img.shields.io/badge/license-MIT-black)

---

## 🎯 Quick Start

### One-Minute Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/automated-edr.git
cd automated-edr

# Run setup (Windows PowerShell or Linux/macOS)
# Windows
.\setup.bat

# Linux/macOS
chmod +x setup.sh
./setup.sh

# Start the EDR system
python main.py
```

Access the backend API at **http://127.0.0.1:8000**

---

## 📋 Features

### ✓ Real-Time Monitoring
- **Process Monitoring** - Track process creation, execution, and termination
- **Network Monitoring** - Monitor inbound/outbound connections, DNS queries
- **File Monitoring** - Detect file modifications and suspicious access
- **System Monitoring** - Track authentication attempts and system events

### ✓ Rule-Based Detection
- **Configurable Detection Rules** - JSON-based rule engine for custom threat patterns
- **Pre-Loaded Rules** - Common attack patterns (reverse shells, brute force, C2)
- **Severity Levels** - Critical, High, Medium, Low classifications
- **Confidence Scoring** - Assess detection accuracy and false positive rates

### ✓ Automated Response
- **Kill Malicious Processes** - Automatically terminate suspicious processes
- **Block Suspicious IPs** - Add detected threat IPs to blocklist
- **Isolate Hosts** - Quarantine compromised endpoints
- **Alert Generation** - Create actionable security alerts

### ✓ Persistent Logging
- **SQLite Database** - Structured event storage
- **JSONL Logs** - Human-readable log files for analysis
- **Query API** - RESTful endpoints for event retrieval
- **Event Correlation** - Link events to detections and responses

### ✓ Web Dashboard
- **Real-Time Alerts** - Live threat notifications
- **Event Timeline** - Chronological view of system activity
- **Statistics & Analytics** - Detection rate, severity distribution
- **Manual Controls** - Simulate threats, trigger collections

### ✓ User Management
- **Session Authentication** - Secure cookie-based sessions
- **Role-Based Access** - Analyst and admin roles
- **User Registration** - Self-service account creation
- **Account Management** - Password reset and profile updates

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│         Web Dashboard (React + Vite)                │
│  - Real-time alerts and events                      │
│  - Detection analytics and filtering                │
│  - Threat simulation controls                       │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────────┐
│        FastAPI Backend (Python)                     │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐   │
│  │ Endpoint Agent                              │   │
│  │ - ProcessCollector                          │   │
│  │ - NetworkCollector                          │   │
│  │ - FileCollector                             │   │
│  └──────────────┬────────────────────────────┬─┘   │
│                 │                            │      │
│  ┌──────────────▼─────────────┐  ┌──────────▼───┐  │
│  │ Event Pipeline             │  │ Detection    │  │
│  │ - EventQueue               │  │ - Rules      │  │
│  │ - EventNormalizer          │  │ - Engine     │  │
│  │ - Dispatcher               │  └──────────────┘  │
│  └──────────────┬─────────────┘                     │
│                 │                                   │
│  ┌──────────────▼─────────────┐                    │
│  │ Response Engine             │                    │
│  │ - Kill Process              │                    │
│  │ - Block IP                  │                    │
│  │ - Isolate Host              │                    │
│  │ - Generate Alert            │                    │
│  └──────────────┬─────────────┘                    │
│                 │                                   │
│  ┌──────────────▼─────────────┐                    │
│  │ Storage Layer               │                    │
│  │ - SQLite Database           │                    │
│  │ - JSONL Logs                │                    │
│  │ - Query API                 │                    │
│  └─────────────────────────────┘                    │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Requirements
- **Python 3.11+**
- **Node.js 20+** (optional, for frontend)
- **npm 10+** (optional, for frontend)

### Backend Only

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Set session secret (recommended)
export EDR_SESSION_SECRET="your-secure-secret-here"

# Start backend
python main.py
```

### Full Stack (Backend + Frontend)

```bash
# Run setup script
./setup.sh --frontend  # Linux/macOS
.\setup.bat --frontend # Windows

# Start full stack
python main.py --frontend
```

---

## 🚀 Usage

### Starting the System

```bash
# Backend only
python main.py

# Backend + Frontend
python main.py --frontend

# Backend with custom configuration
EDR_BACKEND_PORT=9000 python main.py
EDR_WATCH_PATH=/path/to/monitor python main.py
```

### Accessing the System

| Component | URL | Default Credentials |
|-----------|-----|-------------------|
| Backend API | http://127.0.0.1:8000 | Email: admin@edr.local |
| API Docs | http://127.0.0.1:8000/docs | Password: SecurePassword123! |
| Frontend | http://localhost:5173 | (Same as backend) |

### API Endpoints

#### Authentication
```bash
# Signup
POST /api/auth/signup
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

# Get current user
GET /api/me
```

#### Events & Detections
```bash
# Get recent events
GET /api/events?limit=100

# Get recent detections
GET /api/detections?limit=100

# Get response actions
GET /api/actions?limit=100

# Get system status
GET /api/status
```

#### Controls
```bash
# Get control state
GET /api/control

# Set control mode (manual/autonomous)
POST /api/control/mode
{
  "mode": "autonomous"
}

# Trigger event collection
POST /api/collect

# Simulate threat scenario
POST /api/control/simulate
{
  "scenario": "auto"  # or: auth_burst, outbound, process
}

# Ingest custom event
POST /api/ingest
{
  "source": "custom",
  "event_type": "process",
  "title": "suspicious_process",
  "payload": {
    "process_name": "malware.exe",
    "pid": 1234
  }
}

# Reload detection rules
POST /api/reload-rules
```

---

## ⚙️ Configuration

### settings.json
```json
{
  "watch_path": "watched",
  "host_name": "endpoint-01",
  "auto_start_agent": true
}
```

### rules.json
Detection rules are defined in JSON format. Each rule specifies:
- **rule_id**: Unique identifier
- **name**: Rule name
- **event_type**: process, network, file, auth, system
- **condition**: Detection logic (contains, equals, in_list, threshold)
- **field**: Event field to match
- **value**: Expected value or list of values
- **severity**: critical, high, medium, low
- **confidence**: 0-100 score
- **response_actions**: Actions to take (kill_process, block_ip, isolate_host, generate_alert)

Example rule:
```json
{
  "rule_id": "PROC-001",
  "name": "Suspicious Reverse Shell Process",
  "event_type": "process",
  "condition": "in_list",
  "field": "process_name",
  "value": ["nc", "ncat", "netcat", "powershell.exe"],
  "severity": "critical",
  "confidence": 85,
  "description": "Detected known reverse shell utility",
  "tactics": ["Execution", "Command and Control"],
  "techniques": ["T1059", "T1105"],
  "response_actions": ["kill_process", "generate_alert"]
}
```

### Environment Variables
```bash
# Session management
EDR_SESSION_SECRET="your-secure-secret"
EDR_SESSION_TTL_SECONDS=43200          # 12 hours

# Server configuration
EDR_BACKEND_HOST=127.0.0.1
EDR_BACKEND_PORT=8000
EDR_FRONTEND_PORT=5173

# Monitoring
EDR_WATCH_PATH=backend/watched
EDR_AUTO_START_AGENT=true

# CORS
EDR_FRONTEND_ORIGINS="http://127.0.0.1:5173,http://localhost:5173"

# Security
EDR_COOKIE_SECURE=false                # Set to 'true' in production with HTTPS
```

---

## 📊 How It Works

### 1. Event Collection
The endpoint agent continuously collects events from:
- **Process Monitor** - Scans running processes every 2 seconds
- **Network Monitor** - Captures active network connections
- **File Monitor** - Detects file modifications in watched directory
- **Auth Monitor** - Tracks authentication events

### 2. Event Normalization
Raw events are normalized to a standard format:
```python
Event(
    event_id="uuid",
    timestamp="ISO8601",
    host="endpoint-01",
    source="process_collector",
    event_type="process",
    title="process_observed",
    payload={...}
)
```

### 3. Rule Matching
Detection engine evaluates each event against configured rules:
- **Contains**: String contains check
- **Equals**: Exact match
- **In List**: Field value in list
- **Threshold**: Count within time window
- **Allowlist**: Remote IP not in whitelist

### 4. Detection & Response
When a rule matches:
1. **Detection** is created with severity and confidence
2. **Response Actions** are executed automatically:
   - Kill malicious process
   - Block suspicious IP
   - Isolate host
   - Generate alert
3. **Events, Detections, and Actions** are logged to database

### 5. Storage & Retrieval
All data is stored persistently:
- **SQLite Database** - Structured queries
- **JSONL Logs** - Sequential file logs
- **REST API** - Query and retrieve data

---

## 🧪 Testing

### Manual Testing

```bash
# Trigger event collection
curl -X POST http://127.0.0.1:8000/api/collect \
  -H "Cookie: edr_session=<your_session_token>"

# Get recent events
curl http://127.0.0.1:8000/api/events?limit=10 \
  -H "Cookie: edr_session=<your_session_token>"

# Simulate threat scenario
curl -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -H "Cookie: edr_session=<your_session_token>" \
  -d '{"scenario": "auth_burst"}'
```

### Running Tests

```bash
# Install test dependencies
pip install -r backend/requirements.txt[dev]

# Run tests
pytest backend/tests/

# With verbose output
pytest backend/tests/ -v

# With coverage
pytest backend/tests/ --cov=backend.edr
```

---

## 🔐 Security

### Important Notes
1. **Change the default session secret** for production:
   ```bash
   export EDR_SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_hex(32))')"
   ```

2. **Enable HTTPS** in production:
   ```bash
   EDR_COOKIE_SECURE=true
   ```

3. **Change default credentials** immediately:
   - Access `/api/me` to get your user ID
   - Update password through dashboard

4. **Configure CORS** for your frontend domain:
   ```bash
   EDR_FRONTEND_ORIGINS="https://yourdomain.com"
   ```

5. **Restrict network access** - Use firewall rules to limit API access

---

## 📝 Project Structure

```
automated-edr/
├── main.py                          # Central orchestrator
├── setup.sh                         # Linux/macOS setup
├── setup.bat                        # Windows setup
├── README.md                        # This file
│
├── backend/
│   ├── app.py                       # FastAPI application
│   ├── requirements.txt             # Python dependencies
│   ├── pyproject.toml               # Project configuration
│   │
│   ├── edr/
│   │   ├── __init__.py
│   │   ├── models.py                # Data models
│   │   ├── auth.py                  # Authentication
│   │   ├── service.py               # Main EDRService
│   │   ├── logging.py               # Logging configuration
│   │   │
│   │   ├── agent/                   # Endpoint monitoring
│   │   │   ├── collectors.py
│   │   │   └── service.py
│   │   │
│   │   ├── detection/               # Threat detection
│   │   │   ├── engine.py
│   │   │   └── rules.py
│   │   │
│   │   ├── response/                # Automated response
│   │   │   └── engine.py
│   │   │
│   │   ├── pipeline/                # Event processing
│   │   │   ├── dispatcher.py
│   │   │   ├── normalizer.py
│   │   │   └── queue_manager.py
│   │   │
│   │   ├── database/                # Data persistence
│   │   │   └── storage.py
│   │   │
│   │   ├── config/                  # Configuration
│   │   │   └── settings.py
│   │   │
│   │   └── api/                     # API routes (optional)
│   │       └── app.py
│   │
│   ├── config/
│   │   ├── rules.json               # Detection rules
│   │   └── settings.json            # Runtime settings
│   │
│   ├── dashboard/                   # Web UI
│   │   ├── index.html
│   │   ├── login.html
│   │   └── static/
│   │
│   ├── data/
│   │   ├── logs/                    # JSONL logs
│   │   ├── edr.db                   # SQLite database
│   │   └── watched/                 # Monitored directory
│   │
│   └── tests/
│       └── test_edr_flow.py
│
└── frontend/                        # React + Vite
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── api.js
    │   └── components/
    └── public/
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and write tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📚 Documentation

- **[API Documentation](http://127.0.0.1:8000/docs)** - OpenAPI/Swagger docs (when running)
- **[Configuration Guide](./docs/CONFIGURATION.md)** - Detailed configuration options
- **[Rule Development](./docs/RULE_DEVELOPMENT.md)** - Creating custom detection rules
- **[Deployment](./docs/DEPLOYMENT.md)** - Production deployment guide

---

## 🐛 Troubleshooting

### Virtual Environment Issues
```bash
# Rebuild virtual environment
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Port Already in Use
```bash
# Change port
EDR_BACKEND_PORT=9000 python main.py
```

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm backend/data/edr.db
python main.py
```

### Rules Not Loading
```bash
# Validate rules.json
python -c "import json; json.load(open('backend/config/rules.json'))"

# Reload rules via API
curl -X POST http://127.0.0.1:8000/api/reload-rules \
  -H "Cookie: edr_session=<your_session>"
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **EDR Development Team** - Initial architecture and implementation

---

## 📞 Support

For issues, questions, or suggestions:
1. Check existing [Issues](https://github.com/yourusername/automated-edr/issues)
2. Review [Documentation](./docs)
3. Create a new [Issue](https://github.com/yourusername/automated-edr/issues/new)

---

## 🎓 Learning Resources

- **MITRE ATT&CK Framework** - Threat tactics and techniques
- **OWASP Top 10** - Security best practices
- **Sigma Rules** - Community detection rules
- **CIS Controls** - Cybersecurity best practices

---

**Made with ❤️ for the cybersecurity community**
