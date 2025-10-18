from __future__ import annotations

from typing import Optional

try:
    import sounddevice as sd  # type: ignore
    import soundfile as sf  # type: ignore
except Exception:  # noqa: BLE001
    sd = None
    sf = None


def is_supported() -> bool:
    return sd is not None and sf is not None


def tts_save_wav(text: str, out_path: str) -> str:
    # Placeholder stub — integrate a real TTS engine if desired
    return f"[TTS stub] Would synthesize: '{text}' -> {out_path}"


def stt_from_wav(path: str) -> str:
    # Placeholder stub — integrate a real STT model if desired
    return f"[STT stub] Would transcribe audio at: {path}"
