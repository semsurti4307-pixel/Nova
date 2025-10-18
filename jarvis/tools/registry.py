from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol


class Tool(Protocol):
    name: str
    description: str

    def run(self, params: Dict) -> str: ...


@dataclass
class ToolRegistry:
    tools: Dict[str, Tool] = None

    def __post_init__(self) -> None:
        if self.tools is None:
            self.tools = {}

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list(self) -> Dict[str, Tool]:
        return dict(self.tools)
