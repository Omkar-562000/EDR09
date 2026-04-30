from __future__ import annotations

import ipaddress
import platform
import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class FirewallResult:
    status: str
    ip_address: str
    direction: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "status": self.status,
            "ip_address": self.ip_address,
            "direction": self.direction,
            "message": self.message,
        }


class WindowsFirewallController:
    """Manage explicit EDR firewall rules for a single Windows endpoint."""

    rule_prefix = "EDR Block"
    allowed_directions = {"inbound", "outbound", "both"}

    def block_ip(self, ip_address: str, direction: str = "both") -> FirewallResult:
        ip_address = self._validate_ip(ip_address)
        direction = self._validate_direction(direction)
        self._require_windows()

        for firewall_direction in self._directions(direction):
            rule_name = self._rule_name(ip_address, firewall_direction)
            self._run_powershell(
                (
                    "& { param($RuleName, $Direction, $RemoteAddress) "
                    "if (-not (Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue)) { "
                    "New-NetFirewallRule -DisplayName $RuleName -Direction $Direction -RemoteAddress $RemoteAddress "
                    "-Action Block | Out-Null "
                    "} }"
                ),
                [rule_name, firewall_direction, ip_address],
            )

        return FirewallResult(
            status="blocked",
            ip_address=ip_address,
            direction=direction,
            message=f"Windows Firewall rule created for {ip_address}",
        )

    def unblock_ip(self, ip_address: str, direction: str = "both") -> FirewallResult:
        ip_address = self._validate_ip(ip_address)
        direction = self._validate_direction(direction)
        self._require_windows()

        for firewall_direction in self._directions(direction):
            rule_name = self._rule_name(ip_address, firewall_direction)
            self._run_powershell(
                (
                    "& { param($RuleName) "
                    "Remove-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue "
                    "}"
                ),
                [rule_name],
            )

        return FirewallResult(
            status="unblocked",
            ip_address=ip_address,
            direction=direction,
            message=f"Windows Firewall rule removed for {ip_address}",
        )

    def check_ip(self, ip_address: str, direction: str = "both") -> dict[str, object]:
        ip_address = self._validate_ip(ip_address)
        direction = self._validate_direction(direction)
        self._require_windows()

        rules: list[dict[str, object]] = []
        for firewall_direction in self._directions(direction):
            rule_name = self._rule_name(ip_address, firewall_direction)
            exists = self._rule_exists(rule_name)
            rules.append({"name": rule_name, "direction": firewall_direction, "exists": exists})

        return {
            "ip_address": ip_address,
            "direction": direction,
            "blocked": any(rule["exists"] for rule in rules),
            "rules": rules,
        }

    def _validate_ip(self, ip_address: str) -> str:
        try:
            return str(ipaddress.ip_address(ip_address.strip()))
        except ValueError as exc:
            raise ValueError("Enter a valid IPv4 or IPv6 address") from exc

    def _validate_direction(self, direction: str) -> str:
        normalized = direction.strip().lower()
        if normalized not in self.allowed_directions:
            raise ValueError("Direction must be inbound, outbound, or both")
        return normalized

    def _require_windows(self) -> None:
        if platform.system().lower() != "windows":
            raise RuntimeError("Real firewall blocking is only supported on Windows")

    def _directions(self, direction: str) -> list[str]:
        if direction == "both":
            return ["Inbound", "Outbound"]
        return [direction.title()]

    def _rule_name(self, ip_address: str, direction: str) -> str:
        return f"{self.rule_prefix} {ip_address} {direction}"

    def _rule_exists(self, rule_name: str) -> bool:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    "& { param($RuleName) "
                    "if (Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue) { 'true' } "
                    "else { 'false' } "
                    "}"
                ),
                rule_name,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if completed.returncode != 0:
            error = completed.stderr.strip() or completed.stdout.strip() or "Firewall check failed"
            raise RuntimeError(error)
        return completed.stdout.strip().lower() == "true"

    def _run_powershell(self, script: str, args: list[str]) -> None:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
                *args,
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if completed.returncode != 0:
            error = completed.stderr.strip() or completed.stdout.strip() or "Firewall command failed"
            raise RuntimeError(error)
