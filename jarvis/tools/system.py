from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Dict


@dataclass
class SystemShellTool:
    allow_system: bool = False
    name: str = "system.shell"
    description: str = (
        "Run a shell command on the host. Disabled by default for safety. params: {command}"
    )

    def run(self, params: Dict) -> str:
        if not self.allow_system:
            return "system.shell is disabled. Re-run with --allow-system to enable."
        command = params.get("command")
        if not command:
            return "Missing 'command' parameter."
        try:
            completed = subprocess.run(
                command,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
            )
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            if completed.returncode != 0:
                return f"Exit {completed.returncode}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
            return stdout or "(no output)"
        except Exception as exc:
            return f"Error running command: {exc}"
