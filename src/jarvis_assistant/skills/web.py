from __future__ import annotations

import webbrowser
import urllib.parse
from typing import Optional


def open_url(url: str) -> bool:
    try:
        return webbrowser.open(url)
    except Exception:
        return False


def search_web(query: str, engine: str = "duckduckgo") -> Optional[str]:
    q = urllib.parse.quote_plus(query)
    if engine == "google":
        url = f"https://www.google.com/search?q={q}"
    elif engine == "bing":
        url = f"https://www.bing.com/search?q={q}"
    else:
        url = f"https://duckduckgo.com/?q={q}"

    ok = open_url(url)
    return url if ok else None
