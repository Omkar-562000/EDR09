# EDR Dashboard Quick Start Guide

## What's New

We've completely redesigned the dashboard with a professional SOC (Security Operations Center) interface. It looks and feels like industry-standard tools like Microsoft Defender, CrowdStrike, and SentinelOne.

## Main Features

### 1. Dashboard View (Default)
The home screen shows your system at a glance:
- **4 Summary Cards** at the top:
  - 🎯 Active Threats (critical alerts)
  - 🚨 Total Alerts (all detections)
  - ✅ Resolved (automated responses)
  - 💚 System Health (percentage)

- **Two-panel layout below:**
  - Left: Table of all alerts
  - Right: Timeline of events

### 2. Sidebar Navigation
On the left side, click to navigate:
- 📊 **Dashboard** - Overview (default view)
- ⚠️ **Alerts** - Full-screen alert table (shows count badge)
- 📋 **Activity** - Chronological timeline of all events
- 📝 **Logs** - Detailed log viewer with search/filter
- 💻 **Endpoints** - System status and response tracking
- ⚡ **Responses** - History of automated actions taken
- ⚙️ **Settings** - Adjust refresh interval

### 3. Alerts Panel
**Search & Filter:**
- 🔍 Search by alert ID, threat type, or description
- 🎨 Filter by Severity (Critical/High/Medium/Low)
- 📌 Sort by Latest or Highest Severity

**Color Coding:**
- 🔴 Red = Critical/High severity
- 🟠 Orange = Medium severity
- 🟢 Green = Low severity

**Click "View" button** to see full alert details:
- Detection ID and Rule Name
- Confidence level
- MITRE ATT&CK mapping (tactics/techniques)
- Related event information
- Raw detection data

### 4. Activity Timeline
See everything that happened in chronological order:
- 📅 Events grouped by date
- 🕐 Exact timestamp for each event
- 🎯 Event type with matching icon
- 📖 Full event details on hover
- ↕️ Scroll to see more events

**Event Types:**
- 🚨 Alerts/Detections (red)
- ⚡ Responses (green)
- 🌐 Network events (cyan)
- ⚙️ Process events (orange)
- 📌 Other system events (gray)

### 5. Logs Viewer
**Split-view log analysis:**
- Left side: List of all logs
- Right side: Detailed view when you click a log

**Features:**
- 🔍 Search in log messages
- 🏷️ Filter by event type
- 💾 View raw JSON data
- ↕️ Scroll through hundreds of logs

### 6. Endpoints View
See system-level data:
- **System Status:**
  - Total events captured
  - Detections made
  - Critical alerts
  - Actions taken

- **Response Actions:**
  - How many hosts were isolated
  - How many IPs were blocked
  - How many processes were terminated

- **Detailed Lists:**
  - All isolated hosts (🚫)
  - All blocked IPs (🔒)
  - All terminated processes (⚡)

### 7. Responses Panel
History of automated actions:
- ⚡ Terminated processes
- 🚫 Isolated hosts
- 🔒 Blocked IPs
- 🚨 Alerts generated

Each action shows:
- **Type** (what action was taken)
- **Timestamp** (when it happened)
- **Target** (what was affected)
- **Status** (success/failed)

### 8. Settings
Currently allows you to adjust:
- **Refresh Interval** - How often data updates (ms)
  - Default: 5000 (5 seconds)
  - Min: 1000 (1 second)
  - Max: 30000 (30 seconds)

## Top Navigation Bar

**Left side:**
- 📍 Project name: "EDR Tool"
- 🟢/🟠/🔴 System status indicator

**Right side:**
- 🔄 Refresh button (manual data refresh)
- ⏰ Last update time
- 👤 Your email address
- 🚪 Logout button

## System Status Colors

- 🟢 **Green "Secure"** - No critical threats, system healthy
- 🟠 **Orange "Warning"** - Multiple alerts detected
- 🔴 **Red "Under Threat"** - Critical alerts present, requires attention

## Tips & Tricks

1. **Quick Alert Search:**
   - Use the search box to find specific alerts
   - Search works across alert ID, threat type, and description

2. **Severity Filtering:**
   - Quickly focus on high-priority alerts
   - Filter by severity to reduce noise

3. **Timeline Analysis:**
   - Click any event to see details
   - Use timeline to understand attack sequence

4. **Real-time Updates:**
   - Dashboard automatically refreshes every 5 seconds
   - Click refresh icon for immediate update
   - Adjust interval in Settings if needed

5. **Alert Details:**
   - Click any alert row to see full details
   - View MITRE ATT&CK tactics and techniques
   - See related system events

6. **Log Inspection:**
   - Switch between multiple logs quickly
   - Click a log to see full details
   - View raw JSON for technical analysis

## Data Mapping

The dashboard connects to your backend APIs:
- **Alerts** ← `/api/detections`
- **Activity** ← `/api/events`
- **Logs** ← `/api/events`
- **Responses** ← `/api/actions`
- **Endpoints/Status** ← `/api/status`

Data refreshes automatically every 5 seconds.

## Color Scheme

The dashboard uses a professional **dark SOC theme**:
- Dark blue background (#08111f)
- Light gray text (#eef3ff)
- Cyan accents (#63d0ff)
- Color-coded severity and status
- High contrast for readability

## Layout Responsiveness

The dashboard works on:
- **Desktop (1280px+)** - Full 2-column layout
- **Tablet (768-1280px)** - Single column, stacked panels
- **Mobile (<768px)** - Horizontal navigation, optimized spacing

## Common Tasks

### Find an Alert
1. Click "Alerts" in sidebar
2. Use search box to find alert ID or threat type
3. Click "View" to see full details
4. Check MITRE ATT&CK mapping for context

### Track an Incident
1. Click "Activity" to see timeline
2. Scroll through events chronologically
3. Look for related process/network events
4. Check "Responses" to see what actions were taken

### Review Response Actions
1. Click "Responses" in sidebar
2. See all automated actions taken by system
3. Check target, timestamp, and status
4. Verify processes terminated, IPs blocked, hosts isolated

### Check System Health
1. Look at status indicator in top navbar
2. Check summary cards on dashboard
3. Click "Endpoints" to see detailed status
4. Review isolated hosts and blocked IPs

## Keyboard Shortcuts
- Coming soon: Keyboard navigation and shortcuts

## Getting Help
- Check the full [SOC_DASHBOARD_GUIDE.md](./SOC_DASHBOARD_GUIDE.md) for technical details
- Review API endpoint documentation in backend README

---

**Last Updated:** 2026-04-25  
**Version:** 1.0.0
