from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol


@dataclass
class Plan:
    action: str  # "respond" | "tool"
    tool_name: Optional[str] = None
    tool_input: Optional[Dict] = None


class LanguageModel(Protocol):
    def decide(self, user_input: str, context: List[Dict[str, str]]) -> Plan: ...

    def generate_reply(
        self,
        user_input: str,
        context: List[Dict[str, str]],
        tool_output: Optional[str] = None,
    ) -> str: ...
