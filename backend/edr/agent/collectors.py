from __future__ import annotations

import json
import os
import socket
import subprocess
from pathlib import Path
from typing import Any

import psutil

from backend.edr.models import EventType


class ProcessCollector:
    def collect(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for proc in psutil.process_iter(["pid", "name", "cmdline", "username"]):
            try:
                info = proc.info
                cmdline = " ".join(info.get("cmdline") or [])
                if not cmdline and not info.get("name"):
                    continue
                events.append(
                    {
                        "source": "process_collector",
                        "event_type": EventType.PROCESS.value,
                        "title": "process_observed",
                        "payload": {
                            "pid": info.get("pid"),
                            "process_name": info.get("name"),
                            "cmdline": cmdline,
                            "username": info.get("username"),
                        },
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return events


class CommandActivityCollector:
    """Collect visible command-line activity from live processes and Windows 4688 logs when available."""

    command_processes = {
        "cmd.exe",
        "powershell.exe",
        "pwsh.exe",
        "ipconfig.exe",
        "whoami.exe",
        "net.exe",
        "net1.exe",
        "netstat.exe",
        "tasklist.exe",
        "reg.exe",
        "schtasks.exe",
        "wmic.exe",
        "certutil.exe",
        "bitsadmin.exe",
        "curl.exe",
        "rundll32.exe",
        "mshta.exe",
    }

    def __init__(self) -> None:
        self._seen_live_commands: set[str] = set()
        self._last_4688_record_id = 0

    def collect(self) -> list[dict[str, Any]]:
        events = self._collect_live_process_commands()
        events.extend(self._collect_windows_4688_commands())
        return events

    def _collect_live_process_commands(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for proc in psutil.process_iter(["pid", "name", "cmdline", "username", "ppid"]):
            try:
                info = proc.info
                process_name = (info.get("name") or "").lower()
                if process_name not in self.command_processes:
                    continue

                command_line = " ".join(info.get("cmdline") or [])
                command_key = f"{info.get('pid')}:{command_line}"
                if command_key in self._seen_live_commands:
                    continue
                self._seen_live_commands.add(command_key)

                events.append(
                    {
                        "source": "command_collector",
                        "event_type": EventType.COMMAND.value,
                        "title": "command_observed",
                        "payload": {
                            "pid": info.get("pid"),
                            "ppid": info.get("ppid"),
                            "process_name": info.get("name"),
                            "command_line": command_line or info.get("name"),
                            "username": info.get("username"),
                            "capture_method": "live_process",
                        },
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return events

    def _collect_windows_4688_commands(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            (
                "Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4688} -MaxEvents 20 "
                "-ErrorAction SilentlyContinue | "
                "Select-Object TimeCreated,RecordId,Message | ConvertTo-Json -Depth 3"
            ),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return events

        if result.returncode != 0 or not result.stdout.strip():
            return events

        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return events

        records = payload if isinstance(payload, list) else [payload]
        records.sort(key=lambda item: int(item.get("RecordId") or 0))
        for record in records:
            record_id = int(record.get("RecordId") or 0)
            if record_id <= self._last_4688_record_id:
                continue
            self._last_4688_record_id = max(self._last_4688_record_id, record_id)
            message = record.get("Message") or ""
            if not message:
                continue
            events.append(
                {
                    "source": "command_collector",
                    "event_type": EventType.COMMAND.value,
                    "title": "command_observed",
                    "timestamp": record.get("TimeCreated"),
                    "payload": {
                        "record_id": record_id,
                        "command_line": message,
                        "raw_log": message[:1000],
                        "capture_method": "windows_event_4688",
                    },
                }
            )
        return events


class NetworkCollector:
    def collect(self) -> list[dict[str, Any]]:
        host_ip = self._host_ip()
        events: list[dict[str, Any]] = []
        for conn in psutil.net_connections(kind="inet"):
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
            if not raddr:
                continue
            events.append(
                {
                    "source": "network_collector",
                    "event_type": EventType.NETWORK.value,
                    "title": "network_connection_observed",
                    "payload": {
                        "status": conn.status,
                        "local_address": laddr,
                        "remote_address": raddr,
                        "remote_ip": conn.raddr.ip,
                        "remote_port": conn.raddr.port,
                        "pid": conn.pid,
                        "host_ip": host_ip,
                    },
                }
            )
        return events

    def _host_ip(self) -> str:
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            return "127.0.0.1"


class FileCollector:
    def __init__(self, watch_path: Path) -> None:
        self.watch_path = watch_path
        self._known_state: dict[str, float] = {}

    def collect(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        if not self.watch_path.exists():
            return events
        for root, _, files in os.walk(self.watch_path):
            for filename in files:
                path = Path(root) / filename
                try:
                    mtime = path.stat().st_mtime
                except OSError:
                    continue
                key = str(path)
                previous = self._known_state.get(key)
                self._known_state[key] = mtime
                if previous is None:
                    continue
                if mtime > previous:
                    events.append(
                        {
                            "source": "file_collector",
                            "event_type": EventType.FILE.value,
                            "title": "file_modified",
                            "payload": {
                                "path": key,
                                "operation": "modified",
                                "mtime": mtime,
                            },
                        }
                    )
        return events
