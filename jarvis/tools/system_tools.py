from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
import webbrowser


@dataclass
class ToolsRegistry:
    base_dir: Path
    allowed_commands: List[str]

    # ---------- Tool specs for LLM function-calling ----------
    def get_tool_specs(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "open_url",
                    "description": "Open a URL in the user's default browser.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The full URL to open (include https://)",
                            }
                        },
                        "required": ["url"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a text file under the allowed base directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path relative to base directory or absolute inside it.",
                            }
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write text to a file under the base directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                            "mode": {
                                "type": "string",
                                "enum": ["overwrite", "append"],
                                "default": "overwrite",
                            },
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "run_safe_command",
                    "description": "Run a whitelisted shell command with args; returns stdout/stderr.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Executable name; must be allowlisted.",
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Arguments to pass to the command.",
                                "default": [],
                            },
                            "timeout_s": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 120,
                                "default": 15,
                            },
                        },
                        "required": ["command"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_files",
                    "description": "Glob search for files under base directory.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"},
                            "limit": {"type": "integer", "default": 50},
                        },
                        "required": ["pattern"],
                    },
                },
            },
        ]

    # ---------- Execution layer ----------
    def execute(self, name: str, arguments_json: str) -> Tuple[str, str]:
        try:
            args: Dict[str, Any] = json.loads(arguments_json or "{}")
        except Exception:
            return "error", json.dumps({"error": "Invalid JSON arguments"})

        try:
            if name == "open_url":
                return "success", self._open_url(args["url"])  # type: ignore[index]
            if name == "read_file":
                return "success", self._read_file(args["path"])  # type: ignore[index]
            if name == "write_file":
                mode = args.get("mode", "overwrite")
                return "success", self._write_file(args["path"], args["content"], mode)  # type: ignore[index]
            if name == "run_safe_command":
                return "success", self._run_safe_command(
                    args["command"], args.get("args", []), int(args.get("timeout_s", 15))
                )
            if name == "search_files":
                return "success", self._search_files(args["pattern"], int(args.get("limit", 50)))
        except Exception as e:
            return "error", json.dumps({"error": str(e)})

        return "error", json.dumps({"error": f"Unknown tool: {name}"})

    # ---------- Helpers ----------
    def _resolve_under_base(self, path_str: str) -> Path:
        p = Path(path_str)
        if not p.is_absolute():
            p = (self.base_dir / p).resolve()
        else:
            p = p.resolve()
        base = self.base_dir.resolve()
        base_str = str(base)
        p_str = str(p)
        if not (p_str == base_str or p_str.startswith(base_str + os.sep)):
            raise PermissionError("Path is outside allowed base directory")
        return p

    def _open_url(self, url: str) -> str:
        try:
            webbrowser.open(url)
            return json.dumps({"opened": url})
        except Exception as e:
            return json.dumps({"opened": False, "error": str(e)})

    def _read_file(self, path: str) -> str:
        p = self._resolve_under_base(path)
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        return json.dumps({"path": str(p), "content": content})

    def _write_file(self, path: str, content: str, mode: str = "overwrite") -> str:
        p = self._resolve_under_base(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if mode == "append" and p.exists():
            with open(p, "a", encoding="utf-8") as f:
                f.write(content)
        else:
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
        return json.dumps({"path": str(p), "bytes": len(content)})

    def _run_safe_command(self, command: str, args: List[str], timeout_s: int) -> str:
        if command not in self.allowed_commands:
            raise PermissionError(f"Command '{command}' not in allowlist")
        cmd = [command] + [a for a in args]
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_s,
                text=True,
            )
            return json.dumps(
                {
                    "command": cmd,
                    "exit_code": res.returncode,
                    "stdout": res.stdout,
                    "stderr": res.stderr,
                }
            )
        except subprocess.TimeoutExpired:
            return json.dumps({"command": cmd, "timeout": timeout_s, "error": "timeout"})

    def _search_files(self, pattern: str, limit: int) -> str:
        # Use Python's glob recursively
        base = self.base_dir
        matches: List[str] = []
        for p in base.rglob(pattern):
            if p.is_file():
                rel = p.relative_to(base)
                matches.append(str(rel))
                if len(matches) >= limit:
                    break
        return json.dumps({"pattern": pattern, "results": matches})
