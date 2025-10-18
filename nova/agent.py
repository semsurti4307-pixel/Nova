from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .llm import DEFAULT_MODEL, get_llm_client, simple_complete
from .tools import ShellTool
from .tools_fs import read_file, write_file
from .tools_web import http_get


@dataclass
class Thought:
    text: str


@dataclass
class Action:
    name: str
    input: str


@dataclass
class Observation:
    text: str


class NovaAgent:
    def __init__(self) -> None:
        self._client = None  # lazy LLM init
        self.model = DEFAULT_MODEL
        self.shell = ShellTool()

    def _ensure_client(self):
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    def plan(self, goal: str, history: Optional[List[str]] = None) -> Action:
        # A simple heuristic planner: map commands by prefix
        goal_l = goal.strip().lower()
        if goal_l.startswith("run:"):
            return Action("shell", goal.split(":", 1)[1].strip())
        if goal_l.startswith("read:"):
            return Action("read_file", goal.split(":", 1)[1].strip())
        if goal_l.startswith("write:"):
            return Action("write_file", goal.split(":", 1)[1].strip())
        if goal_l.startswith("get:") or goal_l.startswith("web:"):
            url = goal.split(":", 1)[1].strip()
            return Action("http_get", url)
        # Fallback: just ask the LLM to answer
        return Action("answer", goal)

    def act(self, action: Action) -> Observation:
        if action.name == "shell":
            res = self.shell.run(action.input)
            return Observation(res.output)
        if action.name == "read_file":
            res = read_file(action.input)
            return Observation(res.message)
        if action.name == "write_file":
            try:
                path, content = action.input.split("::", 1)
            except ValueError:
                return Observation("Invalid write format. Use path::content")
            res = write_file(path.strip(), content)
            return Observation(res.message)
        if action.name == "http_get":
            res = http_get(action.input)
            return Observation(res)

        # default LLM answer
        try:
            client = self._ensure_client()
        except Exception as ex:  # noqa: BLE001
            return Observation(
                "LLM is not configured (missing OPENAI_API_KEY). "
                "Set it in .env to enable chat answers."
            )
        return Observation(simple_complete(client, action.input))
