from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from backend.edr.agent.service import EndpointAgent
from backend.edr.config.settings import QUEUE_POLL_TIMEOUT, ensure_directories
from backend.edr.database.storage import Storage
from backend.edr.detection.engine import DetectionEngine
from backend.edr.pipeline.dispatcher import Dispatcher
from backend.edr.pipeline.normalizer import EventNormalizer
from backend.edr.pipeline.queue_manager import EventQueue
from backend.edr.response.engine import ResponseEngine
from backend.edr.response.firewall import WindowsFirewallController
from backend.edr.models import ResponseAction


class EDRService:
    def __init__(self, watch_path: Path) -> None:
        ensure_directories()
        self.storage = Storage()
        self.event_queue = EventQueue()
        self.normalizer = EventNormalizer()
        self.detection_engine = DetectionEngine()
        self.response_engine = ResponseEngine()
        self.firewall = WindowsFirewallController()
        self.dispatcher = Dispatcher(
            storage=self.storage,
            detection_engine=self.detection_engine,
            response_engine=self.response_engine,
        )
        
        # Initialize agent with real Windows data collection
        self.agent = EndpointAgent(
            self.event_queue,
            watch_path=watch_path,
            interval_seconds=60,
        )
        self._pipeline_task: asyncio.Task[None] | None = None
        self._agent_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if not self._pipeline_task:
            self._pipeline_task = asyncio.create_task(self._run_pipeline())
        if not self._agent_task:
            self._agent_task = asyncio.create_task(self.agent.run())

    async def stop(self) -> None:
        self.agent.stop()
        for task in (self._agent_task, self._pipeline_task):
            if task:
                task.cancel()
        await asyncio.gather(*(task for task in (self._agent_task, self._pipeline_task) if task), return_exceptions=True)

    async def ingest_event(self, raw_event: dict[str, Any]) -> None:
        await self.event_queue.publish(raw_event)

    async def collect_once(self) -> None:
        await self.agent.collect_once()

    def agent_status(self) -> dict[str, Any]:
        return self.agent.status()

    def pause_agent(self) -> dict[str, Any]:
        self.agent.pause()
        return self.agent.status()

    def resume_agent(self) -> dict[str, Any]:
        self.agent.resume()
        return self.agent.status()

    def set_agent_interval(self, interval_seconds: float) -> dict[str, Any]:
        self.agent.set_interval(interval_seconds)
        return self.agent.status()

    def set_collector_enabled(self, collector_id: str, enabled: bool) -> dict[str, Any]:
        self.agent.set_collector_enabled(collector_id, enabled)
        return self.agent.status()

    def block_ip(self, ip_address: str, direction: str) -> dict[str, str]:
        result = self.firewall.block_ip(ip_address, direction)
        self.response_engine.blocked_ips.add(result.ip_address)
        self.storage.log_action(
            ResponseAction(
                action_type="firewall_block_ip",
                status="completed",
                target=result.ip_address,
                detection_id="manual-firewall",
                details={
                    "direction": result.direction,
                    "message": result.message,
                    "real_action": True,
                },
            )
        )
        return result.to_dict()

    def unblock_ip(self, ip_address: str, direction: str) -> dict[str, str]:
        result = self.firewall.unblock_ip(ip_address, direction)
        self.response_engine.blocked_ips.discard(result.ip_address)
        self.storage.log_action(
            ResponseAction(
                action_type="firewall_unblock_ip",
                status="completed",
                target=result.ip_address,
                detection_id="manual-firewall",
                details={
                    "direction": result.direction,
                    "message": result.message,
                    "real_action": True,
                },
            )
        )
        return result.to_dict()

    def check_ip_block(self, ip_address: str, direction: str) -> dict[str, object]:
        return self.firewall.check_ip(ip_address, direction)

    async def _run_pipeline(self) -> None:
        while True:
            try:
                raw_event = await asyncio.wait_for(self.event_queue.get(), timeout=QUEUE_POLL_TIMEOUT)
            except TimeoutError:
                continue
            try:
                event = self.normalizer.normalize(raw_event)
                self.dispatcher.dispatch(event)
            finally:
                self.event_queue.task_done()
