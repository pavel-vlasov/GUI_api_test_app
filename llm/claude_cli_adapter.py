"""Claude Code CLI adapter using pexpect/wexpect."""
from __future__ import annotations

import json
import logging
import platform
from typing import Callable, List

logger = logging.getLogger(__name__)


class ClaudeCliAdapter:
    """Adapter for Claude Code CLI command emission workflow."""

    def __init__(self, cli_command: str = "claude") -> None:
        """Initialize CLI adapter with binary name."""

        self.cli_command = cli_command

    def generate_commands(self, prompt: str, on_stream: Callable[[str], None] | None = None) -> List[str]:
        """Send prompt to Claude CLI and parse JSON array output."""

        child = self._spawn_process()
        child.sendline(prompt)
        child.expect("\n", timeout=120)
        output = child.before.decode() if isinstance(child.before, bytes) else str(child.before)
        if on_stream:
            on_stream(output)
        parsed = json.loads(output.strip() or "[]")
        return [item["command"] if isinstance(item, dict) else item for item in parsed]

    def _spawn_process(self):
        """Create pexpect or wexpect process based on OS."""

        if platform.system().lower().startswith("win"):
            import wexpect  # type: ignore

            return wexpect.spawn(self.cli_command)
        import pexpect  # type: ignore

        return pexpect.spawn(self.cli_command, encoding="utf-8")
