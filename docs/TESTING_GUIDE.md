# 🧪 TESTING GUIDE - CMD Detection & IP Blocking

## Overview

This guide provides comprehensive testing procedures to verify:
1. ✅ Command detection works with real commands
2. ✅ IP blocking creates Windows Firewall rules
3. ✅ Real data sources are being collected
4. ✅ Detection accuracy (minimize false positives/negatives)

---

## 📋 QUICK START - Running Tests

### Option 1: Automated Comprehensive Tests (Recommended)

Run the full test suite to verify everything:

```bash
cd e:\EDR09
python test_edr_comprehensive.py
```

**What this does**:
- ✓ Test 1: Collects real command events from running processes
- ✓ Test 2: Collects all running processes with full command lines
- ✓ Test 3: Collects active network connections
- ✓ Test 4: Tests suspicious command detection (8 test cases)
- ✓ Test 5: Tests unauthorized network detection (4 test cases)
- ✓ Test 6: Validates firewall IP blocking
- ✓ Test 7: End-to-end simulation of malicious command
- ✓ Test 8: Real-time system audit for current threats

**Expected Output**:
```
✓ Command Collection: Successfully collected real commands
✓ Process Collection: Found cmd.exe/powershell.exe processes
✓ Network Collection: Found active connections
✓ Detection Engine: Correctly identified suspicious patterns
✓ IP Blocking: Firewall rules validated
✓ End-to-End: Suspicious command detected
✓ Real System Audit: 0-5 suspicious activities (depends on system)
```

---

## 🔍 MANUAL TESTING - Step by Step

### TEST 1: Verify Real Command Collection

**Goal**: Confirm that commands are actually being collected from the system

**Steps**:

1. **Open PowerShell as Administrator**
   ```powershell
   # Start PowerShell as admin
   Start-Process powershell -Verb RunAs
   ```

2. **Start the EDR backend** (in separate terminal)
   ```bash
   cd e:\EDR09
   python main.py
   ```

3. **Execute suspicious commands** (in your regular PowerShell)
   ```powershell
   # Test 1: Encoded command detection
   powershell.exe -enc JABzAD0AKABOAGUAdwAtAE8AYgBqAGUA
   
   # Test 2: Mimikatz (simulated - don't actually download)
   echo "mimikatz" | Out-Null
   
   # Test 3: Suspicious registry modification
   reg add HKLM\Software /v Test
   ```

4. **Check the backend logs**
   ```
   Backend output should show:
   INFO: Detected: Suspicious Command Intent (CMD-001)
   ```

5. **Verify in dashboard**
   - Open: http://localhost:5174
   - Login with credentials
   - Go to "Activity" tab
   - Should see your commands listed

**Expected Results**:
```
✓ Command appears in Activity Timeline
✓ Detection shown in Alerts tab
✓ Severity marked as "HIGH"
✓ Full command line visible in forensics
```

---

### TEST 2: Verify Process Collection

**Goal**: Confirm all running processes with command lines are captured

**Steps**:

1. **Run Python test script directly**
   ```bash
   cd e:\EDR09
   python -c "
from backend.edr.agent.collectors import ProcessCollector
import json

collector = ProcessCollector()
events = collector.collect()

# Show cmd/powershell processes
for event in events:
    if 'cmd' in event['payload']['process_name'].lower():
        print(json.dumps(event['payload'], indent=2))
        print()
   "
   ```

2. **Expected output** (example):
   ```json
   {
     "pid": 1234,
     "process_name": "powershell.exe",
     "cmdline": "powershell.exe -NoProfile -ExecutionPolicy Bypass",
     "username": "admin"
   }
   ```

3. **Verify source is real**
   - Command captured from actual running process
   - Not from demo data or mock
   - Username shows your Windows user

---

### TEST 3: Verify Network Connection Collection

**Goal**: Confirm network connections are captured from real system

**Steps**:

1. **Open multiple connections** (in PowerShell)
   ```powershell
   # Download something (creates real connection)
   Invoke-WebRequest -Uri "https://www.github.com" -UseBasicParsing
   
   # Check DNS (creates DNS connection)
   nslookup google.com
   
   # Leave terminal open for connection to persist
   ```

2. **Run network collector test**
   ```bash
   cd e:\EDR09
   python -c "
from backend.edr.agent.collectors import NetworkCollector
import json

collector = NetworkCollector()
events = collector.collect()

print(f'Total connections: {len(events)}')
print('\\nRecent connections:')
for event in events[:5]:
    payload = event['payload']
    print(f\"IP: {payload['remote_ip']}:{payload['remote_port']} - Status: {payload['status']}\")
   "
   ```

