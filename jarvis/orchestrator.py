from __future__ import annotations

import json
from typing import Any, Dict, List

from .config import JarvisConfig
from .llm import get_llm_provider, ToolCall
from .tools import ToolsRegistry


class Orchestrator:
    def __init__(self, config: JarvisConfig) -> None:
        self.config = config
        self.llm = get_llm_provider()
        self.tools = ToolsRegistry(
            base_dir=config.base_dir,
            allowed_commands=config.allowed_commands,
        )

    def build_system_message(self) -> Dict[str, str]:
        return {"role": "system", "content": self.config.system_prompt}

    def tool_specs(self) -> List[Dict[str, Any]]:
        return self.tools.get_tool_specs()

    def step(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run one LLM step; execute tools if requested until final assistant text."""
        tools = self.tool_specs()
        # First completion
        result = self.llm.complete(self.config.model, messages, tools)
        assistant_content = result.get("content", "")
        tool_calls: List[ToolCall] = result.get("tool_calls", [])

        if not tool_calls:
            return {"content": assistant_content, "messages": messages + [{"role": "assistant", "content": assistant_content}]}

        # Add assistant message with tool_calls for traceability
        assistant_msg: Dict[str, Any] = {
            "role": "assistant",
            "content": assistant_content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in tool_calls
            ],
        }
        messages.append(assistant_msg)

        # Execute each tool and append its result
        for tc in tool_calls:
            status, content = self.tools.execute(tc.name, tc.arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tc.name,
                    "content": content,
                }
            )

        # Ask the model again with new tool results
        result2 = self.llm.complete(self.config.model, messages, tools)
        assistant_content2 = result2.get("content", "")
        messages.append({"role": "assistant", "content": assistant_content2})
        return {"content": assistant_content2, "messages": messages}
