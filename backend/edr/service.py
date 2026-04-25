from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from backend.edr.agent.service import EndpointAgent
from backend.edr.agent.config import get_agent_config
from backend.edr.config.settings import QUEUE_POLL_TIMEOUT, ensure_directories
from backend.edr.database.storage import Storage
from backend.edr.detection.engine import DetectionEngine
from backend.edr.pipeline.dispatcher import Dispatcher
from backend.edr.pipeline.normalizer import EventNormalizer
from backend.edr.pipeline.queue_manager import EventQueue
from backend.edr.response.engine import ResponseEngine


class EDRService:
    def __init__(self, watch_path: Path, demo_mode: bool = False) -> None:
        ensure_directories()
        self.storage = Storage()
        self.event_queue = EventQueue()
        self.normalizer = EventNormalizer()
        self.detection_engine = DetectionEngine()
        self.response_engine = ResponseEngine()
        self.dispatcher = Dispatcher(
            storage=self.storage,
            detection_engine=self.detection_engine,
            response_engine=self.response_engine,
        )
        
        # Initialize agent with configuration
        config = get_agent_config(demo_mode=demo_mode)
        self.agent = EndpointAgent(
            self.event_queue,
            watch_path=watch_path,
            interval_seconds=config.interval_seconds,
            demo_mode=config.demo_mode,
            enable_windows_collectors=config.enable_windows_event_logs,
        )
        self.demo_mode = demo_mode
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
