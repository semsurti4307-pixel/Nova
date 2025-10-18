from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class FileReadTool:
    name: str = "files.read"
    description: str = "Read a text file from disk. params: {path}"

    def run(self, params: Dict) -> str:
        path = params.get("path")
        if not path:
            return "Missing 'path' parameter."
        if not os.path.exists(path):
            return f"File not found: {path}"
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as exc:
            return f"Error reading file: {exc}"


@dataclass
class FileWriteTool:
    name: str = "files.write"
    description: str = "Write text content to a file. params: {path, content}"

    def run(self, params: Dict) -> str:
        path = params.get("path")
        content = params.get("content")
        if not path or content is None:
            return "Missing 'path' or 'content' parameter."
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(content))
            return f"Wrote {len(str(content))} bytes to {path}"
        except Exception as exc:
            return f"Error writing file: {exc}"


@dataclass
class FileListTool:
    name: str = "files.list"
    description: str = "List directory contents. params: {path}"

    def run(self, params: Dict) -> str:
        path = params.get("path", ".")
        if not os.path.exists(path):
            return f"Path not found: {path}"
        if os.path.isfile(path):
            return path
        try:
            entries = sorted(os.listdir(path))
            return "\n".join(entries)
        except Exception as exc:
            return f"Error listing directory: {exc}"
