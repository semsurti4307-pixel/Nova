from __future__ import annotations

import urllib.request
from dataclasses import dataclass
from typing import Dict


@dataclass
class HttpGetTool:
    name: str = "web.http_get"
    description: str = "HTTP GET a URL and return text content. params: {url}"

    def run(self, params: Dict) -> str:
        url = params.get("url")
        if not url:
            return "Missing 'url' parameter."
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                data = resp.read()
                try:
                    return data.decode(charset, errors="replace")
                except Exception:
                    return data.decode("utf-8", errors="replace")
        except Exception as exc:
            return f"HTTP error: {exc}"
