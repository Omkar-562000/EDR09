from __future__ import annotations

import asyncio
from pathlib import Path

from backend.edr.config.settings import BASE_DIR
from backend.edr.service import EDRService


async def run_flow() -> None:
    watch_path = BASE_DIR / "watched"
    service = EDRService(watch_path=watch_path)
    await service.start()

    try:
        for _ in range(5):
            await service.ingest_event(
                {
                    "source": "test",
                    "event_type": "auth",
                    "title": "failed_login",
                    "payload": {
                        "username": "alice",
                        "outcome": "failed",
                        "source_ip": "198.51.100.11",
                    },
                }
            )

        await service.ingest_event(
            {
                "source": "test",
                "event_type": "network",
                "title": "network_connection_observed",
                "payload": {
                    "remote_ip": "203.0.113.9",
                    "remote_port": 4444,
                    "status": "ESTABLISHED",
                },
            }
        )
        await asyncio.sleep(1.0)

        summary = service.storage.summary()
        assert summary["events"] >= 6
        assert summary["detections"] >= 2
        assert summary["actions"] >= 3
    finally:
        await service.stop()


def test_edr_flow() -> None:
    asyncio.run(run_flow())
