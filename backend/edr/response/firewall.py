from __future__ import annotations

import ipaddress
import json
import platform
import subprocess
from dataclasses import dataclass

from backend.edr.config.settings import FIREWALL_LOCAL_PORTS


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
            self._remove_netsh_rule(rule_name)
            self._add_netsh_rule(rule_name, ip_address, firewall_direction)
        if direction in {"inbound", "both"} and FIREWALL_LOCAL_PORTS:
            rule_name = self._web_rule_name(ip_address)
            self._remove_netsh_rule(rule_name)
            self._add_netsh_web_rule(rule_name, ip_address)
        verification = self.check_ip(ip_address, direction)
        if not verification["blocked"]:
            raise RuntimeError(
                f"Windows Firewall did not create an active block rule for {ip_address}: {verification['rules']}"
            )

        return FirewallResult(
            status="blocked",
            ip_address=ip_address,
            direction=direction,
            message=self._block_message(ip_address, direction),
        )

    def unblock_ip(self, ip_address: str, direction: str = "both") -> FirewallResult:
        ip_address = self._validate_ip(ip_address)
        direction = self._validate_direction(direction)
        self._require_windows()

        for firewall_direction in self._directions(direction):
            rule_name = self._rule_name(ip_address, firewall_direction)
            self._remove_netsh_rule(rule_name)
        if direction in {"inbound", "both"}:
            web_rule_name = self._web_rule_name(ip_address)
            self._remove_netsh_rule(web_rule_name)

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
            rules.append(self._rule_details(rule_name, firewall_direction))
        if direction in {"inbound", "both"} and FIREWALL_LOCAL_PORTS:
            rules.append(self._rule_details(self._web_rule_name(ip_address), "Inbound web ports"))

        return {
            "ip_address": ip_address,
            "direction": direction,
            "blocked": any(rule["exists"] and rule["enabled"] and rule["action"] == "Block" for rule in rules),
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

    def _web_rule_name(self, ip_address: str) -> str:
        return f"{self.rule_prefix} {ip_address} Web Ports"

    def _block_message(self, ip_address: str, direction: str) -> str:
        if direction in {"inbound", "both"} and FIREWALL_LOCAL_PORTS:
            ports = ", ".join(FIREWALL_LOCAL_PORTS)
            return f"Windows Firewall rules created for {ip_address}, including inbound web ports {ports}"
        return f"Windows Firewall rule created for {ip_address}"

    def _rule_details(self, rule_name: str, direction: str) -> dict[str, object]:
        netsh_details = self._netsh_rule_details(rule_name, direction)
        if netsh_details["exists"]:
            return netsh_details

        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                (
                    "& { param($RuleName) "
                    "$rule = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue; "
                    "$result = if (-not $rule) { "
                    "  [pscustomobject]@{ Exists = $false; Enabled = $false; Action = ''; Profile = ''; RemoteAddress = '' } "
                    "} else { "
                    "  $address = $rule | Get-NetFirewallAddressFilter; "
                    "  $port = $rule | Get-NetFirewallPortFilter; "
                    "  [pscustomobject]@{ "
                    "    Exists = $true; "
                    "    Enabled = ($rule.Enabled -eq 'True'); "
                    "    Action = [string]$rule.Action; "
                    "    Profile = [string]$rule.Profile; "
                    "    RemoteAddress = [string]$address.RemoteAddress; "
                    "    Protocol = [string]$port.Protocol; "
                    "    LocalPort = [string]$port.LocalPort "
                    "  } "
                    "}; "
                    "$result | ConvertTo-Json -Compress "
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
        output = completed.stdout.strip()
        if not output:
            return {
                "name": rule_name,
                "direction": direction,
                "exists": False,
                "enabled": False,
                "action": "",
                "profile": "",
                "remote_address": "",
                "protocol": "",
                "local_port": "",
            }
        details = json.loads(output)
        return {
            "name": rule_name,
            "direction": direction,
            "exists": bool(details.get("Exists")),
            "enabled": bool(details.get("Enabled")),
            "action": details.get("Action", ""),
            "profile": details.get("Profile", ""),
            "remote_address": details.get("RemoteAddress", ""),
            "protocol": details.get("Protocol", ""),
            "local_port": details.get("LocalPort", ""),
        }

    def _add_netsh_rule(self, rule_name: str, ip_address: str, direction: str) -> None:
        self._run_command(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                f"name={rule_name}",
                f"dir={self._netsh_direction(direction)}",
                "action=block",
                f"remoteip={ip_address}",
                "profile=any",
                "enable=yes",
            ],
            "Firewall rule creation failed",
        )

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

    def _add_netsh_web_rule(self, rule_name: str, ip_address: str) -> None:
        self._run_command(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                f"name={rule_name}",
                "dir=in",
                "action=block",
                "protocol=TCP",
                f"localport={','.join(FIREWALL_LOCAL_PORTS)}",
                f"remoteip={ip_address}",
                "profile=any",
                "enable=yes",
            ],
            "Firewall web-port rule creation failed",
        )

    def _remove_netsh_rule(self, rule_name: str) -> None:
        self._run_command(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "delete",
                "rule",
                f"name={rule_name}",
            ],
            "Firewall web-port rule removal failed",
            allow_no_match=True,
        )

    def _netsh_rule_details(self, rule_name: str, direction: str) -> dict[str, object]:
        completed = subprocess.run(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "show",
                "rule",
                f"name={rule_name}",
                "verbose",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = f"{completed.stdout}\n{completed.stderr}".strip()
        if completed.returncode != 0 or "No rules match" in output:
            return {
                "name": rule_name,
                "direction": direction,
                "exists": False,
                "enabled": False,
                "action": "",
                "profile": "",
                "remote_address": "",
                "protocol": "",
                "local_port": "",
            }

        return {
            "name": rule_name,
            "direction": direction,
            "exists": True,
            "enabled": "Enabled:                              Yes" in output,
            "action": "Block" if "Action:                               Block" in output else "",
            "profile": self._extract_netsh_value(output, "Profiles"),
            "remote_address": self._extract_netsh_value(output, "RemoteIP"),
            "protocol": self._extract_netsh_value(output, "Protocol"),
            "local_port": self._extract_netsh_value(output, "LocalPort"),
        }

    def _extract_netsh_value(self, output: str, label: str) -> str:
        prefix = f"{label}:"
        for line in output.splitlines():
            if line.strip().startswith(prefix):
                return line.split(":", 1)[1].strip()
        return ""

    def _netsh_direction(self, direction: str) -> str:
        return "in" if direction.lower() == "inbound" else "out"

    def _run_command(self, command: list[str], default_error: str, allow_no_match: bool = False) -> None:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = f"{completed.stdout}\n{completed.stderr}".strip()
        if allow_no_match and completed.returncode != 0 and "No rules match" in output:
            return
        if completed.returncode != 0:
            raise RuntimeError(output or default_error)
