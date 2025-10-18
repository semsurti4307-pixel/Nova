from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _str_to_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_dotenv_if_available(dotenv_path: Optional[str] = None) -> None:
    """Load .env if python-dotenv is available. Silently skip otherwise."""
    try:
        from dotenv import load_dotenv  # type: ignore
    except Exception:
        return
    load_dotenv(dotenv_path=dotenv_path)


@dataclass
class JarvisConfig:
    llm_provider: str
    openai_api_key: Optional[str]
    openai_model: str
    ollama_base_url: str
    ollama_model: str
    tts_enabled: bool
    voice_rate_wpm: Optional[int]


def get_config() -> JarvisConfig:
    load_dotenv_if_available()

    llm_provider = os.environ.get("JARVIS_LLM_PROVIDER", "auto").strip().lower()

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip()
    ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.1").strip()

    tts_enabled = _str_to_bool(os.environ.get("JARVIS_TTS"), default=False)
    voice_rate_wpm_env = os.environ.get("JARVIS_TTS_RATE_WPM")
    voice_rate_wpm = int(voice_rate_wpm_env) if voice_rate_wpm_env and voice_rate_wpm_env.isdigit() else None

    return JarvisConfig(
        llm_provider=llm_provider,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        tts_enabled=tts_enabled,
        voice_rate_wpm=voice_rate_wpm,
    )
