#!/usr/bin/env python
"""
Real-Time Detection Monitor & Simulator
Execute test commands and watch them get detected in real-time
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from backend.edr.agent.collectors import CommandActivityCollector, NetworkCollector
from backend.edr.detection.engine import DetectionEngine
from backend.edr.models import Event, EventType
from backend.edr.database.storage import Storage


class RealtimeDetectionMonitor:
    def __init__(self):
        self.engine = DetectionEngine()
        self.storage = Storage()
        self.command_collector = CommandActivityCollector()
        self.network_collector = NetworkCollector()
        self.initial_events = set()
        self.last_checked_count = 0
    
    def initialize(self) -> None:
        """Get baseline of current events"""
        print("\n📊 Establishing baseline...")
        
        events = self.storage.recent_events(limit=1000)
        self.initial_events = {e["event_id"] for e in events}
        self.last_checked_count = len(events)
        
        print(f"   ✓ Baseline: {self.last_checked_count} existing events")
        print(f"   ✓ Ready to detect NEW events")
    
    def monitor_commands(self, duration_seconds: int = 30) -> None:
        """Monitor for new commands"""
        print(f"\n🔍 Monitoring commands for {duration_seconds} seconds...")
        print("   (Try running: powershell.exe -enc JABzAD0A)")
        print("   (Or: cmd.exe /c whoami)\n")
        
        end_time = time.time() + duration_seconds
        detections_found = 0
        
        while time.time() < end_time:
            try:
                # Collect current commands
                events = self.command_collector.collect()
                
                for event in events:
                    # Create Event object
                    cmd_event = Event(
                        source=event["source"],
                        event_type=EventType.COMMAND,
                        title=event["title"],
                        payload=event["payload"]
                    )
                    
                    # Check for detections
                    detections = self.engine.evaluate(cmd_event)
                    
                    if detections:
                        detections_found += 1
                        print(f"\n🚨 DETECTION! ({detections_found})")
                        print(f"   Process: {event['payload'].get('process_name')}")
                        print(f"   Command: {event['payload'].get('command_line', 'N/A')[:80]}...")
                        print(f"   Detections: {[d.rule_id for d in detections]}")
                        print(f"   Severity: {', '.join([d.severity.value for d in detections])}")
                        print()
                
                time.sleep(2)  # Check every 2 seconds
            
            except KeyboardInterrupt:
                print("\n\n⏹ Monitoring stopped")
                break
            except Exception as e:
                print(f"⚠ Error: {e}")
                time.sleep(2)
        
        print(f"\n📊 Monitoring complete. Found {detections_found} detections.")
    
    def monitor_network(self, duration_seconds: int = 30) -> None:
        """Monitor for suspicious network connections"""
        print(f"\n🔍 Monitoring network for {duration_seconds} seconds...")
        print("   (Try: Invoke-WebRequest https://suspicious-site.com)")
        print("   (Or: ping 8.8.8.8)\n")
        
        end_time = time.time() + duration_seconds
        detections_found = 0
        seen_ips = set()
        
        while time.time() < end_time:
            try:
                events = self.network_collector.collect()
                
                for event in events:
                    net_event = Event(
                        source=event["source"],
                        event_type=EventType.NETWORK,
                        title=event["title"],
                        payload=event["payload"]
                    )
                    
                    detections = self.engine.evaluate(net_event)
                    
                    remote_ip = event['payload'].get('remote_ip')
                    if detections and remote_ip not in seen_ips:
                        detections_found += 1
                        seen_ips.add(remote_ip)
                        print(f"\n⚠ SUSPICIOUS CONNECTION! ({detections_found})")
                        print(f"   IP: {remote_ip}")
                        print(f"   Port: {event['payload'].get('remote_port')}")
                        print(f"   Status: {event['payload'].get('status')}")
                        print(f"   Detections: {[d.rule_id for d in detections]}")
                        print()
                
                time.sleep(2)
            
            except KeyboardInterrupt:
                print("\n\n⏹ Monitoring stopped")
                break
            except Exception as e:
                print(f"⚠ Error: {e}")
                time.sleep(2)
        
        print(f"\n📊 Monitoring complete. Found {detections_found} suspicious connections.")


def test_scenario_1() -> None:
    """Test: Encoded PowerShell Detection"""
    print("\n" + "="*70)
    print("  SCENARIO 1: Encoded PowerShell Command")
    print("="*70)
    
    print("\n📝 Malicious command:")
    cmd = "powershell.exe -enc JABzAD0AKABOAGUAdwAtAE8AYgBqAGUAYwB0IE5ldC5XZWJDZGLLAAAA"
    print(f"   {cmd}\n")
    
    print("🔧 Simulating detection...")
    
    from backend.edr.detection.engine import DetectionEngine
    from backend.edr.models import Event, EventType
    
    engine = DetectionEngine()
    
    event = Event(
        source="command_collector",
        event_type=EventType.COMMAND,
        title="command_observed",
        payload={
            "process_name": "powershell.exe",
            "command_line": cmd,
            "pid": 1234,
            "username": "attacker"
        }
    )
    
    detections = engine.evaluate(event)
    
    if detections:
        d = detections[0]
        print(f"\n✅ DETECTED!")
        print(f"   Rule: {d.rule_id} - {d.rule_name}")
        print(f"   Severity: {d.severity}")
        print(f"   Confidence: {d.confidence}%")
        print(f"   Tactics: {', '.join(d.tactics)}")
        print(f"   Techniques: {', '.join(d.techniques)}")
    else:
        print("\n❌ NOT DETECTED (False Negative)")


def test_scenario_2() -> None:
    """Test: Ransomware Anti-Recovery"""
    print("\n" + "="*70)
    print("  SCENARIO 2: Ransomware Anti-Recovery")
    print("="*70)
    
    print("\n📝 Ransomware command:")
    cmd = "vssadmin delete shadows /all /quiet"
    print(f"   {cmd}\n")
    
    print("🔧 Simulating detection...")
    
    from backend.edr.detection.engine import DetectionEngine
    from backend.edr.models import Event, EventType
    
    engine = DetectionEngine()
    
    event = Event(
        source="command_collector",
        event_type=EventType.COMMAND,
        title="command_observed",
        payload={
            "process_name": "cmd.exe",
            "command_line": cmd,
            "pid": 5678,
            "username": "system"
        }
    )
    
    detections = engine.evaluate(event)
    
    if detections:
        d = detections[0]
        print(f"\n✅ DETECTED!")
        print(f"   Rule: {d.rule_id} - {d.rule_name}")
        print(f"   Severity: {d.severity}")
        print(f"   Confidence: {d.confidence}%")
    else:
        print("\n❌ NOT DETECTED (False Negative)")


def test_scenario_3() -> None:
    """Test: Lateral Movement (Net User)"""
    print("\n" + "="*70)
    print("  SCENARIO 3: Lateral Movement (User Creation)")
    print("="*70)
    
    print("\n📝 Lateral movement command:")
    cmd = "net user backdoor Password123! /add"
    print(f"   {cmd}\n")
    
    print("🔧 Simulating detection...")
    
    from backend.edr.detection.engine import DetectionEngine
    from backend.edr.models import Event, EventType
    
    engine = DetectionEngine()
    
    event = Event(
        source="command_collector",
        event_type=EventType.COMMAND,
        title="command_observed",
        payload={
            "process_name": "cmd.exe",
            "command_line": cmd,
            "pid": 7890,
            "username": "admin"
        }
    )
    
    detections = engine.evaluate(event)
    
    if detections:
        d = detections[0]
        print(f"\n✅ DETECTED!")
        print(f"   Rule: {d.rule_id} - {d.rule_name}")
        print(f"   Severity: {d.severity}")
        print(f"   Confidence: {d.confidence}%")
    else:
        print("\n❌ NOT DETECTED (False Negative)")


def main() -> None:
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-Time Detection Monitor")
    parser.add_argument(
        "--mode",
        choices=["monitor-cmd", "monitor-net", "scenario1", "scenario2", "scenario3"],
        default="scenario1",
        help="Test mode to run"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Monitoring duration in seconds (for monitor modes)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  REAL-TIME DETECTION MONITOR")
    print("="*70)
    
    if args.mode == "monitor-cmd":
        monitor = RealtimeDetectionMonitor()
        monitor.initialize()
        monitor.monitor_commands(args.duration)
    
    elif args.mode == "monitor-net":
        monitor = RealtimeDetectionMonitor()
        monitor.initialize()
        monitor.monitor_network(args.duration)
    
    elif args.mode == "scenario1":
        test_scenario_1()
    
    elif args.mode == "scenario2":
        test_scenario_2()
    
    elif args.mode == "scenario3":
        test_scenario_3()
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
