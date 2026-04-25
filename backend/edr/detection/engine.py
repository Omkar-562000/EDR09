from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Any

from backend.edr.detection.rules import Rule, RuleLoader
from backend.edr.models import Detection, Event, EventType, Severity


class DetectionEngine:
    def __init__(self, rule_loader: RuleLoader | None = None) -> None:
        self.rule_loader = rule_loader or RuleLoader()
        self.rules = self.rule_loader.load()
        self.state: dict[str, deque[datetime]] = defaultdict(deque)

    def reload_rules(self) -> None:
        self.rules = self.rule_loader.load()

    def evaluate(self, event: Event) -> list[Detection]:
        matches: list[Detection] = []
        for rule in self.rules:
            if rule.event_type != event.event_type.value:
                continue
            if self._matches_rule(rule, event):
                matches.append(
                    Detection(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        severity=Severity(rule.severity),
                        description=rule.description,
                        event=event,
                        confidence=rule.confidence,
                        tactics=rule.tactics,
                        techniques=rule.techniques,
                    )
                )
        return matches

    def _matches_rule(self, rule: Rule, event: Event) -> bool:
        payload = event.payload
        if rule.condition == "contains":
            target = str(payload.get(rule.match_field or "", "")).lower()
            return str(rule.value).lower() in target
        if rule.condition == "equals":
            return payload.get(rule.match_field or "") == rule.value
        if rule.condition == "in_list":
            target = str(payload.get(rule.match_field or "", "")).lower()
            return target in {str(item).lower() for item in (rule.value or [])}
        if rule.condition == "failed_login_threshold":
            return self._failed_login_threshold(rule, event)
        if rule.condition == "port_in_list":
            return int(payload.get(rule.match_field or "port", -1)) in set(rule.value or [])
        if rule.condition == "remote_ip_not_in_allowlist":
            remote_ip = payload.get(rule.match_field or "remote_ip")
            if not remote_ip:
                return False
            return remote_ip not in set(rule.value or [])
        return False

    def _failed_login_threshold(self, rule: Rule, event: Event) -> bool:
        if event.event_type != EventType.AUTH:
            return False
        username = str(event.payload.get("username", "unknown"))
        outcome = event.payload.get("outcome")
        if outcome != "failed":
            return False
        key = f"{rule.rule_id}:{username}"
        now = datetime.fromisoformat(event.timestamp)
        window = timedelta(seconds=rule.window_seconds or 300)
        bucket = self.state[key]
        bucket.append(now)
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        return len(bucket) >= int(rule.threshold or 5)
