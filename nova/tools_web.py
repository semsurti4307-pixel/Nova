from __future__ import annotations

import httpx


def http_get(url: str, timeout_seconds: float = 15.0) -> str:
    try:
        with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            text = resp.text
            if len(text) > 5000:
                return text[:5000] + "\n... [truncated]"
            return text
    except Exception as ex:  # noqa: BLE001
        return f"GET error: {ex}"
