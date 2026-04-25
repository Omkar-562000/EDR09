# EDR SOC Dashboard - Implementation Guide

## Overview

We have successfully built a professional, industry-style SOC (Security Operations Center) dashboard for the EDR tool. This dashboard provides real-time visualization of endpoint security data, including alerts, logs, system activity, and automated responses.

## Architecture & Components

### 1. **Main Dashboard Component** (`SOCDashboard.jsx`)
The central hub that manages all dashboard functionality:
- Data fetching and state management
- Navigation between different views
- Real-time updates with configurable polling interval
- System status determination based on threat levels

**Features:**
- Auto-refresh every 5 seconds (configurable)
- Determines system status (Secure/Warning/Threat) based on critical alert count
- Manages selected alert for detailed viewing
- Responsive sidebar navigation

### 2. **Navigation & Layout**

#### Top Navigation Bar (`soc-navbar`)
- **Left Side:**
  - Project name/brand
  - System status indicator with color coding
  
- **Right Side:**
  - Refresh button with disabled state during loading
  - Last update timestamp
  - Current user email
  - Logout button

#### Left Sidebar (`soc-sidebar`)
- **Navigation Items:**
  - Dashboard (summary view)
  - Alerts (full alert table)
  - Activity (timeline view)
  - Logs (detailed logs viewer)
  - Endpoints (system status view)
  - Responses (action history)
  - Settings (configuration)

- **Visual Indicators:**
  - Active nav item highlighted
  - Alert count badge on Alerts menu item
  - Icon + label format for easy identification

### 3. **Dashboard Views**

#### Dashboard Overview (Default View)
1. **Summary Cards** (4-column grid)
   - Active Threats: Number of critical alerts
   - Total Alerts: All detections
   - Resolved: Automated responses taken
   - System Health: % based on status
   - Color-coded backgrounds (red/orange/green)

2. **Two-Column Layout**
   - Left: Alerts Panel (table view)
   - Right: Activity Timeline (chronological events)

#### Alerts Panel (`AlertsPanel.jsx`)
**Full-featured alert management system:**

**Display:**
- Table with 7 columns:
  - Alert ID (shortened UUID)
  - Threat Type (rule name)
  - Severity (color-coded badge)
  - Process (affected process from event)
  - Timestamp
  - Status
  - Action (View button)

**Features:**
- **Search:** Search across alert ID, threat type, description, process
- **Filter by Severity:** All / Critical / High / Medium / Low
- **Filter by Status:** All / Active / Resolved
- **Sort Options:**
  - Latest First (by timestamp)
  - Highest Severity
