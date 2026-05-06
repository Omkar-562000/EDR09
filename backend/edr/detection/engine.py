from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import math
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
                self._annotate_match(rule, event)
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

    def _annotate_match(self, rule: Rule, event: Event) -> None:
        matched_value = self._matched_value(rule, event)
        if matched_value is None:
            return
        event.payload.setdefault("matched_rules", {})[rule.rule_id] = {
            "rule_name": rule.name,
            "field": rule.match_field,
            "matched_value": matched_value,
        }

    def _matches_rule(self, rule: Rule, event: Event) -> bool:
        payload = event.payload
        if rule.condition == "contains":
            return self._contains_any(payload.get(rule.match_field or ""), rule.value)
        if rule.condition == "equals":
            return self._values_equal(payload.get(rule.match_field or ""), rule.value)
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
        if rule.condition == "event_id_match":
            return self._values_equal(payload.get(rule.match_field or "event_id"), rule.value)
        if rule.condition in {"registry_persistence_check", "registry_path_contains"}:
            return self._contains_any(payload.get(rule.match_field or "registry_path"), rule.value)
        if rule.condition == "dns_c2_check":
            return self._contains_any(self._first_present(payload, ["domain", "query", "dns_activity"]), rule.value)
        if rule.condition == "dns_entropy_high":
            domain = str(self._first_present(payload, [rule.match_field or "domain", "query", "dns_activity"]) or "")
            return bool(domain) and self._shannon_entropy(domain) >= 3.8 and len(domain) >= 24
        if rule.condition == "injection_parent_child":
            return self._contains_any(payload.get(rule.match_field or "parent_process"), rule.value)
        if rule.condition == "command_line_contains":
            return self._contains_any(payload.get(rule.match_field or "cmdline"), rule.value)
        if rule.condition == "hollow_process_check":
            process = self._first_present(payload, [rule.match_field or "process_name", "process"])
            cmdline = str(payload.get("cmdline", "")).lower()
            suspicious_cmd = any(token in cmdline for token in ("-enc", "-nop", "hidden", "iex", "invoke-", "cmd.exe", "powershell"))
            return self._contains_any(process, rule.value) and suspicious_cmd
        if rule.condition == "network_share_access":
            return self._contains_any(payload.get(rule.match_field or "remote_path"), rule.value)
        if rule.condition == "large_outbound_transfer":
            return self._number(payload.get(rule.match_field or "bytes_sent")) >= self._number(rule.value)
        if rule.condition == "cloud_sync_unusual":
            return self._contains_any(payload.get(rule.match_field or "process_name"), rule.value)
        if rule.condition == "mass_file_encryption":
            extension = self._first_present(payload, [rule.match_field or "file_extension", "extension"])
            path = self._first_present(payload, ["path", "filename"])
            return self._contains_any(extension, rule.value) or self._contains_any(path, rule.value)
        if rule.condition == "lsass_memory_access":
            return self._contains_any(payload.get(rule.match_field or "target_process"), rule.value)
        return False

    def _contains_any(self, target: Any, expected: Any) -> bool:
        if target is None:
            return False
        target_text = str(target).lower()
        if isinstance(expected, list):
            return any(str(item).lower() in target_text for item in expected)
        return str(expected).lower() in target_text

    def _matched_value(self, rule: Rule, event: Event) -> str | None:
        payload = event.payload
        field = rule.match_field
        target = payload.get(field or "") if field else None
        if rule.condition == "contains":
            return self._first_matching_text(target, rule.value)
        if rule.condition == "command_line_contains":
            return self._first_matching_text(payload.get(field or "cmdline"), rule.value)
        if rule.condition == "in_list":
            return str(payload.get(field or "", "")) or None
        if rule.condition == "remote_ip_not_in_allowlist":
            return str(payload.get(field or "remote_ip", "")) or None
        if rule.condition == "event_id_match":
            return str(payload.get(field or "event_id", "")) or None
        return None

    def _first_matching_text(self, target: Any, expected: Any) -> str | None:
        if target is None:
            return None
        target_text = str(target).lower()
        if isinstance(expected, list):
            for item in expected:
                item_text = str(item)
                if item_text.lower() in target_text:
                    return item_text
            return None
        expected_text = str(expected)
        return expected_text if expected_text.lower() in target_text else None

    def _values_equal(self, left: Any, right: Any) -> bool:
        if left == right:
            return True
        return str(left).lower() == str(right).lower()

    def _first_present(self, payload: dict[str, Any], fields: list[str]) -> Any:
        for field in fields:
            value = payload.get(field)
            if value not in (None, ""):
                return value
        return None

    def _number(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _shannon_entropy(self, value: str) -> float:
        if not value:
            return 0.0
        frequencies = {char: value.count(char) for char in set(value)}
        length = len(value)
        return -sum((count / length) * math.log2(count / length) for count in frequencies.values())

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
