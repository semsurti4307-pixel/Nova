from __future__ import annotations

import re
from typing import Dict, List, Optional

from .base import LanguageModel, Plan


TOOL_ALIASES = {
    # files
    "read": "files.read",
    "read file": "files.read",
    "open": "files.read",
    "write": "files.write",
    "save": "files.write",
    "ls": "files.list",
    "list": "files.list",
    "dir": "files.list",
    # web
    "http": "web.http_get",
    "get": "web.http_get",
    "fetch": "web.http_get",
    # system
    "shell": "system.shell",
    "bash": "system.shell",
    "run": "system.shell",
}


class SimpleRuleBasedModel(LanguageModel):
    def _infer_tool(self, user_input: str) -> Optional[str]:
        text = user_input.lower().strip()

        for alias, tool in TOOL_ALIASES.items():
            if alias in text:
                return tool

        # simple heuristics
        if re.search(r"\b(list|show) (files|directory|dir)\b", text):
            return "files.list"
        if re.search(r"\b(read|open)\b", text) and "." in text:
            return "files.read"
        if text.startswith("http://") or text.startswith("https://"):
            return "web.http_get"
        if re.search(r"\b(run|exec|shell|bash|sh)\b", text):
            return "system.shell"
        return None

    def decide(self, user_input: str, context: List[Dict[str, str]]) -> Plan:
        tool = self._infer_tool(user_input)
        if tool is None:
            return Plan(action="respond")

        tool_input: Dict = {}
        if tool == "files.read":
            # crude filename extraction
            m = re.search(r"(?:read|open)\s+([\w_/.-]+)", user_input, flags=re.I)
            if m:
                tool_input = {"path": m.group(1)}
        elif tool == "files.write":
            m = re.search(r"(?:write|save)\s+([\w_/.-]+)\s+(.+)$", user_input, flags=re.I)
            if m:
                tool_input = {"path": m.group(1), "content": m.group(2)}
        elif tool == "files.list":
            m = re.search(r"(?:ls|list|dir)\s+([\w_/.-]+)", user_input, flags=re.I)
            if m:
                tool_input = {"path": m.group(1)}
        elif tool == "web.http_get":
            m = re.search(r"(https?://\S+)", user_input, flags=re.I)
            if m:
                tool_input = {"url": m.group(1)}
        elif tool == "system.shell":
            m = re.search(r"(?:run|shell|bash)\s+(.+)$", user_input, flags=re.I)
            if m:
                tool_input = {"command": m.group(1)}
        return Plan(action="tool", tool_name=tool, tool_input=tool_input)

    def generate_reply(
        self,
        user_input: str,
        context: List[Dict[str, str]],
        tool_output: Optional[str] = None,
    ) -> str:
        if tool_output is not None:
            return str(tool_output).strip()
        # default: echo a helpful response
        return (
            "I can help with files (read/write/ls), web (http get), or system shell. "
            "Try: 'ls .', 'read README.md', 'https://example.com', or 'run echo hello'."
        )
