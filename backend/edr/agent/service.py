from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable

from backend.edr.agent.collectors import FileCollector, NetworkCollector, ProcessCollector
from backend.edr.agent.windows_collectors import (
    WindowsEventLogCollector,
    RegistryCollector,
    DNSCollector,
    ProcessInjectionDetector,
)
from backend.edr.config.settings import DEFAULT_AGENT_INTERVAL
from backend.edr.pipeline.queue_manager import EventQueue


class EndpointAgent:
    """
    Hybrid endpoint agent supporting local and remote data collection.
    Collects real Windows telemetry with fallback to demo mode.
    """

    def __init__(
        self,
        event_queue: EventQueue,
        watch_path: Path,
        interval_seconds: float = 60,  # 60 seconds for low overhead
        demo_mode: bool = False,
        enable_windows_collectors: bool = True,
    ) -> None:
        self.event_queue = event_queue
        self.interval_seconds = interval_seconds
        self.demo_mode = demo_mode
        self.enable_windows_collectors = enable_windows_collectors
        
        # Base collectors (always enabled)
        self.collectors = [
            ProcessCollector(),
            NetworkCollector(),
            FileCollector(watch_path),
        ]
        
        # Windows-specific collectors (enabled by default, graceful fallback)
        if enable_windows_collectors:
            self.collectors.extend([
                WindowsEventLogCollector(),
                RegistryCollector(),
                DNSCollector(),
                ProcessInjectionDetector(),
            ])
        
        self._running = False

    async def run(self) -> None:
        """Run the agent in collection loop."""
        self._running = True
        while self._running:
            await self.collect_once()
            await asyncio.sleep(self.interval_seconds)

    async def collect_once(self) -> None:
        """Collect events from all enabled collectors."""
        for collector in self.collectors:
            try:
                events = collector.collect()
                for event in events:
                    await self.event_queue.publish(event)
            except Exception as e:
                # Graceful degradation - log and continue
                if self.demo_mode:
                    # In demo mode, generate synthetic event on collector failure
                    await self.event_queue.publish({
                        "source": "agent_health",
                        "event_type": "system",
                        "title": "collector_fallback_to_demo",
                        "payload": {
                            "collector": collector.__class__.__name__,
                            "error": str(e)
                        }
                    })

    def stop(self) -> None:
        """Stop the agent."""
        self._running = False

    def set_demo_mode(self, enabled: bool) -> None:
        """Enable/disable demo mode for synthetic data generation."""
        self.demo_mode = enabled

    def get_collector_status(self) -> dict[str, bool]:
        """Return status of all collectors."""
        return {
            collector.__class__.__name__: hasattr(collector, 'collect')
            for collector in self.collectors
        }
