from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ToolResult:
    ok: bool
    output: str
    exit_code: int = 0


class ShellTool:
    """Execute shell commands with a timeout."""

    def __init__(self, timeout_seconds: int = 30) -> None:
        self.timeout_seconds = timeout_seconds

    def run(self, command: str, cwd: Optional[str] = None) -> ToolResult:
        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            return ToolResult(ok=completed.returncode == 0, output=output, exit_code=completed.returncode)
        except subprocess.TimeoutExpired as ex:
            return ToolResult(ok=False, output=f"Timeout after {self.timeout_seconds}s: {ex}", exit_code=124)


__all__ = ["ShellTool", "ToolResult"]
