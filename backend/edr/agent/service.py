from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.edr.agent.collectors import FileCollector, NetworkCollector, ProcessCollector
from backend.edr.agent.windows_collectors import (
    WindowsEventLogCollector,
    RegistryCollector,
    DNSCollector,
    ProcessInjectionDetector,
)
from backend.edr.config.settings import DEFAULT_AGENT_INTERVAL
from backend.edr.pipeline.queue_manager import EventQueue


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CollectorSlot:
    collector_id: str
    label: str
    collector: Any
    enabled: bool = True


class EndpointAgent:
    """
    Endpoint agent for collecting real Windows telemetry.
    Uses Windows Event Logs, Registry monitoring, DNS queries, and process injection detection.
    """

    def __init__(
        self,
        event_queue: EventQueue,
        watch_path: Path,
        interval_seconds: float = 60,
    ) -> None:
        self.event_queue = event_queue
        self.interval_seconds = interval_seconds
        self.paused = False
        
        # Real data collectors
        self.collectors: list[CollectorSlot] = [
            CollectorSlot("process", "Processes", ProcessCollector()),
            CollectorSlot("network", "Network Connections", NetworkCollector()),
            CollectorSlot("file", "Watched Files", FileCollector(watch_path)),
            CollectorSlot("windows_event_log", "Windows Event Logs", WindowsEventLogCollector()),
            CollectorSlot("registry", "Registry Persistence Keys", RegistryCollector()),
            CollectorSlot("dns", "DNS Activity", DNSCollector()),
            CollectorSlot("process_injection", "Process Injection Indicators", ProcessInjectionDetector()),
        ]
        
        self._running = False

    async def run(self) -> None:
        """Run the agent in collection loop."""
        self._running = True
        while self._running:
            await self.collect_once()
            await asyncio.sleep(self.interval_seconds)

    async def collect_once(self, force: bool = False) -> None:
        """Collect events from all enabled collectors."""
        if self.paused and not force:
            return

        for slot in self.collectors:
            if not slot.enabled:
                continue
            try:
                events = slot.collector.collect()
                for event in events:
                    await self.event_queue.publish(event)
            except Exception:
                logger.exception("%s failed during telemetry collection", slot.label)

    def stop(self) -> None:
        """Stop the agent."""
        self._running = False

    def pause(self) -> None:
        """Pause scheduled collection without stopping the backend."""
        self.paused = True

    def resume(self) -> None:
        """Resume scheduled collection."""
        self.paused = False

    def set_interval(self, interval_seconds: float) -> None:
        """Set collection interval for the running agent loop."""
        self.interval_seconds = interval_seconds

    def set_collector_enabled(self, collector_id: str, enabled: bool) -> None:
        """Enable or disable a collector by stable ID."""
        for slot in self.collectors:
            if slot.collector_id == collector_id:
                slot.enabled = enabled
                return
        raise KeyError(collector_id)

    def get_collector_status(self) -> list[dict[str, Any]]:
        """Return status of all collectors."""
        return [
            {
                "id": slot.collector_id,
                "label": slot.label,
                "class_name": slot.collector.__class__.__name__,
                "enabled": slot.enabled,
                "available": hasattr(slot.collector, "collect"),
            }
            for slot in self.collectors
        ]

    def status(self) -> dict[str, Any]:
        """Return runtime collection status."""
        return {
            "running": self._running,
            "paused": self.paused,
            "interval_seconds": self.interval_seconds,
            "collectors": self.get_collector_status(),
        }
