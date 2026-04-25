# EDR Configuration Guide

Complete reference for configuring the Automated EDR system.

---

## Table of Contents

1. [Environment Variables](#environment-variables)
2. [Settings Configuration](#settings-configuration)
3. [Detection Rules](#detection-rules)
4. [Advanced Configuration](#advanced-configuration)

---

## Environment Variables

### Session Management

| Variable | Default | Description |
|----------|---------|-------------|
| `EDR_SESSION_SECRET` | `"change-this-secret-in-production"` | HMAC secret for session tokens. **Must be changed for production!** |
| `EDR_SESSION_TTL_SECONDS` | `43200` | Session time-to-live in seconds (12 hours) |
| `EDR_COOKIE_SECURE` | `false` | Enable secure cookie flag (requires HTTPS) |

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EDR_BACKEND_HOST` | `127.0.0.1` | Backend API listen address |
| `EDR_BACKEND_PORT` | `8000` | Backend API port |
| `EDR_FRONTEND_PORT` | `5173` | Frontend dev server port |

### Monitoring Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EDR_WATCH_PATH` | `backend/watched` | Path to monitor for file changes (relative or absolute) |
| `EDR_AUTO_START_AGENT` | `true` | Auto-start endpoint agent on backend startup |
| `EDR_AGENT_INTERVAL` | `2.0` | Collection interval in seconds |

### CORS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EDR_FRONTEND_ORIGINS` | `http://127.0.0.1:5173,http://localhost:5173` | Comma-separated list of allowed frontend origins |

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EDR_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

### Path Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EDR_RULES_PATH` | `backend/config/rules.json` | Path to detection rules file |
| `EDR_SETTINGS_PATH` | `backend/config/settings.json` | Path to settings file |
| `EDR_DATABASE_PATH` | `backend/data/edr.db` | Path to SQLite database |

---

## Settings Configuration

### settings.json

Located at `backend/config/settings.json`

```json
{
  "watch_path": "watched",
  "host_name": "endpoint-01",
  "auto_start_agent": true
}
```

### Configuration Options

```json
{
  "watch_path": {
    "type": "string",
    "description": "Directory to monitor for file changes",
    "default": "watched",
    "examples": ["watched", "/var/log", "C:\\Users\\Desktop\\Uploads"]
  },
  "host_name": {
    "type": "string",
    "description": "Endpoint identifier in logs and alerts",
    "default": "endpoint-01",
    "examples": ["workstation-01", "server-prod-1", "laptop-john"]
  },
  "auto_start_agent": {
    "type": "boolean",
    "description": "Automatically start the endpoint agent",
    "default": true,
    "examples": [true, false]
  }
}
```

---

## Detection Rules

### rules.json Structure

Located at `backend/config/rules.json`

```json
{
  "rules": [
    {
      "rule_id": "UNIQUE_RULE_ID",
      "name": "Human-readable rule name",
      "event_type": "process|network|file|auth|system",
      "condition": "contains|equals|in_list|failed_login_threshold|remote_ip_not_in_allowlist",
      "field": "payload_field_to_match",
      "value": "value_or_list",
      "severity": "critical|high|medium|low",
      "confidence": 85,
      "description": "Detailed description",
      "tactics": ["MITRE ATT&CK tactic"],
      "techniques": ["T1234"],
      "response_actions": ["kill_process", "block_ip", "isolate_host", "generate_alert"]
    }
  ]
}
```

### Rule Types by Event Type

#### Process Rules

```json
{
  "rule_id": "PROC-001",
  "name": "Suspicious Process Name",
  "event_type": "process",
  "condition": "in_list",
  "field": "process_name",
  "value": ["nc.exe", "ncat.exe", "powershell.exe"],
  "severity": "critical",
  "confidence": 85,
  "description": "Detects known reverse shell utilities",
  "tactics": ["Execution", "Command and Control"],
  "techniques": ["T1059"],
  "response_actions": ["kill_process", "generate_alert"]
}
```

Payload fields:
- `process_name`: Process executable name
- `cmdline`: Full command line
- `pid`: Process ID
- `username`: User running process

#### Network Rules

```json
{
  "rule_id": "NET-001",
  "name": "Outbound to Suspicious IP",
  "event_type": "network",
  "condition": "remote_ip_not_in_allowlist",
  "field": "remote_ip",
  "value": ["127.0.0.1", "192.168.1.0/24", "::1"],
  "severity": "high",
  "confidence": 75,
  "description": "Detects connections outside baseline allowlist",
  "tactics": ["Command and Control", "Exfiltration"],
  "techniques": ["T1071"],
  "response_actions": ["block_ip", "generate_alert"]
}
```

Payload fields:
- `remote_ip`: Remote IP address
- `remote_port`: Remote port
- `local_address`: Local address:port
- `status`: Connection status (ESTABLISHED, LISTEN, etc.)
- `pid`: Process ID

#### File Rules

```json
{
  "rule_id": "FILE-001",
  "name": "System File Modification",
  "event_type": "file",
  "condition": "contains",
  "field": "path",
  "value": "Windows\\System32",
  "severity": "critical",
  "confidence": 90,
  "description": "Detects modifications to system files",
  "tactics": ["Persistence", "Defense Evasion"],
  "techniques": ["T1547"],
  "response_actions": ["generate_alert"]
}
```

Payload fields:
- `path`: File path
- `filename`: File name

#### Auth Rules

```json
{
  "rule_id": "AUTH-001",
  "name": "Brute Force Attempt",
  "event_type": "auth",
  "condition": "failed_login_threshold",
  "threshold": 5,
  "window_seconds": 300,
  "severity": "critical",
  "confidence": 90,
  "description": "Multiple failed login attempts within time window",
  "tactics": ["Credential Access"],
  "techniques": ["T1110"],
  "response_actions": ["isolate_host", "generate_alert"]
}
```

Payload fields:
- `username`: User attempting to login
- `outcome`: Result (success/failed)
- `source_ip`: Source IP address

### Condition Types

#### `contains`
String contains check (case-insensitive)

```json
{
  "condition": "contains",
  "field": "process_name",
  "value": "malware"
}
```

Matches if `"C:\\malware.exe"` is in `process_name`

#### `equals`
Exact string match (case-sensitive)

```json
{
  "condition": "equals",
  "field": "process_name",
  "value": "cmd.exe"
}
```

Matches only `"cmd.exe"`, not `"CMD.EXE"`

#### `in_list`
Check if field value is in list (case-insensitive)

```json
{
  "condition": "in_list",
  "field": "process_name",
  "value": ["nc", "netcat", "ncat", "powershell"]
}
```

#### `failed_login_threshold`
Count failures within time window

```json
{
  "condition": "failed_login_threshold",
  "threshold": 5,
  "window_seconds": 300
}
```

Triggers if 5+ failed logins for same user in 5 minutes

#### `remote_ip_not_in_allowlist`
Block IPs outside allowlist

```json
{
  "condition": "remote_ip_not_in_allowlist",
  "field": "remote_ip",
  "value": ["127.0.0.1", "192.168.0.0/16"]
}
```

---

## Advanced Configuration

### Custom Collectors

Extend `backend/edr/agent/collectors.py`:

```python
class CustomCollector:
    def collect(self) -> list[dict[str, Any]]:
        events = []
        # Your collection logic
        for item in collected_items:
            events.append({
                "source": "custom_collector",
                "event_type": "system",
                "title": "custom_event",
                "payload": {
                    "field1": "value1",
                    "field2": "value2",
                }
            })
        return events
```

### Custom Response Actions

Extend `backend/edr/response/engine.py`:

```python
def _run_action(self, action_name: str, detection: Detection) -> ResponseAction | None:
    if action_name == "custom_action":
        # Your response logic
        return ResponseAction(
            action_type=action_name,
            status="success",
            target=target,
            detection_id=detection.detection_id,
            details={...}
        )
```

### Database Access

Query detection data directly:

```python
from backend.edr.database.storage import Storage

storage = Storage()

# Get recent events
events = storage.recent_events(limit=100)

# Get recent detections
detections = storage.recent_detections(limit=100)

# Get statistics
summary = storage.summary()
```

---

## Best Practices

### Rule Writing

1. **Be Specific**: Avoid generic patterns that create false positives
2. **Test First**: Validate rules before deploying to production
3. **Set Appropriate Severity**: Match severity to impact
4. **Include Context**: Provide clear descriptions and MITRE ATT&CK mapping
5. **Use Allowlists**: For network rules, define trusted IPs/domains

### Configuration Management

1. **Version Control**: Keep rules.json and settings.json in git
2. **Document Changes**: Comment why rules were added/modified
3. **Review Before Deploy**: Have rules reviewed before production
4. **Monitor Performance**: Track false positive rate
5. **Rotate Secrets**: Regularly change EDR_SESSION_SECRET

### Monitoring

1. **Log Aggregation**: Collect all EDR logs to central location
2. **Alert on Errors**: Monitor for critical errors in logs
3. **Track Detections**: Monitor detection rate by rule
4. **Performance Metrics**: Track response times and resource usage
5. **Regular Audits**: Review detections and response actions

---

## Examples

### Example: Banking Trojan Detection

```json
{
  "rule_id": "MALWARE-BANKING-001",
  "name": "Banking Trojan Process Pattern",
  "event_type": "process",
  "condition": "in_list",
  "field": "process_name",
  "value": ["svchost32.exe", "explorer32.exe", "iexplore32.exe", "firefox32.exe"],
  "severity": "critical",
  "confidence": 95,
  "description": "Detects known banking trojan process names (suspicious 32-bit variants)",
  "tactics": ["Execution", "Defense Evasion"],
  "techniques": ["T1036.004", "T1059"],
  "response_actions": ["kill_process", "generate_alert"]
}
```

### Example: Data Exfiltration Detection

```json
{
  "rule_id": "EXFIL-BULK-001",
  "name": "Unusual Outbound Network Activity",
  "event_type": "network",
  "condition": "remote_ip_not_in_allowlist",
  "field": "remote_ip",
  "value": [
    "127.0.0.1",
    "192.168.0.0/16",
    "10.0.0.0/8",
    "172.16.0.0/12"
  ],
  "severity": "high",
  "confidence": 80,
  "description": "Detects connection attempts to external IPs (potential data exfiltration)",
  "tactics": ["Exfiltration", "Command and Control"],
  "techniques": ["T1041", "T1071"],
  "response_actions": ["block_ip", "generate_alert"]
}
```

### Example: Credential Stuffing Detection

```json
{
  "rule_id": "AUTHATTACK-BRUTEFORCE-001",
  "name": "Credential Stuffing / Brute Force",
  "event_type": "auth",
  "condition": "failed_login_threshold",
  "threshold": 10,
  "window_seconds": 600,
  "severity": "critical",
  "confidence": 95,
  "description": "Multiple failed authentication attempts detected within 10 minutes",
  "tactics": ["Credential Access"],
  "techniques": ["T1110.001"],
  "response_actions": ["isolate_host", "generate_alert"]
}
```

---

## Troubleshooting Configuration

### Rules Not Matching

1. Check rule syntax: `python -c "import json; json.load(open('backend/config/rules.json'))"`
2. Verify field names match event payload
3. Check condition type is correct
4. Reload rules: `POST /api/reload-rules`

### High False Positive Rate

1. Add more specific conditions
2. Implement allowlists
3. Increase confidence threshold
4. Add contextual conditions

### Performance Issues

1. Limit rule evaluation: Use event_type matching
2. Optimize conditions: Use in_list for common checks
3. Archive old data: Implement retention policies
4. Monitor database size: `du -sh backend/data/edr.db`

---

## Support

For configuration questions:
- Review [README.md](../README.md)
- Check [Deployment Guide](./DEPLOYMENT.md)
- Review [Rule Development Guide](./RULE_DEVELOPMENT.md)
