"""
Project 4 — Security Interceptor.

Inspects every tool call / file operation before execution.
Assigns a risk level (LOW/MEDIUM/HIGH/CRITICAL) and blocks HIGH/CRITICAL
operations unless approved by the user via the Chainlit HITL gate.

Each interception is tagged with:
  - MITRE ATLAS technique (https://atlas.mitre.org)
  - STRIDE category
for direct use in the security analysis report.
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from src.security.policies import SecurityPolicy, DEFAULT_POLICY

logger = logging.getLogger(__name__)

# MITRE ATLAS + STRIDE lookup per operation type
_THREAT_MAP: dict[str, dict] = {
    "env_read": {
        "atlas": "AML.T0048 — Exfiltration via ML Inference API",
        "stride": "Information Disclosure, Tampering",
    },
    "file_read": {
        "atlas": "AML.T0051 — LLM Prompt Injection / AML.T0048 — Exfiltration",
        "stride": "Information Disclosure, Elevation of Privilege",
    },
    "file_write": {
        "atlas": "AML.T0051 — LLM Prompt Injection",
        "stride": "Tampering",
    },
    "terminal": {
        "atlas": "AML.T0051 — LLM Prompt Injection / AML.T0040 — ML Inference API Access",
        "stride": "Elevation of Privilege, Tampering",
    },
    "output_scan": {
        "atlas": "AML.T0048 — Exfiltration via ML Inference API",
        "stride": "Information Disclosure",
    },
}


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class InterceptionResult:
    """Result of a security interception check."""
    allowed: bool
    risk_level: RiskLevel
    reason: str
    operation: str
    target: str  # File path or command
    atlas_technique: str = ""
    stride_category: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class SecurityInterceptor:
    """
    Inspects agent operations before execution.

    For LOW/MEDIUM: logs and allows.
    For HIGH/CRITICAL: blocks and requests HITL approval.
    """

    def __init__(self, policy: SecurityPolicy | None = None):
        self.policy = policy or DEFAULT_POLICY
        self.interception_log: list[InterceptionResult] = []
        self.enabled = True

    def _enrich(self, result: InterceptionResult) -> InterceptionResult:
        """Attach MITRE ATLAS and STRIDE labels to a result."""
        mapping = _THREAT_MAP.get(result.operation, {})
        result.atlas_technique = mapping.get("atlas", "")
        result.stride_category = mapping.get("stride", "")
        return result

    def check_file_read(self, path: str) -> InterceptionResult:
        """Check if a file read operation should be allowed."""
        if not self.enabled:
            return InterceptionResult(True, RiskLevel.LOW, "Interceptor disabled", "read", path)

        allowed, reason = self.policy.is_path_allowed(path)

        if not allowed:
            # Determine severity
            critical_patterns = [r"\.ssh", r"id_rsa", r"/etc/shadow", r"\.env"]
            high_patterns = [r"/etc/passwd", r"\.config", r"\.aws", r"\.gnupg"]

            risk = RiskLevel.HIGH
            for pattern in critical_patterns:
                if re.search(pattern, path):
                    risk = RiskLevel.CRITICAL
                    break
            for pattern in high_patterns:
                if re.search(pattern, path):
                    risk = RiskLevel.HIGH
                    break

            result = InterceptionResult(False, risk, reason, "file_read", path)
        else:
            result = InterceptionResult(True, RiskLevel.LOW, reason, "file_read", path)

        self._enrich(result)
        self.interception_log.append(result)
        logger.info(
            "🛡️ Interceptor [%s] %s: %s — %s | ATLAS: %s | STRIDE: %s",
            result.risk_level.value,
            "ALLOWED" if result.allowed else "BLOCKED",
            result.operation,
            result.target,
            result.atlas_technique,
            result.stride_category,
        )
        return result

    def check_file_write(self, path: str) -> InterceptionResult:
        """Check if a file write operation should be allowed."""
        if not self.enabled:
            return InterceptionResult(True, RiskLevel.LOW, "Interceptor disabled", "write", path)

        allowed, reason = self.policy.is_path_allowed(path)
        risk = RiskLevel.MEDIUM if allowed else RiskLevel.HIGH

        result = InterceptionResult(allowed, risk, reason, "file_write", path)
        self.interception_log.append(result)
        return result

    def check_command(self, command: str) -> InterceptionResult:
        """Check if a terminal command should be allowed."""
        if not self.enabled:
            return InterceptionResult(True, RiskLevel.LOW, "Interceptor disabled", "command", command)

        allowed, reason = self.policy.is_command_allowed(command)
        risk = RiskLevel.LOW if allowed else RiskLevel.CRITICAL

        result = InterceptionResult(allowed, risk, reason, "terminal", command)
        self.interception_log.append(result)
        return result

    def check_env_access(self) -> InterceptionResult:
        """Check if environment variable access should be allowed."""
        result = InterceptionResult(
            False,
            RiskLevel.CRITICAL,
            "Environment variable access is blocked by security policy",
            "env_read",
            "system environment",
        )
        self.interception_log.append(result)
        return result

    def check_output(self, output: str) -> InterceptionResult:
        """Check if agent output contains leaked sensitive data."""
        has_leak, reason = self.policy.check_output_for_leaks(output)
        if has_leak:
            result = InterceptionResult(
                False, RiskLevel.CRITICAL,
                f"Output leak detected: {reason}",
                "output_scan", "agent_output",
            )
        else:
            result = InterceptionResult(True, RiskLevel.LOW, "Clean", "output_scan", "agent_output")

        self.interception_log.append(result)
        return result

    def get_blocked_count(self) -> int:
        """Count how many operations were blocked."""
        return sum(1 for r in self.interception_log if not r.allowed)

    def get_log_summary(self) -> dict:
        """Get a summary of all interceptions for the report."""
        return {
            "total_checks": len(self.interception_log),
            "blocked": self.get_blocked_count(),
            "allowed": len(self.interception_log) - self.get_blocked_count(),
            "by_risk": {
                level.value: sum(1 for r in self.interception_log if r.risk_level == level)
                for level in RiskLevel
            },
            "blocked_operations": [
                {
                    "operation": r.operation,
                    "target": r.target,
                    "risk": r.risk_level.value,
                    "reason": r.reason,
                    "atlas_technique": r.atlas_technique,
                    "stride_category": r.stride_category,
                    "timestamp": r.timestamp,
                }
                for r in self.interception_log if not r.allowed
            ],
        }

    def export_log_json(self, path: str = "security_audit_log.json") -> str:
        """Export the full interception log as JSON for report evidence."""
        log_data = {
            "session_summary": self.get_log_summary(),
            "full_log": [
                {
                    "timestamp": r.timestamp,
                    "operation": r.operation,
                    "target": r.target,
                    "allowed": r.allowed,
                    "risk_level": r.risk_level.value,
                    "reason": r.reason,
                    "atlas_technique": r.atlas_technique,
                    "stride_category": r.stride_category,
                }
                for r in self.interception_log
            ],
        }
        with open(path, "w") as f:
            json.dump(log_data, f, indent=2)
        logger.info("🛡️ Security audit log exported to %s", path)
        return path
