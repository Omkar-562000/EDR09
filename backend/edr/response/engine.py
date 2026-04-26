from __future__ import annotations

from backend.edr.detection.rules import RuleLoader
from backend.edr.models import Detection, ResponseAction


class ResponseEngine:
    def __init__(self, rule_loader: RuleLoader | None = None) -> None:
        self.rule_loader = rule_loader or RuleLoader()
        self.rules_by_id = {rule.rule_id: rule for rule in self.rule_loader.load()}
        self.isolated_hosts: set[str] = set()
        self.blocked_ips: set[str] = set()
        self.terminated_processes: list[str] = []

    def reload_rules(self) -> None:
        self.rules_by_id = {rule.rule_id: rule for rule in self.rule_loader.load()}

    def execute(self, detection: Detection) -> list[ResponseAction]:
        rule = self.rules_by_id.get(detection.rule_id)
        if not rule:
            return []
        actions: list[ResponseAction] = []
        for action_name in rule.response_actions:
            action = self._run_action(action_name, detection)
            if action:
                actions.append(action)
        return actions

    def _run_action(self, action_name: str, detection: Detection) -> ResponseAction | None:
        payload = detection.event.payload
        target = detection.event.host
        details = {"rule_id": detection.rule_id, "rule_name": detection.rule_name}
        if action_name == "kill_process":
            process_name = payload.get("process_name") or payload.get("process") or "unknown"
            self.terminated_processes.append(process_name)
            return ResponseAction(
                action_type=action_name,
                status="simulated_success",
                target=process_name,
                detection_id=detection.detection_id,
                details={**details, "message": f"Process {process_name} terminated"},
            )
        if action_name == "block_ip":
            remote_ip = payload.get("remote_ip", "unknown")
            self.blocked_ips.add(remote_ip)
            return ResponseAction(
                action_type=action_name,
                status="simulated_success",
                target=remote_ip,
                detection_id=detection.detection_id,
                details={**details, "message": f"IP {remote_ip} blocked"},
            )
        if action_name == "isolate_host":
            self.isolated_hosts.add(target)
            return ResponseAction(
                action_type=action_name,
                status="simulated_success",
                target=target,
                detection_id=detection.detection_id,
                details={**details, "message": f"Host {target} isolated"},
            )
        if action_name == "generate_alert":
            return ResponseAction(
                action_type=action_name,
                status="completed",
                target=target,
                detection_id=detection.detection_id,
                details={**details, "message": detection.description},
            )
        if action_name == "block_domain":
            domain = payload.get("domain") or payload.get("query") or payload.get("dns_activity") or "unknown"
            return ResponseAction(
                action_type=action_name,
                status="simulated_success",
                target=str(domain),
                detection_id=detection.detection_id,
                details={**details, "message": f"Domain {domain} blocked"},
            )
        if action_name == "delete_file":
            path = payload.get("path") or payload.get("filename") or "unknown"
            return ResponseAction(
                action_type=action_name,
                status="simulated_success",
                target=str(path),
                detection_id=detection.detection_id,
                details={**details, "message": f"File {path} deleted"},
            )
        if action_name in {"monitor", "investigate"}:
            return ResponseAction(
                action_type=action_name,
                status="queued",
                target=target,
                detection_id=detection.detection_id,
                details={**details, "message": f"{action_name.title()} workflow queued"},
            )
        return None
