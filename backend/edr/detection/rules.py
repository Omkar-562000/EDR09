from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from backend.edr.config.settings import RULES_PATH


@dataclass(slots=True)
class Rule:
    rule_id: str
    name: str
    event_type: str
    condition: str
    match_field: str | None = None
    operator: str | None = None
    value: Any = None
    threshold: int | None = None
    window_seconds: int | None = None
    severity: str = "medium"
    confidence: int = 70
    description: str = ""
    tactics: list[str] = field(default_factory=list)
    techniques: list[str] = field(default_factory=list)
    response_actions: list[str] = field(default_factory=list)


class RuleLoader:
    def __init__(self, rules_path: Path = RULES_PATH) -> None:
        self.rules_path = rules_path

    def load(self) -> list[Rule]:
        data = json.loads(self.rules_path.read_text(encoding="utf-8"))
        normalized_rules: list[Rule] = []
        for rule in data["rules"]:
            payload = dict(rule)
            if "field" in payload and "match_field" not in payload:
                payload["match_field"] = payload.pop("field")
            normalized_rules.append(Rule(**payload))
        return normalized_rules