- **Row Interaction:** Click row to open detail modal
- **Color Coding:**
  - Red (#ff9090) = Critical/High
  - Orange (#f3c66a) = Medium
  - Green (#80e6a7) = Low
- **Empty State:** Helpful message when no alerts match criteria
- **Footer:** Shows count of filtered vs total alerts

**Data Mapping:**
```
detection_id → Alert ID
rule_name / description → Threat Type
severity → Severity
event.title / event.payload.process_name → Process
timestamp → Timestamp
```

#### Activity Timeline (`ActivityTimeline.jsx`)
**Chronological event visualization:**

**Features:**
- **Date Grouping:** Events grouped by date
- **Timeline Layout:** Vertical timeline with events
- **Event Cards:**
  - Event icon (based on type)
  - Event type (process/network/file/alert/response)
  - Timestamp
  - Title/description
  - Source information
  - Details (if available)

**Event Color Coding:**
- 🚨 Alerts/Detections → Red
- ⚡ Responses → Green
- 🌐 Network events → Cyan
- ⚙️ Process events → Orange
- 📌 Other → Gray

**Visual Elements:**
- Color-coded left border
- Hover effects
- Scrollable container (max-height 600px)

#### Logs Viewer (`LogsViewer.jsx`)
**Detailed log inspection:**

**Layout:**
- Split view: logs list (left) + detail panel (right)
- Scrollable containers

**Features:**
- **Search:** Find logs by message content
- **Filter by Type:** Show specific event types
- **Log Entry Preview:**
  - Timestamp (gray, monospace)
  - Log type (cyan, uppercase)
  - Message (truncated)
- **Detail View:**
  - Full log details when selected
  - Expandable JSON view
  - Close button to deselect
  - All fields displayed in code format

**Colors:**
- Timestamps: Muted gray
- Types: Accent cyan
- Messages: Light text

#### Endpoints View (`EndpointsView.jsx`)
**System-level status and response data:**

**Sections:**
1. **System Status Card**
   - Total Events
   - Total Detections
   - Critical Alerts (red if > 0)
   - Automated Actions

2. **Response Actions Card**
   - Isolated Hosts count
   - Blocked IPs count
   - Terminated Processes count

3. **Isolated Hosts List**
   - Host names with 🚫 icon
   - Shows isolation responses

4. **Blocked IPs List**
   - IP addresses with 🔒 icon
   - Shows network blocks

5. **Terminated Processes List**
   - Process names with ⚡ icon
   - Shows process terminations

#### Response Panel (`ResponsePanel.jsx`)
**Action history and automated responses:**

**Action Items Display:**
- **Header:**
  - Action type (uppercase)
  - Timestamp
  
- **Content:**
  - Description/target
  - Status badge
  - Details excerpt

**Action Types & Colors:**
- **Terminate/Kill** → Red border + red background
- **Isolate/Block** → Orange border + orange background
- **Alert** → Red border
- **Other** → Gray border

**Features:**
- Sorted by timestamp (newest first)
- Empty state message
- Action count in header
- Scrollable list

### 4. **Alert Detail Modal** (`AlertDetailModal.jsx`)
**Comprehensive alert inspection:**

**Fields Displayed:**
- Detection ID
- Rule Name
- Severity (badge)
- Confidence percentage
- Timestamp
- Detection Source
- Rule ID
- Description
- MITRE ATT&CK Tactics (tags)
- MITRE ATT&CK Techniques (tags)
- Related Event details
- Raw JSON data

**Features:**
- Modal overlay with semi-transparent background
- Close button (✕)
- Scrollable body
- Buttons: Close, Mark as Resolved
- Tag display for tactics/techniques

## Design System

### Color Palette
```css
--bg: #08111f (dark blue background)
--panel: rgba(13, 20, 34, 0.92) (panel background)
--text: #eef3ff (light text)
--muted: #95a4c4 (secondary text)
--accent: #63d0ff (cyan accent)
--ok: #80e6a7 (green - secure)
--warn: #f3c66a (orange - warning)
--danger: #ff9090 (red - danger)
```

### Severity Levels
- **Critical** → Red (#ff9090)
- **High** → Red (#ff9090)
- **Medium** → Orange (#f3c66a)
- **Low** → Green (#80e6a7)

### Status Indicators
- **Secure** → 🟢 Green
- **Warning** → 🟠 Orange
- **Threat** → 🔴 Red

### Typography
- Font Family: Inter, Segoe UI, Arial, sans-serif
- Headings: H1-H3 with appropriate sizing
- Labels: Uppercase, small size, accent color
- Monospace: For IDs, paths, timestamps (code blocks)

## Responsive Design

### Breakpoints
- **Desktop (1280px+):** 4-column summary grid, full 2-column layout
- **Tablet (768-1280px):** 2-column summary grid, stacked layout
- **Mobile (<768px):**
  - Sidebar converts to horizontal nav bar
  - Single column layout
  - Condensed nav items
  - Reduced padding

## API Integration

### Data Flow
1. **Fetch:** Component calls `api.detections()`, `api.events()`, `api.actions()`, `api.status()`
2. **Transform:** Raw API response is used directly (no additional transform needed)
3. **Display:** Components render data using correct field mappings

### Endpoints Used
```javascript
GET /api/status → System summary, isolated hosts, blocked IPs, terminated processes
GET /api/detections → Alerts with full detection data
GET /api/events → All system events
GET /api/actions → Automated response actions
POST /api/collect → Trigger data collection
POST /api/reload-rules → Reload detection rules
```

### Data Structures

**Detection Object:**
```javascript
{
  detection_id: "uuid",
  timestamp: "ISO-8601",
  rule_id: "rule-name",
  rule_name: "Suspicious Process",
  severity: "high|medium|low|critical",
  description: "Detection description",
  confidence: 85,
  tactics: ["Execution", "Persistence"],
  techniques: ["T1234", "T5678"],
  event: {
    event_id: "uuid",
    timestamp: "ISO-8601",
    host: "endpoint-name",
    source: "source-name",
    event_type: "process|network|file|auth|system",
    title: "Process started",
    payload: { ...details }
  }
}
```

**Event Object:**
```javascript
{
  event_id: "uuid",
  timestamp: "ISO-8601",
  host: "endpoint-name",
  source: "source-name",
  event_type: "process|network|file|auth|system",
  title: "Event title",
  payload: { ...details }
}
```

**Action Object:**
```javascript
{
  action_id: "uuid",
  timestamp: "ISO-8601",
  action_type: "terminate_process|isolate_host|block_ip|alert",
  status: "success|failed|pending",
  target: "target-identifier",
  detection_id: "uuid",
  details: { ...metadata }
}
```

**Status Object:**
```javascript
{
  summary: {
    events: 1234,
    detections: 56,
    critical_alerts: 2,
    actions: 43
  },
  isolated_hosts: ["host1", "host2"],
  blocked_ips: ["1.2.3.4", "5.6.7.8"],
  terminated_processes: ["process1.exe", "process2.exe"]
}
```

## Features Implemented

### ✅ Real-Time Updates
- Auto-refresh every 5 seconds
- Configurable interval in Settings
- Last update timestamp displayed
- Refresh button for manual updates

### ✅ Alert Management
- Search & filter capabilities
- Severity color coding
- Detailed alert modal
- View affected processes
- MITRE ATT&CK mapping display

### ✅ Activity Monitoring
- Chronological event timeline
- Date grouping
- Event type categorization
- Scrollable event feed
- 100+ events visible

### ✅ Logs Analysis
- Full-text search
- Event type filtering
- Detail inspection
- JSON view of raw data
- Scrollable interface

### ✅ System Status
- Health percentage
- Threat indicators
- Isolated hosts list
- Blocked IPs list
- Terminated processes history

### ✅ Response Tracking
- Action history
- Status indicators
- Target tracking
- Timestamp sorting
- Action type categorization

### ✅ User Experience
- Professional dark theme
- Responsive layout
- Intuitive navigation
- Empty states
- Loading indicators
- Error handling
- Session management

## Styling Details

### CSS Classes Overview
```css
.soc-dashboard          /* Main container */
.soc-navbar             /* Top navigation */
.soc-sidebar            /* Left sidebar */
.soc-main               /* Main content area */
.summary-grid           /* Summary cards grid */
.panel                  /* Panel container */
.alerts-table           /* Alert table */
.timeline-event         /* Timeline event */
.action-item            /* Response action */
.modal-content          /* Modal container */
.status-badge           /* Status indicator */
.severity-badge         /* Severity indicator */
```

### Interactive Elements
- **Buttons:** Gradient backgrounds, hover effects, disabled states
- **Inputs:** Dark background, light text, focus outlines
- **Tables:** Hover rows, click effects, sticky headers
- **Navigation:** Active state highlighting, hover backgrounds
- **Modals:** Overlay, scroll containment, responsive sizing

## Performance Considerations

1. **Data Fetching:**
   - Limit to 50 detections, 100 events, 30 actions
   - 5-second refresh interval (configurable)
   - All requests in parallel using Promise.all()

2. **Rendering:**
   - useMemo for filtered/sorted lists
   - Scrollable containers with max-heights
   - Overflow handling with truncation

3. **Memory:**
   - Singleton components
   - Cleanup on component unmount
   - Event listeners removed on cleanup

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ JavaScript support
- CSS Grid & Flexbox support
- Fetch API support

## Future Enhancements
- WebSocket integration for real-time updates
- Advanced filtering with date ranges
- Export functionality (PDF, CSV)
- Alert acknowledgment/resolution workflow
- Custom dashboard layouts
- Role-based visibility controls
- Alert correlation and grouping
- Threat intelligence integration
- Automated playbook responses
- Custom rule creation UI

## Security Notes
- All API calls include credentials (cookies)
- Session validation before dashboard access
- CSRF protection via SameSite cookies
- Safe JSON.stringify for data display
- No sensitive data in localStorage

## Troubleshooting

### Alerts not loading?
- Check `/api/detections` endpoint is responding
- Verify authentication token is valid
- Check browser console for errors

### Timeline not showing events?
- Ensure `/api/events` has data
- Check event timestamp format (should be ISO-8601)
- Verify event_type is set correctly

### Styling issues?
- Clear browser cache (Ctrl+Shift+Delete)
- Rebuild frontend (`npm run build`)
- Check CSS variables in `:root`

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-25  
**Status:** Production Ready ✓
