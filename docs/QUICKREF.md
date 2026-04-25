# EDR Quick Reference Guide

Quick command reference for common operations.

---

## 🚀 Quick Start

### Linux/macOS
```bash
chmod +x setup.sh
./setup.sh
python main.py
```

### Windows PowerShell
```powershell
.\setup.bat
python main.py
```

### With Frontend
```bash
python main.py --frontend
```

---

## 📋 Environment Setup

### Set Session Secret
```bash
# Linux/macOS
export EDR_SESSION_SECRET="$(openssl rand -hex 32)"

# Windows PowerShell
$env:EDR_SESSION_SECRET = "your-secret-here"
```

### Custom Configuration
```bash
# Custom port
EDR_BACKEND_PORT=9000 python main.py

# Custom watch path
EDR_WATCH_PATH=/var/log python main.py

# Disable auto-start agent
EDR_AUTO_START_AGENT=false python main.py
```

---

## 🐳 Docker Commands

### Build Image
```bash
docker build -f backend/Dockerfile -t edr:latest .
```

### Run Container
```bash
docker run -d -p 8000:8000 \
  -e EDR_SESSION_SECRET="secret" \
  -v edr-data:/app/backend/data \
  --name edr-backend \
  edr:latest
```

### Docker Compose
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Remove volumes
docker-compose down -v
```

---

## 🔌 API Quick Calls

### Authentication
```bash
# Signup
curl -X POST http://127.0.0.1:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123!"}'

# Login (saves session cookie)
curl -c cookies.txt -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123!"}'

# Get current user
curl -b cookies.txt http://127.0.0.1:8000/api/me
```

### Events & Detections
```bash
# Get events
curl -b cookies.txt http://127.0.0.1:8000/api/events?limit=10

# Get detections
curl -b cookies.txt http://127.0.0.1:8000/api/detections?limit=10

# Get status
curl -b cookies.txt http://127.0.0.1:8000/api/status
```

### Controls
```bash
# Trigger collection
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/collect

# Simulate threat
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"auth_burst"}'

# Reload rules
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/reload-rules
```

---

## 📝 Configuration Files

### Quick Edit Rules
```bash
nano backend/config/rules.json
```

### Quick Edit Settings
```bash
nano backend/config/settings.json
```

### Reload After Changes
```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/reload-rules
```

---

## 🧪 Testing

### Run Tests
```bash
pytest backend/tests/
pytest backend/tests/ -v
pytest backend/tests/ --cov=backend.edr
```

### Inject Test Event
```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -H "Cookie: edr_session=<token>" \
  -d '{
    "source":"test",
    "event_type":"process",
    "title":"test",
    "payload":{"process_name":"nc.exe","pid":1234}
  }'
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Reset Database
```bash
rm backend/data/edr.db
python main.py
```

### Check Logs
```bash
# Application logs
tail -f backend/data/logs/*.log

# Docker logs
docker logs -f edr-backend
```

### Validate Rules
```bash
python -c "import json; json.load(open('backend/config/rules.json')); print('✓ Valid')"
```

---

## 📊 Kubernetes Quick Commands

### Deploy
```bash
kubectl apply -f k8s/
kubectl get pods -n edr-system
kubectl get svc -n edr-system
```

### View Logs
```bash
kubectl logs -n edr-system -l app=edr-backend
kubectl logs -n edr-system deployment/edr-backend
```

### Scale
```bash
kubectl scale deployment edr-backend -n edr-system --replicas=3
```

### Update Configuration
```bash
kubectl edit configmap edr-config -n edr-system
kubectl restart deployment edr-backend -n edr-system
```

### Delete Everything
```bash
kubectl delete namespace edr-system
```

---

## 📚 Useful Paths

```
/backend/config/rules.json          ← Detection rules
/backend/config/settings.json       ← Runtime settings
/backend/data/edr.db               ← SQLite database
/backend/data/logs/                ← JSONL logs
/docs/DEPLOYMENT.md                ← Deployment guide
/docs/CONFIGURATION.md             ← Configuration reference
/docs/RULE_DEVELOPMENT.md          ← Rule development guide
```

---

## 🔑 Default Credentials

```
Email: admin@edr.local
Password: SecurePassword123!
```

⚠️ **CHANGE THESE IMMEDIATELY IN PRODUCTION**

---

## 🌐 Common URLs

```
Backend API:       http://127.0.0.1:8000
API Docs:          http://127.0.0.1:8000/docs
Frontend:          http://localhost:5173
Health Check:      http://127.0.0.1:8000/api/health
```

---

## 📝 Rule Template

```json
{
  "rule_id": "CATEGORY-NAME-001",
  "name": "Human readable name",
  "event_type": "process|network|file|auth|system",
  "condition": "contains|equals|in_list",
  "field": "payload_field",
  "value": "value_or_list",
  "severity": "critical|high|medium|low",
  "confidence": 85,
  "description": "What this rule detects",
  "tactics": ["MITRE Tactic"],
  "techniques": ["T1234"],
  "response_actions": ["kill_process", "generate_alert"]
}
```

---

## 🆘 Getting Help

- **README**: `cat README.md` or view online
- **API Docs**: http://127.0.0.1:8000/docs (when running)
- **Configuration**: `cat docs/CONFIGURATION.md`
- **Rules**: `cat docs/RULE_DEVELOPMENT.md`
- **Deployment**: `cat docs/DEPLOYMENT.md`
- **Contributing**: `cat CONTRIBUTING.md`

---

## 🚀 Cheat Sheet Summary

| Task | Command |
|------|---------|
| Quick start | `./setup.sh && python main.py` |
| Full stack | `python main.py --frontend` |
| Docker | `docker-compose up` |
| Tests | `pytest backend/tests/` |
| Logs | `tail -f backend/data/logs/*.log` |
| Reload rules | `curl -X POST .../api/reload-rules` |
| Health check | `curl http://127.0.0.1:8000/api/health` |
| Database reset | `rm backend/data/edr.db` |

---

**For detailed information, see:**
- README.md - Project overview
- docs/DEPLOYMENT.md - Deployment options
- docs/CONFIGURATION.md - Configuration guide
- docs/RULE_DEVELOPMENT.md - Rule writing
