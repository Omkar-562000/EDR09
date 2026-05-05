from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from backend.edr.models import Alert, Detection, Severity


class Aggregator:
    def __init__(self, storage, window_seconds: int = 300) -> None:
        self.storage = storage
        self.window = timedelta(seconds=window_seconds)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _merge_severity(self, current: Severity, incoming: Severity) -> Severity:
        order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return incoming if order.index(incoming) > order.index(current) else current

    def process_detection(self, detection: Detection) -> Alert:
        # Load recent alerts for same host and look for merge candidate
        recent = self.storage.recent_alerts(limit=50)
        candidate = None
        det_time = datetime.fromisoformat(detection.timestamp)
        for a in recent:
            if a["host"] != detection.event.host:
                continue
            last_seen = datetime.fromisoformat(a["last_seen"])
            if det_time - last_seen > self.window:
                continue
            # simple merge criteria: shared rule_id or shared event_id
            if detection.rule_id in a.get("rule_ids", []) or detection.event.event_id in a.get("detection_ids", []):
                candidate = a
                break
        if candidate:
            # update existing alert
            alert = Alert(
                alert_id=candidate["alert_id"],
                title=candidate["title"],
                host=candidate["host"],
                rule_ids=list({*candidate.get("rule_ids", []), detection.rule_id}),
                detection_ids=list({*candidate.get("detection_ids", []), detection.detection_id}),
                severity=self._merge_severity(Severity(candidate["severity"]), detection.severity),
                description=candidate["description"],
                created_at=candidate["created_at"],
                last_seen=self._now(),
            )
        else:
            # create new alert
            alert = Alert(
                alert_id=str(uuid4()),
                title=f"Alert: {detection.rule_name}",
                host=detection.event.host,
                rule_ids=[detection.rule_id],
                detection_ids=[detection.detection_id],
                severity=detection.severity,
                description=detection.description,
            )

        # persist and return
        self.storage.log_alert(alert)
        return alert
