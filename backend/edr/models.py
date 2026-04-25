from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventType(str, Enum):
    PROCESS = "process"
    NETWORK = "network"
    FILE = "file"
    AUTH = "auth"
    SYSTEM = "system"
    SECURITY_EVENT = "security_event"
    SYSTEM_EVENT = "system_event"
    REGISTRY_CHANGE = "registry_change"
    DNS_QUERY = "dns_query"
    PROCESS_INJECTION = "process_injection"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Event:
    source: str
    event_type: EventType
    title: str
    payload: dict[str, Any]
    timestamp: str = field(default_factory=utc_now)
    host: str = "endpoint-01"
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "host": self.host,
            "source": self.source,
            "event_type": self.event_type.value,
            "title": self.title,
            "payload": self.payload,
        }


@dataclass(slots=True)
class Detection:
    rule_id: str
    rule_name: str
    severity: Severity
    description: str
    event: Event
    confidence: int
    tactics: list[str] = field(default_factory=list)
    techniques: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=utc_now)
    detection_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "timestamp": self.timestamp,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "description": self.description,
            "confidence": self.confidence,
            "tactics": self.tactics,
            "techniques": self.techniques,
            "event": self.event.to_dict(),
        }


@dataclass(slots=True)
class ResponseAction:
    action_type: str
    status: str
    target: str
    detection_id: str
    details: dict[str, Any]
    timestamp: str = field(default_factory=utc_now)
    action_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "timestamp": self.timestamp,
            "action_type": self.action_type,
            "status": self.status,
            "target": self.target,
            "detection_id": self.detection_id,
            "details": self.details,
        }