3. **Expected output**:
   ```
   Total connections: 42
   
   Recent connections:
   IP: 8.8.8.8:443 - Status: ESTABLISHED
   IP: 142.250.185.46:443 - Status: ESTABLISHED
   IP: 127.0.0.1:5000 - Status: LISTENING
   ```

4. **Verify in dashboard**
   - Go to Logs tab
   - Filter by "network"
   - Should see your live connections with IPs and ports

---

### TEST 4: Verify Suspicious Command Detection

**Goal**: Confirm detection engine correctly identifies malicious patterns

**Steps**:

1. **Run detection test**
   ```bash
   python test_edr_comprehensive.py
   ```
   This will test 8 different command patterns:

2. **What's being tested**:
   ```
   ✓ Encoded PowerShell (-enc parameter)
   ✓ Mimikatz (credential dumping)
   ✓ Ransomware anti-recovery (vssadmin delete shadows)
   ✓ Persistence (schtasks /create)
   ✓ Persistence (reg add)
   ✓ Download (bitsadmin)
   ✓ Legitimate commands (should NOT alert)
   ```

3. **Verify detection accuracy**
   ```
   Expected: 6 detections (malicious), 2 no detection (legitimate)
   Actual: [Check test output]
   ```

4. **Check rules file**
   ```bash
   cat backend/config/rules.json | grep -A 20 "CMD-001"
   ```
   Should show all suspicious patterns being checked

---

### TEST 5: Verify Network Detection (Unauthorized IPs)

**Goal**: Confirm system detects unauthorized outbound connections

**Steps**:

1. **Run network detection test** (part of comprehensive test)
   ```bash
   python test_edr_comprehensive.py
   ```

2. **Manual test - simulate unauthorized connection**
   ```bash
   python -c "
from backend.edr.detection.engine import DetectionEngine
from backend.edr.models import Event, EventType

engine = DetectionEngine()

# Test: Private IP should be flagged as unauthorized
event = Event(
    source='network_collector',
    event_type=EventType.NETWORK,
    title='network_connection',
    payload={
        'remote_ip': '192.168.1.100',
        'remote_port': 4444,
        'status': 'ESTABLISHED'
    }
)

detections = engine.evaluate(event)
print(f'Detections: {len(detections)}')
for d in detections:
    print(f'  Rule: {d.rule_id} - {d.rule_name}')
   "
   ```

3. **Expected output**:
   ```
   Detections: 1
     Rule: NET-001 - Unauthorized Outbound Connection
   ```

---

### TEST 6: Verify IP Blocking Works

**Goal**: Confirm firewall rules are created and IPs are blocked

**Steps**:

1. **Check Windows Firewall is running**
   ```powershell
   # Run as Administrator
   Get-NetFirewallProfile | Select-Object Name, Enabled
   
   # Expected output:
   # Name             Enabled
   # Domain             True
   # Private            True
   # Public             True
   ```

2. **Test firewall rule creation**
   ```bash
   python -c "
from backend.edr.response.firewall import WindowsFirewallController
import sys

if sys.platform != 'win32':
    print('Error: Windows required')
    exit(1)

controller = WindowsFirewallController()

# Test: Block a specific IP
test_ip = '203.0.113.44'
print(f'Attempting to block IP: {test_ip}')

result = controller.block_ip(test_ip, direction='outbound')
print(f'Result: {result.status}')
print(f'Message: {result.message}')

# Verify rule was created
check = controller.check_ip(test_ip)
print(f'\\nVerification:')
print(f'IP Blocked: {check[\"blocked\"]}')
print(f'Rules:')
for rule in check['rules']:
    print(f'  - {rule[\"name\"]}: {rule[\"exists\"]}')
   "
   ```

3. **Expected output**:
   ```
   Attempting to block IP: 203.0.113.44
   Result: blocked
   Message: Windows Firewall rule created for 203.0.113.44
   
   Verification:
   IP Blocked: True
   Rules:
     - EDR Block 203.0.113.44 Inbound: True
     - EDR Block 203.0.113.44 Outbound: True
   ```

4. **Verify in Windows Firewall GUI**
   ```powershell
   # Open firewall rules
   wf.msc
   ```
   Look for rules named "EDR Block..." in both Inbound and Outbound rules

5. **Unblock the test IP**
   ```bash
   python -c "
from backend.edr.response.firewall import WindowsFirewallController

controller = WindowsFirewallController()
result = controller.unblock_ip('203.0.113.44')
print(f'Unblocked: {result.status}')
   "
   ```

---

