from __future__ import annotations

import os
from typing import Any

from openai import OpenAI


DEFAULT_MODEL = os.getenv("NOVA_MODEL", "gpt-4o-mini")


def get_llm_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Put it in your .env")
    return OpenAI(api_key=api_key)


def simple_complete(client: OpenAI, prompt: str) -> str:
    # Minimal completion using Chat Completions API
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are Nova, a helpful, concise assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""
