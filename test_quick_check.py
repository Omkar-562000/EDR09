#!/usr/bin/env python
"""
Quick Verification Script - Fast checks for CMD detection and IP blocking
Run this for quick system health check
"""

import subprocess
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def check_backend_running() -> bool:
    """Check if backend is accessible"""
    print("\n🔍 Checking if backend is running...")
    try:
        import urllib.request
        import urllib.error
        with urllib.request.urlopen("http://localhost:8000/api/health", timeout=2) as response:
            print("   ✓ Backend is running and responding")
            return True
    except (urllib.error.URLError, TimeoutError):
        print("   ✗ Backend not accessible (start with: python main.py)")
        return False


def check_real_data_collection() -> bool:
    """Quick check that real data is being collected"""
    print("\n🔍 Checking real data collection...")
    try:
        from backend.edr.agent.collectors import CommandActivityCollector
        
        collector = CommandActivityCollector()
        events = collector.collect()
        
        if events:
            print(f"   ✓ Collected {len(events)} real commands")
            print(f"     Sample: {events[0]['payload']['process_name']}")
            return True
        else:
            print("   ⚠ No commands collected (try running cmd.exe or powershell)")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def check_detection_engine() -> bool:
    """Check if detection rules are loaded"""
    print("\n🔍 Checking detection engine...")
    try:
        from backend.edr.detection.engine import DetectionEngine
        
        engine = DetectionEngine()
        if len(engine.rules) > 0:
            print(f"   ✓ Loaded {len(engine.rules)} detection rules")
            
            # Show some rules
            cmd_rules = [r for r in engine.rules if r.rule_id.startswith("CMD")]
            net_rules = [r for r in engine.rules if r.rule_id.startswith("NET")]
            
            print(f"     - CMD Detection Rules: {len(cmd_rules)}")
            print(f"     - Network Detection Rules: {len(net_rules)}")
            return True
        else:
            print("   ✗ No detection rules loaded")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def check_firewall_access() -> bool:
    """Check if we can access Windows Firewall"""
    print("\n🔍 Checking Windows Firewall access...")
    
    if sys.platform != "win32":
        print("   ⚠ Not Windows - firewall checks skipped")
        return True
    
    try:
        from backend.edr.response.firewall import WindowsFirewallController
        
        controller = WindowsFirewallController()
        
        # Try to check a safe IP
        result = controller.check_ip("127.0.0.1")
        
        if result["ip_address"]:
            print("   ✓ Can access Windows Firewall")
            return True
        else:
            print("   ✗ Cannot access Windows Firewall")
            return False
    except Exception as e:
        if "not found" in str(e).lower():
            print("   ⚠ Must run as Administrator for firewall access")
            print("     (Restart PowerShell with: Start-Process powershell -Verb RunAs)")
            return False
        else:
            print(f"   ✗ Error: {e}")
            return False


def quick_detection_test() -> bool:
    """Quick test of detection engine"""
    print("\n🔍 Testing detection engine...")
    try:
        from backend.edr.detection.engine import DetectionEngine
        from backend.edr.models import Event, EventType
        
        engine = DetectionEngine()
        
        # Test suspicious command
        event = Event(
            source="test",
            event_type=EventType.COMMAND,
            title="test",
            payload={
                "command_line": "powershell.exe -enc JABzAD0A",
                "process_name": "powershell.exe"
            }
        )
        
        detections = engine.evaluate(event)
        
        if len(detections) > 0:
            print(f"   ✓ Detected suspicious command (Rule: {detections[0].rule_id})")
            return True
        else:
            print("   ✗ Failed to detect suspicious command")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def check_database() -> bool:
    """Check if database is accessible"""
    print("\n🔍 Checking database...")
    try:
        from backend.edr.database.storage import Storage
        
        storage = Storage()
        
        # Try a simple query
        events = storage.recent_events(limit=1)
        
        print(f"   ✓ Database accessible")
        print(f"     - Total events stored: {len(storage.get_all_events())}")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main() -> None:
    print("\n" + "="*70)
    print("  EDR SYSTEM - QUICK VERIFICATION")
    print("  Testing CMD Detection & IP Blocking")
    print("="*70)
    
    checks = {
        "Backend Running": check_backend_running(),
        "Real Data Collection": check_real_data_collection(),
        "Detection Engine": check_detection_engine(),
        "Firewall Access": check_firewall_access(),
        "Detection Test": quick_detection_test(),
        "Database": check_database(),
    }
    
    print_header("VERIFICATION RESULTS")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ ALL SYSTEMS READY!")
        print("\nNext steps:")
        print("  1. Start backend: python main.py")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Open dashboard: http://localhost:5174")
        print("  4. Run full tests: python test_edr_comprehensive.py")
    else:
        print(f"\n⚠ {total - passed} issue(s) to resolve")
        print("\nTroubleshooting:")
        print("  - Ensure backend is running: python main.py")
        print("  - Run as Administrator (for firewall access)")
        print("  - Check Python 3.11+ installed: python --version")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
