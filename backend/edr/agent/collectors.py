from __future__ import annotations

import os
import socket
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