### TEST 7: End-to-End Incident Simulation

**Goal**: Simulate a complete attack scenario from command to IP block

**Steps**:

1. **Run end-to-end test**
   ```bash
   python test_edr_comprehensive.py
   # Look for TEST 7: END-TO-END output
   ```

2. **Manual end-to-end test**
   ```bash
   python -c "
from backend.edr.agent.collectors import CommandActivityCollector
from backend.edr.detection.engine import DetectionEngine
from backend.edr.pipeline.normalizer import EventNormalizer
from backend.edr.models import Event, EventType

print('=== SIMULATING ATTACK ===\n')

# Step 1: Create malicious event
print('1. Creating malicious command event')
event = Event(
    source='command_collector',
    event_type=EventType.COMMAND,
    title='command_observed',
    payload={
        'process_name': 'powershell.exe',
        'command_line': 'powershell.exe -enc JABzAD0AKABOAGUAdwAtAE8AYg==',
        'pid': 5678,
        'username': 'admin'
    }
)
print(f'   Event ID: {event.event_id}')

# Step 2: Normalize
print('\\n2. Normalizing event')
normalizer = EventNormalizer()
normalized = normalizer.normalize(event.to_dict())
print(f'   Normalized to: {normalized.event_type}')

# Step 3: Detect
print('\\n3. Running detection')
engine = DetectionEngine()
detections = engine.evaluate(normalized)
print(f'   Detections found: {len(detections)}')

if detections:
    d = detections[0]
    print(f'   Rule: {d.rule_id}')
    print(f'   Severity: {d.severity}')
    print(f'   Confidence: {d.confidence}%')

# Step 4: Response
print('\\n4. Response would execute:')
if detections:
    rule = [r for r in engine.rule_loader.load() if r.rule_id == d.rule_id][0]
    print(f'   Actions: {rule.response_actions}')
    for action in rule.response_actions:
        if action == 'generate_alert':
            print(f'   ✓ Alert generated')
        elif action == 'block_ip':
            print(f'   ✓ IP would be blocked')

print('\\n✅ Attack contained!')
   "
   ```

---

### TEST 8: Real-Time System Audit

**Goal**: Check current system for active threats

**Steps**:

1. **Run real-time audit**
   ```bash
   python test_edr_comprehensive.py
   # Look for TEST 8: REAL SYSTEM AUDIT output
   ```

2. **What it does**:
   - Collects all current commands
   - Collects all current network connections
   - Runs each through detection engine
   - Shows any suspicious activity

3. **Expected output** (normal system):
   ```
   📊 Analyzing 45 command events...
   
   (No suspicious commands if clean system)
   
   📊 Analyzing 38 network events...
   
   📋 Summary: 0 suspicious activities found
   ```

4. **If threats are found**:
   ```
   🚨 SUSPICIOUS COMMAND DETECTED
      Process: powershell.exe
      Command: powershell.exe -enc JABz...
      Rules Matched: ['CMD-001']
   ```

---

## 📊 Verification Checklist

### Command Detection Verification

```
□ Real commands are collected from running processes
  └─ Verify: Check backend logs for "command_collector" events
  
□ Suspicious patterns are detected
  └─ Verify: See "CMD-001" rules triggering in logs
  
□ False positives are minimal
  └─ Verify: Normal commands don't trigger alerts
  
□ Full command line is captured (including arguments)
  └─ Verify: See "-enc", "-nop", etc. in captured commands
  
□ Detection appears in dashboard within 30 seconds
  └─ Verify: Run command, check Activity tab
```

### IP Blocking Verification

```
□ Real network connections are collected
  └─ Verify: Check "netstat -ano" output matches collected IPs
  
□ Unauthorized IPs are detected
  └─ Verify: Non-127.0.0.1 IPs trigger NET-001 rule
  
□ Firewall rules are created
  └─ Verify: Check "Get-NetFirewallRule -DisplayName 'EDR Block*'"
  
□ Rules actually block traffic
  └─ Verify: Try ping blocked IP (should timeout)
  
□ Rules can be removed
  └─ Verify: Firewall rule removed after unblock_ip()
```

### Data Source Verification

```
□ Using REAL Windows processes (not mock)
  └─ Verify: PIDs exist in tasklist /v
  
□ Using REAL network connections (not simulated)
  └─ Verify: IPs appear in netstat -an output
  
□ Using REAL Event Logs (not demo data)
  └─ Verify: Event IDs match Windows Event Viewer (4688, 4625, etc.)
  
□ Using REAL registry data (not fake)
  └─ Verify: Registry paths exist and checked
  
□ Timestamp matches system time (UTC)
  └─ Verify: Events within ±5 seconds of current time
```

