# EDR Demo - Quick Checklist

Minimal steps to run the complete demonstration in ~15 minutes.

---

## ✅ Pre-Demo Setup (Do Once)

```powershell
# Terminal 1: Backend Setup
cd E:\EDR09
python -m venv .venv              # Create venv (if needed)
.\.venv\Scripts\Activate.ps1      # Activate
pip install -r backend/requirements.txt  # Install deps

# Terminal 2: Frontend Setup (Optional but recommended)
cd E:\EDR09\frontend
npm install                        # Install dependencies
```

---

## 🚀 Start Demo (Day Of)

### Terminal 1: Start Backend
```powershell
.\.venv\Scripts\Activate.ps1
python main.py

# ✓ Wait for: "EDR System Started Successfully!"
# ✓ Note the URL: http://127.0.0.1:8000
```

### Terminal 2: Start Frontend (Optional)
```powershell
cd E:\EDR09\frontend
npm run dev

# ✓ Wait for: "ready in X ms"
# ✓ Note the URL: http://localhost:5173
```

---

## 📋 Demo Sequence (15 minutes)

### Step 1: Login (1 min)
```
URL: http://localhost:5173
Email: admin@edr.local
Password: SecurePassword123!
```

### Step 2: Collect Events (2 min)
```
Click "Collect" button → Wait → See events appear
Explain: "Scanning system for processes, connections, files"
```

### Step 3: Simulate Brute Force (3 min)
```bash
# Terminal 3
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"auth_burst"}'
```
**Watch:** Red "Critical" alert appears
**Say:** "5 failed logins detected → Rule AUTH-001 triggered → Host isolated automatically"

### Step 4: Simulate Malicious Connection (3 min)
```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"outbound"}'
```
**Watch:** Orange "High" alert appears
**Say:** "Unauthorized outbound connection detected → Rule NET-001 triggered → IP blocked automatically"

### Step 5: Simulate Reverse Shell (3 min)
```bash
curl -b cookies.txt -X POST http://127.0.0.1:8000/api/control/simulate \
  -H "Content-Type: application/json" \
  -d '{"scenario":"process"}'
```
**Watch:** Red "Critical" alert appears
**Say:** "Netcat (reverse shell) detected → Rule PROC-001 triggered → Process terminated automatically"

### Step 6: Show API Docs (3 min)
```
URL: http://127.0.0.1:8000/docs
Show:
  - GET /api/events
  - GET /api/detections
  - GET /api/actions
  - GET /api/status
```

---

## 🎯 Key Talking Points

- ✅ **Real-time monitoring** - Continuous system scanning
- ✅ **Rule-based detection** - 4+ pre-loaded threat rules
- ✅ **Automated response** - Kill process, block IP, isolate host
- ✅ **Persistent logging** - SQLite database + JSONL logs
- ✅ **Easy deployment** - Docker, Kubernetes, Cloud platforms
- ✅ **Extensible** - Custom rules, collectors, response actions

---

## 🔑 Credentials

```
Email:    admin@edr.local
Password: SecurePassword123!
```

---

## 🌐 Quick URLs

```
Dashboard:        http://localhost:5173
API Docs:         http://127.0.0.1:8000/docs
API Health:       http://127.0.0.1:8000/api/health
Documentation:    README.md
Demo Guide:       DEMO_GUIDE.md
```

---

## 💡 If Something Goes Wrong

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `netstat -ano \| findstr :8000` then `taskkill /PID <id> /F` |
| venv issues | Delete `.venv`, recreate with `python -m venv .venv` |
| Module not found | `pip install -r backend/requirements.txt` again |
| Rules not loading | Check `backend/config/rules.json` syntax |
| Clear data | Delete `backend/data/edr.db` and restart |

---

## 📊 Expected Results

After running demo, you should see:
- ✓ 3+ detection alerts (different severities)
- ✓ 3+ response actions triggered
- ✓ Summary showing stats
- ✓ Events listed chronologically
- ✓ API documentation working

---

## 🎉 Demo Success Metrics

- ✓ System starts without errors
- ✓ Events collected within 2 seconds
- ✓ All 3 threat scenarios trigger detections
- ✓ Dashboard updates in real-time
- ✓ API endpoints working
- ✓ Response actions visible

**Time to complete: ~15 minutes**
