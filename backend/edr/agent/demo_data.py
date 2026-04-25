"""
Demo data generators for EDR demonstrations.

These create realistic synthetic security events when:
- Windows Event Logs/APIs are unavailable
- Running in non-production environments
- Demonstrating system capabilities

Can be enabled via demo_mode flag in agent configuration.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

from backend.edr.models import EventType, Severity


class DemoDataGenerator:
    """Generate realistic synthetic security events for demonstrations."""

    def __init__(self):
        self.event_counter = 0
        self.sample_domains = [
            "microsoft.com", "google.com", "github.com",
            "suspicious-domain.xyz", "malware-c2.com",
            "data-exfil.ru", "botnet-command.biz"
        ]
        self.sample_processes = [
            "explorer.exe", "svchost.exe", "cmd.exe", "powershell.exe",
            "notepad.exe", "chrome.exe", "mimikatz.exe", "psexec.exe"
        ]
        self.sample_users = [
            "SYSTEM", "Administrator", "LocalService", "NetworkService",
            "attacker", "guest", "anonymous"
        ]

    def generate_failed_logins(self, count: int = 3) -> list[dict[str, Any]]:
        """Generate failed login attempt events."""
        events = []
        for i in range(count):
            events.append({
                "source": "demo_data",
                "event_type": EventType.SECURITY_EVENT.value,
                "title": f"failed_login_demo_{i}",
                "payload": {
                    "event_id": 4625,
                    "log_name": "Security",
                    "username": random.choice(self.sample_users),
                    "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
                    "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                    "failure_reason": "Bad password" if random.random() > 0.5 else "Account locked"
                }
            })
        return events

    def generate_privilege_escalation(self) -> dict[str, Any]:
        """Generate privilege escalation event."""
        return {
            "source": "demo_data",
            "event_type": EventType.SECURITY_EVENT.value,
            "title": "privilege_escalation_demo",
            "payload": {
                "event_id": 4672,
                "log_name": "Security",
                "username": "SYSTEM",
                "privileges": ["SeDebugPrivilege", "SeTcbPrivilege"],
                "timestamp": datetime.now().isoformat(),
                "source": random.choice(self.sample_processes)
            }
        }

    def generate_suspicious_process(self) -> dict[str, Any]:
        """Generate suspicious process execution event."""
        suspicious_process = random.choice([
            "cmd.exe", "powershell.exe", "mimikatz.exe", "psexec.exe"
        ])
        parent = random.choice(["explorer.exe", "svchost.exe", "services.exe"])
        
        return {
            "source": "demo_data",
            "event_type": EventType.PROCESS_INJECTION.value,
            "title": "suspicious_process_demo",
            "payload": {
                "pid": random.randint(1000, 9999),
                "process": suspicious_process,
                "parent_process": parent,
                "cmdline": f"{suspicious_process} /c whoami",
                "severity": "high" if suspicious_process in ["mimikatz.exe", "psexec.exe"] else "medium",
                "indicator": "suspicious_command_line" if "powershell" in suspicious_process else "suspicious_parent_child_relationship",
                "timestamp": datetime.now().isoformat()
            }
        }

    def generate_scheduled_task(self) -> dict[str, Any]:
        """Generate scheduled task creation event."""
        return {
            "source": "demo_data",
            "event_type": EventType.SECURITY_EVENT.value,
            "title": "scheduled_task_demo",
            "payload": {
                "event_id": 4698,
                "log_name": "Security",
                "task_name": f"\\\\{random.choice(['System', 'Microsoft', 'Malware'])}Task{random.randint(1, 100)}",
                "action": "cmd.exe /c powershell.exe -enc ...",
                "trigger": "On logon" if random.random() > 0.5 else "On schedule",
                "timestamp": datetime.now().isoformat()
            }
        }

    def generate_registry_modification(self) -> dict[str, Any]:
        """Generate registry modification event."""
        reg_key = random.choice([
            "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKLM\\System\\CurrentControlSet\\Services"
        ])
        
        return {
            "source": "demo_data",
            "event_type": EventType.REGISTRY_CHANGE.value,
            "title": "registry_modification_demo",
            "payload": {
                "registry_path": reg_key,
                "value_name": f"MalwareEntry{random.randint(1, 1000)}",
                "new_value": "C:\\\\Windows\\\\System32\\\\malware.exe",
                "timestamp": datetime.now().isoformat(),
                "severity": "high"
            }
        }

    def generate_dns_query(self, suspicious: bool = True) -> dict[str, Any]:
        """Generate DNS query event."""
        if suspicious:
            domain = random.choice([
                "malware-c2.com", "botnet-command.ru",
                "data-exfil.xyz", "command-control.biz"
            ])
            severity = "critical"
        else:
            domain = random.choice([
                "microsoft.com", "google.com", "github.com",
                "stackoverflow.com", "npmjs.com"
            ])
            severity = "low"
        
        return {
            "source": "demo_data",
            "event_type": EventType.DNS_QUERY.value,
            "title": f"dns_query_{'suspicious' if suspicious else 'normal'}_demo",
            "payload": {
                "domain": domain,
                "query_type": "A" if random.random() > 0.5 else "AAAA",
                "source_ip": "192.168.1.100",
                "response_ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                "timestamp": datetime.now().isoformat(),
                "severity": severity
            }
        }

    def generate_network_connection(self, suspicious: bool = False) -> dict[str, Any]:
        """Generate network connection event."""
        if suspicious:
            remote_ip = f"103.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            port = random.choice([4444, 5555, 6666, 8888, 9999])
            severity = "high"
        else:
            remote_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            port = random.choice([80, 443, 3389, 22])
            severity = "low"
        
        return {
            "source": "demo_data",
            "event_type": EventType.NETWORK.value,
            "title": f"network_connection_{'suspicious' if suspicious else 'normal'}_demo",
            "payload": {
                "process": random.choice(self.sample_processes),
                "local_ip": "192.168.1.100",
                "local_port": random.randint(49152, 65535),
                "remote_ip": remote_ip,
                "remote_port": port,
                "protocol": "TCP",
                "timestamp": datetime.now().isoformat(),
                "severity": severity
            }
        }

    def generate_file_activity(self, suspicious: bool = False) -> dict[str, Any]:
        """Generate file activity event."""
        if suspicious:
            filename = random.choice([
                "C:\\\\Windows\\\\System32\\\\malware.exe",
                "C:\\\\Users\\\\Public\\\\Downloads\\\\trojan.exe",
                "C:\\\\ProgramData\\\\backdoor.dll"
            ])
            activity = "create"
            severity = "high"
        else:
            filename = random.choice([
                "C:\\\\Users\\\\Documents\\\\report.docx",
                "C:\\\\Users\\\\Pictures\\\\vacation.jpg",
                "C:\\\\Program Files\\\\App\\\\config.ini"
            ])
            activity = random.choice(["read", "modify"])
            severity = "low"
        
        return {
            "source": "demo_data",
            "event_type": EventType.FILE.value,
            "title": f"file_{activity}_demo",
            "payload": {
                "filename": filename,
                "activity": activity,
                "process": random.choice(self.sample_processes),
                "timestamp": datetime.now().isoformat(),
                "severity": severity
            }
        }

    def generate_random_event(self) -> dict[str, Any]:
        """Generate a random security event for demo."""
        event_type = random.choice([
            self.generate_failed_logins,
            self.generate_suspicious_process,
            self.generate_dns_query,
            self.generate_network_connection,
            self.generate_file_activity,
        ])
        
        if callable(event_type) and event_type.__name__ == "generate_failed_logins":
            return event_type(1)[0]
        else:
            return event_type()

    def generate_demo_batch(self, count: int = 10) -> list[dict[str, Any]]:
        """Generate a batch of demo events."""
        events = []
        
        # Always include some failed logins
        events.extend(self.generate_failed_logins(random.randint(1, 3)))
        
        # Add occasional suspicious activity
        if random.random() > 0.5:
            events.append(self.generate_suspicious_process())
        
        if random.random() > 0.5:
            events.append(self.generate_dns_query(suspicious=True))
        
        if random.random() > 0.5:
            events.append(self.generate_scheduled_task())
        
        if random.random() > 0.5:
            events.append(self.generate_registry_modification())
        
        # Fill rest with normal activity
        while len(events) < count:
            events.append(self.generate_random_event())
        
        return events[:count]


# Singleton instance
_demo_generator = None


def get_demo_generator() -> DemoDataGenerator:
    """Get or create demo data generator."""
    global _demo_generator
    if _demo_generator is None:
        _demo_generator = DemoDataGenerator()
    return _demo_generator