---

## 🔧 Troubleshooting

### Issue: "No commands collected"

**Cause**: No cmd.exe/powershell running

**Solution**:
```bash
# Open PowerShell
start powershell

# Wait a few seconds, then run test
python test_edr_comprehensive.py
```

---

### Issue: "Detection engine showing 0 detections"

**Cause**: Rules file not loaded properly

**Solution**:
```bash
# Check rules file exists
ls backend/config/rules.json

# Verify it's valid JSON
python -m json.tool backend/config/rules.json

# Check detection engine loading rules
python -c "
from backend.edr.detection.engine import DetectionEngine
engine = DetectionEngine()
print(f'Loaded {len(engine.rules)} rules')
for rule in engine.rules[:3]:
    print(f'  - {rule.rule_id}: {rule.name}')
"
```

---

### Issue: "Firewall rules not created"

**Cause**: Not running as Administrator

**Solution**:
```powershell
# Start PowerShell as Administrator
Start-Process powershell -Verb RunAs

# Then run your tests
python test_edr_comprehensive.py
```

---

### Issue: "Real data not showing in dashboard"

**Cause**: Backend not running or API endpoint broken

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Should return:
# {"status":"ok"}

# If not running, start it:
python main.py
```

---

## 📈 Performance Verification

### Measure Detection Latency

```bash
python -c "
import time
from backend.edr.detection.engine import DetectionEngine
from backend.edr.models import Event, EventType

engine = DetectionEngine()

# Measure detection time
start = time.time()
event = Event(
    source='command_collector',
    event_type=EventType.COMMAND,
    title='command_observed',
    payload={
        'process_name': 'powershell.exe',
        'command_line': 'powershell.exe -enc JABzAD0A',
    }
)
detections = engine.evaluate(event)
elapsed = (time.time() - start) * 1000

print(f'Detection time: {elapsed:.2f}ms')
print(f'Expected: <10ms')
print(f'Status: {\"✓ PASS\" if elapsed < 10 else \"⚠ SLOW\"}')"
```

---

## 📝 Test Report Template

```
EDR System Test Report
Date: [DATE]
System: Windows [VERSION]
Python: [VERSION]

TEST RESULTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Command Collection
   Status: [ ] PASS [ ] FAIL
   Commands Found: ____
   Sample: ____________________

2. Process Collection
   Status: [ ] PASS [ ] FAIL
   Processes Found: ____
   cmd.exe Present: [ ] YES [ ] NO

3. Network Collection
   Status: [ ] PASS [ ] FAIL
   Connections Found: ____
   Sample IPs: ____________________

4. Detection Engine
   Status: [ ] PASS [ ] FAIL
   Detection Time: ____ ms
   Rules Loaded: ____
   False Positives: ____

5. IP Blocking
   Status: [ ] PASS [ ] FAIL
   Rules Created: [ ] YES [ ] NO
   Can Verify in wf.msc: [ ] YES [ ] NO

6. End-to-End
   Status: [ ] PASS [ ] FAIL
   Total Latency: ____ seconds
   Full Forensics Available: [ ] YES [ ] NO

OVERALL ASSESSMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] PRODUCTION READY
[ ] NEEDS TUNING
[ ] NOT READY

Comments:
_________________________________________
_________________________________________
```

---

## ✅ Sign-Off Checklist

Before considering the system tested and verified:

- [ ] Ran automated test suite (`test_edr_comprehensive.py`) - all pass
- [ ] Manually tested command detection with real commands
- [ ] Manually tested IP blocking with Windows Firewall
- [ ] Verified data sources are real (not mock/demo)
- [ ] Checked detection latency <30 seconds
- [ ] Confirmed false positive rate <5%
- [ ] Tested both suspicious and legitimate commands
- [ ] Verified dashboard displays detections
- [ ] Tested both inbound and outbound IP blocking
- [ ] Created test report documenting results

---

## 🚀 Next Steps After Verification

Once all tests pass:

1. **Deploy to production**
   - Copy configuration to endpoint
   - Enable auto-start
   - Configure SIEM integration

2. **Establish baseline**
   - Run 24 hours to collect normal activity
   - Tune rules to reduce false positives
   - Train SOC analysts on alert types

3. **Monitor effectiveness**
   - Track detection accuracy over time
   - Measure mean time to detect (MTTD)
   - Measure mean time to respond (MTTR)

4. **Continuous improvement**
   - Update rules based on new threats
   - Add new data sources as needed
   - Refine response actions based on feedback
