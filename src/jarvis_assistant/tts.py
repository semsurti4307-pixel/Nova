from __future__ import annotations

from typing import Optional


def speak(text: str, enabled: bool = False, voice_rate_wpm: Optional[int] = None) -> bool:
    """Speak the given text using pyttsx3 if available and enabled.

    Returns True if TTS was performed, False otherwise.
    """
    if not enabled:
        return False

    try:
        import pyttsx3  # type: ignore
    except Exception:
        # TTS not available, skip gracefully
        return False

    try:
        engine = pyttsx3.init()
        if voice_rate_wpm is not None:
            engine.setProperty("rate", int(voice_rate_wpm))
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        # Any runtime TTS error: fail closed
        return False
