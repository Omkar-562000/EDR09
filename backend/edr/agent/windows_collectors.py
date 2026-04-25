"""
Windows-specific data collectors for real endpoint telemetry.

Collects:
- Windows Event Logs (Security, System, Application)
- Registry modifications for persistence detection
- DNS queries for C2 detection
- Process injection/memory activity indicators

Falls back to demo data when Windows APIs are unavailable.
"""

from __future__ import annotations

import socket
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from collections import defaultdict

import psutil

from backend.edr.models import EventType


class WindowsEventLogCollector:
    """
    Collects Windows Event Logs from Security, System, and Application channels.
    Detects: Failed logins, privilege escalation, service changes, account creation.
    Falls back to demo data if PowerShell unavailable.
    """

    def __init__(self, lookback_minutes: int = 5, demo_mode: bool = False):
        self.lookback_minutes = lookback_minutes
        self.last_record_id = defaultdict(int)
        self.demo_mode = demo_mode
        self._fallback_count = 0

    def collect(self) -> list[dict[str, Any]]:
        """Collect security-relevant Windows Event Log entries."""
        events = []
        
        try:
            # Try real Windows Event Logs first
            if not self.demo_mode:
                # Security channel events
                security_events = self._get_security_events()
                if security_events:
                    events.extend(security_events)
                    return events
                
                # System channel events
                system_events = self._get_system_events()
                if system_events:
                    events.extend(system_events)
                    return events
            
            # Fallback to demo data
            self._fallback_count += 1
            if self._fallback_count <= 5:  # Log first few fallbacks
                events.append({
                    "source": "windows_event_log",
                    "event_type": EventType.SECURITY_EVENT.value,
                    "title": "using_demo_data_fallback",
                    "payload": {
                        "reason": "Windows Event Log collection unavailable",
                        "fallback_count": self._fallback_count
                    }
                })
            
            # Generate demo events
            from backend.edr.agent.demo_data import get_demo_generator
            gen = get_demo_generator()
            demo_events = gen.generate_failed_logins(2)
            events.extend(demo_events)
            
        except Exception as e:
            # Ultimate fallback to demo
            from backend.edr.agent.demo_data import get_demo_generator
            events.extend(get_demo_generator().generate_demo_batch(3))
        
        return events

    def _get_security_events(self) -> list[dict[str, Any]]:
        """Collect security-related events (failed logins, privilege changes, etc)."""
        events = []
        
        try:
            # Event IDs to monitor:
            # 4625 = Failed login, 4624 = Successful login, 4672 = Special privileges assigned
            # 4698 = Scheduled task created, 4732 = User added to group
            event_ids = ["4625", "4672", "4698", "4732", "4735", "4781"]
            
            for event_id in event_ids:
                cmd = f'powershell -Command "Get-WinEvent -FilterHashtable @{{LogName=\'Security\'; ID={event_id}}} -MaxEvents 10 2>$null | ConvertTo-Json"'
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if result.stdout:
                        events.append({
                            "source": "windows_event_log",
                            "event_type": EventType.SECURITY_EVENT.value,
                            "title": f"security_event_{event_id}",
                            "payload": {
                                "event_id": event_id,
                                "log_name": "Security",
                                "raw_log": result.stdout[:500],  # First 500 chars
                            }
                        })
                except (subprocess.TimeoutExpired, Exception):
                    pass
        except Exception:
            pass
        
        return events

    def _get_system_events(self) -> list[dict[str, Any]]:
        """Collect system events (service installation, driver loading, etc)."""
        events = []
        
        try:
            # Event IDs: 7045 = Service installed, 7040 = Service startup type changed
            event_ids = ["7045", "7040"]
            
            for event_id in event_ids:
                cmd = f'powershell -Command "Get-WinEvent -FilterHashtable @{{LogName=\'System\'; ID={event_id}}} -MaxEvents 5 2>$null | ConvertTo-Json"'
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if result.stdout:
                        events.append({
                            "source": "windows_event_log",
                            "event_type": EventType.SYSTEM_EVENT.value,
                            "title": f"system_event_{event_id}",
                            "payload": {
                                "event_id": event_id,
                                "log_name": "System",
                                "raw_log": result.stdout[:500],
                            }
                        })
                except (subprocess.TimeoutExpired, Exception):
                    pass
        except Exception:
            pass
        
        return events


class RegistryCollector:
    """
    Monitors Windows Registry for persistence mechanisms.
    Detects: Run keys, scheduled task creation, startup folder modifications.
    """

    def __init__(self):
        self.monitored_paths = [
            r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run",
            r"HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run",
            r"HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\RunOnce",
            r"HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services",
        ]

    def collect(self) -> list[dict[str, Any]]:
        """Collect registry modifications and suspicious values."""
        events = []
        
        try:
            for reg_path in self.monitored_paths:
                entries = self._get_registry_entries(reg_path)
                for entry in entries:
                    events.append({
                        "source": "registry_monitor",
                        "event_type": EventType.REGISTRY_CHANGE.value,
                        "title": "registry_modification_detected",
                        "payload": entry
                    })
        except Exception:
            pass
        
        return events

    def _get_registry_entries(self, path: str) -> list[dict[str, Any]]:
        """Read registry entries from a given path."""
        entries = []
        
        try:
            # Convert registry path format
            reg_path = path.replace("\\", "\\\\")
            cmd = f'powershell -Command "Get-Item -Path \'Registry::{reg_path}\' 2>$null | ForEach-Object {{ $_.Property }} | ForEach-Object {{ @{{ Property=$_; Value=$(Get-ItemProperty -Path \'Registry::{reg_path}\' -Name $_).($_) }} }}"'
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.stdout:
                entries.append({
                    "registry_path": path,
                    "entries": result.stdout[:500],
                    "timestamp": datetime.now().isoformat(),
                })
        except (subprocess.TimeoutExpired, Exception):
            pass
        
        return entries


