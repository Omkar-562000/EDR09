from __future__ import annotations

from backend.edr.detection.rules import RuleLoader
from backend.edr.models import Detection


class ResponseEngine:
    def __init__(self, rule_loader: RuleLoader | None = None) -> None:
        self.rule_loader = rule_loader or RuleLoader()
        self.rules_by_id = {rule.rule_id: rule for rule in self.rule_loader.load()}
        self.isolated_hosts: set[str] = set()
        self.blocked_ips: set[str] = set()
        self.terminated_processes: list[str] = []

    def reload_rules(self) -> None:
        self.rules_by_id = {rule.rule_id: rule for rule in self.rule_loader.load()}

    def execute(self, detection: Detection) -> list[object]:
        rule = self.rules_by_id.get(detection.rule_id)
        if not rule:
            return []
        return []
