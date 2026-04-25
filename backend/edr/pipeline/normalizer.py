from __future__ import annotations

from typing import Any

from backend.edr.models import Event, EventType


class EventNormalizer:
    def normalize(self, raw_event: dict[str, Any]) -> Event:
        event_type = EventType(raw_event["event_type"])
        payload = raw_event.get("payload", {})
        payload.setdefault("normalized", True)
        event_kwargs = {
            "source": raw_event.get("source", "agent"),
            "event_type": event_type,
            "title": raw_event.get("title", event_type.value),
            "payload": payload,
            "host": raw_event.get("host", "endpoint-01"),
        }
        if raw_event.get("timestamp"):
            event_kwargs["timestamp"] = raw_event["timestamp"]
        return Event(
            **event_kwargs,
        )
