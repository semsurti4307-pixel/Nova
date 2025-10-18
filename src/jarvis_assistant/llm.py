from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

# Defer HTTP client import to call sites to keep optional dependency truly optional


@dataclass
class LLMResponse:
    text: str


class LLMClient:
    def __init__(self, provider: str, openai_api_key: Optional[str], openai_model: str,
                 ollama_base_url: str, ollama_model: str) -> None:
        self.provider = provider
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.ollama_base_url = ollama_base_url.rstrip("/")
        self.ollama_model = ollama_model

    def _has_openai(self) -> bool:
        try:
            import openai  # type: ignore
            _ = openai
            return True
        except Exception:
            return False

    def _choose_provider(self) -> str:
        if self.provider in {"openai", "ollama", "none"}:
            return self.provider
        # auto
        if self._has_openai() and self.openai_api_key:
            return "openai"
        # try ollama if reachable
        if self._ollama_reachable():
            return "ollama"
        # fallback to none
        return "none"

    def _ollama_reachable(self) -> bool:
        try:
            import requests  # type: ignore
        except Exception:
            return False
        try:
            url = f"{self.ollama_base_url}/api/tags"
            r = requests.get(url, timeout=1.5)
            return r.ok
        except Exception:
            return False

    def chat(self, prompt: str, system: Optional[str] = None) -> LLMResponse:
        provider = self._choose_provider()
        if provider == "openai":
            return self._chat_openai(prompt, system=system)
        if provider == "ollama":
            return self._chat_ollama(prompt, system=system)
        # none
        return LLMResponse(text="I am offline and cannot access an LLM right now.")

    # --- Providers ---
    def _chat_openai(self, prompt: str, system: Optional[str]) -> LLMResponse:
        import openai  # type: ignore

        client = openai.OpenAI(api_key=self.openai_api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            temperature=0.3,
        )
        text = resp.choices[0].message.content or ""
        return LLMResponse(text=text.strip())

    def _chat_ollama(self, prompt: str, system: Optional[str]) -> LLMResponse:
        url = f"{self.ollama_base_url}/api/chat"
        headers = {"Content-Type": "application/json"}
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.3},
        }
        try:
            import requests  # type: ignore
            r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
            r.raise_for_status()
            data = r.json()
            message = data.get("message", {})
            text = message.get("content", "")
            return LLMResponse(text=(text or "").strip())
        except Exception as e:
            return LLMResponse(text=f"[ollama error] {e}")
