"""
Project 4 — Security Policies.

Configurable security policies that define what agents are
and are not allowed to do.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field


@dataclass
class SecurityPolicy:
    """
    Security policy configuration.

    Defines the boundaries within which agents may operate.
    """

    # Allowed base directories for file operations
    allowed_directories: list[str] = field(default_factory=lambda: [
        os.getenv("PROJECT_DIR", "/home/shadman/Documents/Project 4"),
        "/tmp/project4",
    ])

    # Explicitly blocked paths (regex patterns)
    blocked_path_patterns: list[str] = field(default_factory=lambda: [
        r"/etc/passwd",
        r"/etc/shadow",
        r"/etc/hosts",
        r"\.ssh/",
        r"\.gnupg/",
        r"\.aws/",
        r"\.config/",
        r"\.env$",               # Block reading .env files (contains API keys)
        r"id_rsa",
        r"id_ed25519",
        r"authorized_keys",
        r"known_hosts",
        r"/proc/",
        r"/sys/",
        r"/dev/",
    ])

    # Blocked terminal commands (substrings)
    blocked_commands: list[str] = field(default_factory=lambda: [
        "rm -rf",
        "shutdown",
        "reboot",
        "mkfs",
        "dd if=",
        "curl",      # Prevent data exfiltration via HTTP
        "wget",
        "nc ",        # netcat
        "ncat",
        "socat",
        "env",        # Prevent env variable dumping
        "printenv",
        "export",
        "set |",
    ])

    # Blocked content patterns in agent outputs (data leak indicators)
    blocked_output_patterns: list[str] = field(default_factory=lambda: [
        r"AIza[A-Za-z0-9_-]{35}",       # Google API keys
        r"sk-[A-Za-z0-9]{48}",           # OpenAI keys
        r"-----BEGIN.*PRIVATE KEY-----",  # Private keys
        r"password\s*[:=]\s*\S+",         # Passwords
        r"secret\s*[:=]\s*\S+",           # Secrets
    ])

    def is_path_allowed(self, path: str) -> tuple[bool, str]:
        """Check if a file path is allowed by policy."""
        abs_path = os.path.abspath(os.path.expanduser(path))

        # Check blocked patterns first
        for pattern in self.blocked_path_patterns:
            if re.search(pattern, abs_path):
                return False, f"Path matches blocked pattern: {pattern}"

        # Check if within allowed directories
        for allowed_dir in self.allowed_directories:
            allowed_abs = os.path.abspath(allowed_dir)
            if abs_path.startswith(allowed_abs):
                return True, "Within allowed directory"

        return False, f"Path outside allowed directories: {self.allowed_directories}"

    def is_command_allowed(self, command: str) -> tuple[bool, str]:
        """Check if a terminal command is allowed by policy."""
        cmd_lower = command.lower().strip()
        for blocked in self.blocked_commands:
            if blocked.lower() in cmd_lower:
                return False, f"Command contains blocked substring: {blocked}"
        return True, "Command allowed"

    def check_output_for_leaks(self, output: str) -> tuple[bool, str]:
        """Check if agent output contains sensitive data."""
        for pattern in self.blocked_output_patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return True, f"Output contains sensitive data matching: {pattern}"
        return False, "No sensitive data detected"


# Default policy instance
DEFAULT_POLICY = SecurityPolicy()
