#!/usr/bin/env python
"""
External CMD Monitoring Verification
Monitor commands from a remote machine by polling the API
"""

import json
import time
import sys
import argparse
from typing import List, Dict, Any
from datetime import datetime


def fetch_from_api(api_url: str, endpoint: str, timeout: int = 5) -> Dict[str, Any]:
    """Fetch data from remote API"""
    try:
        import urllib.request
        import urllib.error
        
        url = f"{api_url.rstrip('/')}/{endpoint}"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except Exception as e:
        return {"error": str(e), "data": []}


class RemoteCMDMonitor:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")
        self.seen_events = set()
        self.test_connection()
    
    def test_connection(self) -> bool:
        """Test if API is accessible"""
        result = fetch_from_api(self.api_url, "api/health")
        if "error" in result:
            print(f"❌ Cannot connect to API: {result['error']}")
            print(f"   Make sure backend is running: python main.py")
            sys.exit(1)
        return True
    
    def fetch_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent events from remote API"""
        result = fetch_from_api(self.api_url, f"api/events?limit={limit}")
        return result.get("data", [])
    
    def fetch_detections(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch detected threats from remote API"""
        result = fetch_from_api(self.api_url, f"api/detections?limit={limit}")
        return result.get("data", [])
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return fetch_from_api(self.api_url, "api/status")
    
    def monitor_commands(self, duration_seconds: int = 60, interval: int = 5):
        """Monitor commands in real-time"""
        print(f"\n{'='*70}")
        print(f"  MONITORING COMMANDS - Real-Time")
        print(f"{'='*70}")
        
        print(f"\n📡 Monitoring for {duration_seconds} seconds...")
        print(f"   API: {self.api_url}")
        print(f"   Polling interval: {interval}s")
        print(f"   Status: Listening for new commands...\n")
        
        end_time = time.time() + duration_seconds
        command_count = 0
        last_check = 0
        
        while time.time() < end_time:
            try:
                current_time = time.time()
                
                # Only fetch every interval seconds
                if current_time - last_check >= interval:
                    events = self.fetch_events(limit=50)
                    last_check = current_time
                    
                    for event in events:
                        event_id = event.get("event_id")
                        
                        # Skip if already seen
                        if event_id in self.seen_events:
                            continue
                        
                        self.seen_events.add(event_id)
                        command_count += 1
                        
                        # Print new command
                        payload = event.get("payload", {})
                        timestamp = event.get("timestamp", "N/A")
                        source = event.get("source", "unknown")
                        event_type = event.get("event_type", "UNKNOWN")
                        
                        # Only show command/process events
                        if event_type in ["COMMAND", "PROCESS"]:
                            print(f"🔵 NEW COMMAND #{command_count}")
                            print(f"   Time: {timestamp}")
                            print(f"   Process: {payload.get('process_name', 'N/A')}")
                            print(f"   Command: {payload.get('command_line', 'N/A')[:100]}...")
                            if payload.get('pid'):
                                print(f"   PID: {payload.get('pid')}")
                            if payload.get('username'):
                                print(f"   User: {payload.get('username')}")
                            print()
                
                time.sleep(0.5)  # Check every 500ms
            
            except KeyboardInterrupt:
                print("\n⏹ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"⚠ Error: {e}")
                time.sleep(interval)
        
        print(f"\n{'='*70}")
        print(f"✅ Monitoring complete")
        print(f"   Total commands captured: {command_count}")
        print(f"{'='*70}\n")
    
    def monitor_detections(self, duration_seconds: int = 60, interval: int = 5):
        """Monitor detections/threats in real-time"""
        print(f"\n{'='*70}")
        print(f"  MONITORING THREATS - Real-Time")
        print(f"{'='*70}")
        
        print(f"\n🚨 Monitoring for {duration_seconds} seconds...")
        print(f"   API: {self.api_url}")
        print(f"   Polling interval: {interval}s")
        print(f"   Status: Listening for detections...\n")
        
        end_time = time.time() + duration_seconds
        detection_count = 0
        last_check = 0
        
        while time.time() < end_time:
            try:
                current_time = time.time()
                
                if current_time - last_check >= interval:
                    detections = self.fetch_detections(limit=50)
                    last_check = current_time
                    
                    for detection in detections:
                        detection_id = detection.get("detection_id")
                        
                        if detection_id in self.seen_events:
                            continue
                        
                        self.seen_events.add(detection_id)
                        detection_count += 1
                        
                        print(f"🚨 THREAT DETECTED #{detection_count}")
                        print(f"   Rule: {detection.get('rule_id', 'UNKNOWN')}")
                        print(f"   Name: {detection.get('rule_name', 'N/A')}")
                        print(f"   Severity: {detection.get('severity', 'N/A')}")
                        print(f"   Confidence: {detection.get('confidence', 'N/A')}%")
                        print(f"   Time: {detection.get('timestamp', 'N/A')}")
                        if detection.get('details'):
                            print(f"   Details: {str(detection.get('details'))[:80]}...")
                        print()
                
                time.sleep(0.5)
            
            except KeyboardInterrupt:
                print("\n⏹ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"⚠ Error: {e}")
                time.sleep(interval)
        
        print(f"\n{'='*70}")
        print(f"✅ Monitoring complete")
        print(f"   Total threats detected: {detection_count}")
        print(f"{'='*70}\n")
    
    def show_status(self):
        """Display system status"""
        print(f"\n{'='*70}")
        print(f"  EDR SYSTEM STATUS")
        print(f"{'='*70}\n")
        
        try:
            data = self.get_status()
            
            if "error" in data:
                print(f"❌ Error: {data['error']}")
                return
            
            print(f"✓ API Status: {data.get('status', 'unknown').upper()}")
            print(f"✓ Total Events: {data.get('events', 0):,}")
            print(f"✓ Total Detections: {data.get('detections', 0):,}")
            print(f"✓ Total Actions: {data.get('actions', 0):,}")
            
            if data.get('last_event'):
                print(f"✓ Last Event: {data.get('last_event')}")
            
            if data.get('last_detection'):
                print(f"✓ Last Detection: {data.get('last_detection')}")
            
            print(f"\n{'='*70}\n")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def show_recent_commands(self, count: int = 10):
        """Display recent commands"""
        print(f"\n{'='*70}")
        print(f"  RECENT COMMANDS (Last {count})")
        print(f"{'='*70}\n")
        
        events = self.fetch_events(limit=count)
        
        if not events:
            print("No commands found")
            return
        
        for i, event in enumerate(events, 1):
            payload = event.get("payload", {})
            timestamp = event.get("timestamp", "N/A")
            
            print(f"{i}. {timestamp}")
            print(f"   Process: {payload.get('process_name', 'N/A')}")
            print(f"   Command: {payload.get('command_line', 'N/A')[:80]}...")
            print()
        
        print(f"{'='*70}\n")
    
    def show_recent_detections(self, count: int = 10):
        """Display recent detections"""
        print(f"\n{'='*70}")
        print(f"  RECENT DETECTIONS (Last {count})")
        print(f"{'='*70}\n")
        
        detections = self.fetch_detections(limit=count)
        
        if not detections:
            print("No detections found")
            return
        
        for i, detection in enumerate(detections, 1):
            print(f"{i}. {detection.get('timestamp', 'N/A')}")
            print(f"   Rule: {detection.get('rule_id')}")
            print(f"   Severity: {detection.get('severity')}")
            print(f"   Details: {str(detection.get('details'))[:80]}...")
            print()
        
        print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="External CMD Monitoring - Verify monitoring from remote machine"
    )
    parser.add_argument(
        "api_url",
        help="API URL (e.g., http://192.168.1.100:8000)"
    )
    parser.add_argument(
        "--mode",
        choices=["commands", "detections", "status", "recent-commands", "recent-detections"],
        default="commands",
        help="Monitoring mode"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Monitoring duration in seconds (for real-time modes)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Polling interval in seconds"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of items to display (for recent modes)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("  EXTERNAL CMD MONITORING VERIFICATION")
    print("="*70)
    
    monitor = RemoteCMDMonitor(args.api_url)
    
    if args.mode == "commands":
        monitor.monitor_commands(args.duration, args.interval)
    elif args.mode == "detections":
        monitor.monitor_detections(args.duration, args.interval)
    elif args.mode == "status":
        monitor.show_status()
    elif args.mode == "recent-commands":
        monitor.show_recent_commands(args.count)
    elif args.mode == "recent-detections":
        monitor.show_recent_detections(args.count)


if __name__ == "__main__":
    main()
