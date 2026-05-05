"""
Project 4 — Security Policies.

Configurable security policies that define what agents are
and are not allowed to do.
"""

from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


_HIGH_ENTROPY_MIN_LEN = 20    # ignore tokens shorter than this
_HIGH_ENTROPY_THRESHOLD = 4.5 # bits/char — above this is likely an encoded secret

def _shannon_entropy(s: str) -> float:
    """Calculate Shannon entropy in bits per character."""
    if not s:
        return 0.0
    freq: dict[str, int] = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    length = len(s)
    return -sum((n / length) * math.log2(n / length) for n in freq.values())


@dataclass
class SecurityPolicy:
    """
    Security policy configuration.

    Defines the boundaries within which agents may operate.
    """

    # Allowed base directories for file operations
    allowed_directories: list[str] = field(default_factory=lambda: [
        os.getenv("PROJECT_DIR", str(Path.home() / "Documents" / "Project 4")),
        str(Path(os.getenv("TEMP", "/tmp")) / "project4"),
    ])

    # Explicitly blocked paths (regex patterns — cross-platform, separator-agnostic)
    blocked_path_patterns: list[str] = field(default_factory=lambda: [
        # System credential and password files (Unix + Windows equivalents)
        r"etc[\\/]passwd",
        r"etc[\\/]shadow",
        r"etc[\\/]hosts",
        # SSH / GPG / cloud credential directories (forward or back slash)
        r"\.ssh[\\/]",
        r"\.gnupg[\\/]",
        r"\.aws[\\/]",
        r"\.config[\\/]",
        # Windows credential paths
        r"AppData[\\/]Roaming[\\/]",
        r"AppData[\\/]Local[\\/]Microsoft[\\/]",
        # Key files and secrets (filename-only — already cross-platform)
        r"\.env$",
        r"id_rsa",
        r"id_ed25519",
        r"authorized_keys",
        r"known_hosts",
        # Unix virtual filesystems (harmless to keep, never match on Windows)
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
        abs_path = Path(os.path.expanduser(path)).resolve()

        # Check blocked patterns first (case-insensitive for Windows compatibility)
        for pattern in self.blocked_path_patterns:
            if re.search(pattern, str(abs_path), re.IGNORECASE):
                return False, f"Path matches blocked pattern: {pattern}"

        # Check if within allowed directories using pathlib (avoids startswith false-positives)
        for allowed_dir in self.allowed_directories:
            try:
                abs_path.relative_to(Path(allowed_dir).resolve())
                return True, "Within allowed directory"
            except ValueError:
                continue

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

        # Entropy scan: catch encoded/obfuscated secrets that evade regex patterns
        for token in re.findall(r"[A-Za-z0-9+/=_\-]{20,}", output):
            entropy = _shannon_entropy(token)
            if entropy >= _HIGH_ENTROPY_THRESHOLD:
                return True, (
                    f"High-entropy token detected (entropy={entropy:.2f} bits/char, "
                    f"len={len(token)}) — possible encoded or obfuscated secret"
                )

        return False, "No sensitive data detected"


# Default policy instance
DEFAULT_POLICY = SecurityPolicy()