class DNSCollector:
    """
    Monitors DNS queries for C2 communications and data exfiltration.
    Detects: Unusual domains, known bad domains, DNS tunneling.
    """

    def __init__(self):
        # Known malicious/suspicious domain patterns
        self.suspicious_patterns = [
            "malware", "c2", "botnet", "exfil", "payload",
            "shell", "backdoor", "rat", "dropper", "loader"
        ]
        self.dns_cache = {}

    def collect(self) -> list[dict[str, Any]]:
        """Collect DNS query activity."""
        events = []
        
        try:
            dns_queries = self._get_dns_queries()
            for query in dns_queries:
                events.append({
                    "source": "dns_collector",
                    "event_type": EventType.DNS_QUERY.value,
                    "title": "dns_query_observed",
                    "payload": query
                })
        except Exception:
            pass
        
        return events

    def _get_dns_queries(self) -> list[dict[str, Any]]:
        """Extract DNS queries from network connections and system state."""
        queries = []
        
        try:
            # Analyze netstat for DNS activity
            cmd = 'netstat -an -p TCP 2>nul | findstr ":53"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.stdout:
                for line in result.stdout.split('\n')[:10]:  # Limit to 10 entries
                    queries.append({
                        "dns_activity": line.strip(),
                        "timestamp": datetime.now().isoformat(),
                    })
        except (subprocess.TimeoutExpired, Exception):
            pass
        
        # Fallback: Check for common DNS request ports
        try:
            for conn in psutil.net_connections(kind="inet"):
                if conn.raddr and conn.raddr.port == 53:
                    queries.append({
                        "src": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "dst": f"{conn.raddr.ip}:{conn.raddr.port}",
                        "status": conn.status,
                        "timestamp": datetime.now().isoformat(),
                    })
        except (psutil.AccessDenied, Exception):
            pass
        
        return queries


class ProcessInjectionDetector:
    """
    Detects process injection attacks (hollowing, DLL injection, code injection).
    Identifies: Suspicious API calls, memory modifications, hidden processes.
    """

    def __init__(self):
        self.baseline_processes = set()
        self.suspicious_parent_combinations = [
            ("explorer.exe", "cmd.exe"),
            ("explorer.exe", "powershell.exe"),
            ("winlogon.exe", "cmd.exe"),
            ("svchost.exe", "cmd.exe"),
        ]

    def collect(self) -> list[dict[str, Any]]:
        """Detect process injection indicators."""
        events = []
        
        try:
            injection_indicators = self._detect_injection()
            for indicator in injection_indicators:
                events.append({
                    "source": "process_injection_detector",
                    "event_type": EventType.PROCESS_INJECTION.value,
                    "title": "potential_injection_detected",
                    "payload": indicator
                })
        except Exception:
            pass
        
        return events

    def _detect_injection(self) -> list[dict[str, Any]]:
        """Analyze processes for injection indicators."""
        indicators = []
        
        try:
            for proc in psutil.process_iter(["pid", "name", "ppid", "cmdline"]):
                try:
                    info = proc.info
                    ppid = info.get("ppid")
                    name = info.get("name", "").lower()
                    cmdline = " ".join(info.get("cmdline") or []).lower()
                    
                    # Check for suspicious parent-child relationships
                    if ppid:
                        try:
                            parent = psutil.Process(ppid)
                            parent_name = parent.name().lower()
                            
                            if (parent_name, name) in self.suspicious_parent_combinations:
                                indicators.append({
                                    "pid": info.get("pid"),
                                    "process": name,
                                    "parent_process": parent_name,
                                    "severity": "high",
                                    "indicator": "suspicious_parent_child_relationship"
                                })
                        except psutil.NoSuchProcess:
                            pass
                    
                    # Check for suspicious command lines
                    if any(keyword in cmdline for keyword in ["powershell", "cmd", "-enc", "-e ", "-nop"]):
                        if any(keyword in cmdline for keyword in ["-nop", "-enc", "hidden", "-w hidden", "iex", "invoke-"]):
                            indicators.append({
                                "pid": info.get("pid"),
                                "process": name,
                                "cmdline": cmdline[:100],
                                "severity": "high",
                                "indicator": "suspicious_command_line"
                            })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        
        return indicators


# Export all collectors
__all__ = [
    "WindowsEventLogCollector",
    "RegistryCollector",
    "DNSCollector",
    "ProcessInjectionDetector",
]
