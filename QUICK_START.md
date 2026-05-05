# 🚀 Quick Start - EDR System

**Everything you need to run the project in 3 steps**

---

## Step 1: Clone & Setup

```bash
# Clone repository
git clone https://github.com/Omkar-562000/EDR09.git
cd EDR09

# Windows
.\setup.bat

# Linux/macOS
chmod +x setup.sh && ./setup.sh
```

---

## Step 2: Run the Project

### **Option A: Backend Only (Simplest)**
```bash
python main.py
```
Access API: `http://127.0.0.1:8000/api/events`

### **Option B: With Dashboard**
```bash
python main.py --frontend
```
- Backend: `http://127.0.0.1:8000`
- Dashboard: `http://localhost:5173`
- Login with: `admin@example.com` / `SecurePassword123!`

---

## Step 3: Test It (Optional)

```bash
python test_edr_comprehensive.py
```

This runs the full test suite and verifies everything works.

---

## ✅ Done!

Your EDR system is now:
- ✓ Monitoring all processes, commands, and network activity
- ✓ Detecting threats in real-time
- ✓ Storing all data for analysis
- ✓ Ready to use

Open the dashboard and watch it work!

---

## 📞 Common Issues

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `EDR_BACKEND_PORT=9000 python main.py` |
| Script execution error | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| No data in dashboard | Wait 10-15 seconds, data will appear automatically |
| Module not found | Verify venv is activated: `.\.venv\Scripts\Activate.ps1` |

---

## 📖 Full Documentation

For detailed guides, see:
- `docs/COMPLETE_SETUP_AND_RUN_GUIDE.md` - Complete setup guide
- `docs/PROJECT_OVERVIEW.md` - What the system does
- `docs/CONFIGURATION.md` - Customization options
