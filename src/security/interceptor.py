"""
Project 4 — Security Interceptor.

Inspects every tool call / file operation before execution.
Assigns a risk level and blocks HIGH/CRITICAL operations unless
approved by the user via the Chainlit HITL gate.
"""

from __future__ import annotations

import logging
import re
from enum import Enum
from dataclasses import dataclass

from src.security.policies import SecurityPolicy, DEFAULT_POLICY

logger = logging.getLogger(__name__)


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

        self.interception_log.append(result)
        logger.info(
            "🛡️ Interceptor [%s] %s: %s — %s",
            result.risk_level.value,
            "ALLOWED" if result.allowed else "BLOCKED",
            result.operation,
            result.target,
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
                {"operation": r.operation, "target": r.target, "risk": r.risk_level.value, "reason": r.reason}
                for r in self.interception_log if not r.allowed
            ],
        }
