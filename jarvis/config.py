from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

import yaml


_DEFAULT_CONFIG = {
    "jarvis": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "system_prompt": (
            "You are J.A.R.V.I.S., a precise, helpful assistant. Be concise. "
            "Use tools when helpful. Confirm dangerous actions."
        ),
    },
    "paths": {"base_dir": "."},
    "tools": {"allowed_commands": ["ls", "pwd", "echo"]},
}


@dataclass
class JarvisConfig:
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    system_prompt: str = _DEFAULT_CONFIG["jarvis"]["system_prompt"]
    base_dir: Path = Path(".")
    allowed_commands: List[str] = field(default_factory=lambda: ["ls", "pwd", "echo"])

    @staticmethod
    def load(config_path: Optional[Path] = None) -> "JarvisConfig":
        path = (
            Path(os.environ.get("JARVIS_CONFIG")).expanduser()
            if os.environ.get("JARVIS_CONFIG")
            else (config_path or Path.cwd() / "config.yaml")
        )
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data: Dict[str, Any] = yaml.safe_load(f) or {}
        else:
            data = _DEFAULT_CONFIG

        jarvis = data.get("jarvis", {})
        paths = data.get("paths", {})
        tools = data.get("tools", {})

        base_dir = Path(paths.get("base_dir", ".")).expanduser().resolve()

        return JarvisConfig(
            provider=jarvis.get("provider", _DEFAULT_CONFIG["jarvis"]["provider"]),
            model=jarvis.get("model", _DEFAULT_CONFIG["jarvis"]["model"]),
            system_prompt=jarvis.get(
                "system_prompt", _DEFAULT_CONFIG["jarvis"]["system_prompt"]
            ),
            base_dir=base_dir,
            allowed_commands=tools.get(
                "allowed_commands", _DEFAULT_CONFIG["tools"]["allowed_commands"]
            ),
        )
