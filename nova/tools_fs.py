from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FSResult:
    ok: bool
    message: str


def read_file(path: str) -> FSResult:
    file_path = Path(path)
    if not file_path.exists() or not file_path.is_file():
        return FSResult(False, f"File not found: {path}")
    try:
        content = file_path.read_text(encoding="utf-8")
        return FSResult(True, content)
    except Exception as ex:  # noqa: BLE001
        return FSResult(False, f"Read error: {ex}")


def write_file(path: str, content: str, create_dirs: bool = True) -> FSResult:
    file_path = Path(path)
    try:
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return FSResult(True, str(file_path))
    except Exception as ex:  # noqa: BLE001
        return FSResult(False, f"Write error: {ex}")
