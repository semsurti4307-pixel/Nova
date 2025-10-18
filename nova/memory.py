from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_DIR = Path(".nova")
DEFAULT_FILE = DEFAULT_DIR / "session.jsonl"


def ensure_dirs() -> None:
    DEFAULT_DIR.mkdir(parents=True, exist_ok=True)


def append_turn(turn: Dict[str, Any]) -> None:
    ensure_dirs()
    with DEFAULT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(turn, ensure_ascii=False) + "\n")
