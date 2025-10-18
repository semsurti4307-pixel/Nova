from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .llm.base import LanguageModel, Plan
from .tools.registry import ToolRegistry
from .utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class Agent:
    model: LanguageModel
    tools: ToolRegistry
    memory: List[Dict[str, str]] = field(default_factory=list)

    def respond(self, user_input: str) -> str:
        self.memory.append({"role": "user", "content": user_input})

        plan: Plan = self.model.decide(user_input=user_input, context=self.memory)
        if plan.action == "respond":
            reply = self.model.generate_reply(
                user_input=user_input, context=self.memory, tool_output=None
            )
            self.memory.append({"role": "assistant", "content": reply})
            return reply

        if plan.action == "tool":
            tool_name = plan.tool_name
            if not tool_name:
                reply = "I planned to use a tool but did not specify which."
                self.memory.append({"role": "assistant", "content": reply})
                return reply

            tool = self.tools.get(tool_name)
            if not tool:
                reply = f"Requested tool '{tool_name}' is not available."
                self.memory.append({"role": "assistant", "content": reply})
                return reply

            try:
                output = tool.run(plan.tool_input or {})
            except Exception as exc:
                logger.exception("Tool '%s' execution failed", tool_name)
                output = f"Error while running tool '{tool_name}': {exc}"

            reply = self.model.generate_reply(
                user_input=user_input, context=self.memory, tool_output=output
            )
            self.memory.append({"role": "assistant", "content": reply})
            return reply

        reply = "I could not create a plan for this request."
        self.memory.append({"role": "assistant", "content": reply})
        return reply
