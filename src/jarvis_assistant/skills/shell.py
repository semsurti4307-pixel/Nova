from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Sequence


@dataclass
class CommandResult:
    exit_code: int
    stdout: str
    stderr: str


def run_command(command: Sequence[str] | str, timeout: Optional[int] = 60) -> CommandResult:
    if isinstance(command, str):
        command_list: List[str] = shlex.split(command)
    else:
        command_list = list(command)

    try:
        completed = subprocess.run(
            command_list,
            capture_output=True,
            timeout=timeout,
            text=True,
        )
        return CommandResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    except subprocess.TimeoutExpired as e:
        return CommandResult(exit_code=124, stdout=e.stdout or "", stderr=e.stderr or "timeout")
    except FileNotFoundError as e:
        return CommandResult(exit_code=127, stdout="", stderr=str(e))
