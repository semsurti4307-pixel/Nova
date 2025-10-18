from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str


class LLMProvider:
    def complete(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        raise NotImplementedError


class EchoProvider(LLMProvider):
    def complete(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        last = messages[-1]["content"] if messages else ""
        return {
            "content": f"[OFFLINE MODE] You said: {last}",
            "tool_calls": [],
        }


class OpenAILLMProvider(LLMProvider):
    def __init__(self) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package not available")
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI()

    def complete(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        resp = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools or None,
            tool_choice="auto" if tools else None,
        )
        msg = resp.choices[0].message
        content = msg.content or ""
        tool_calls: List[ToolCall] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=tc.function.arguments,
                    )
                )
        return {
            "content": content,
            "tool_calls": tool_calls,
            "raw_assistant_message": msg,  # so caller can echo tool_calls back
        }


def get_llm_provider() -> LLMProvider:
    try:
        return OpenAILLMProvider()
    except Exception:
        return EchoProvider()
