from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from .config import get_config
from . import __version__
from .llm import LLMClient
from .skills.shell import run_command
from .skills.web import open_url, search_web
from .tts import speak


SYSTEM_PROMPT = (
    "You are a helpful, concise assistant called JARVIS. "
    "You can suggest commands, summarize output, and remain brief."
)


def cmd_chat(args: argparse.Namespace) -> int:
    cfg = get_config()
    client = LLMClient(
        provider=cfg.llm_provider,
        openai_api_key=cfg.openai_api_key,
        openai_model=cfg.openai_model,
        ollama_base_url=cfg.ollama_base_url,
        ollama_model=cfg.ollama_model,
    )

    prompt = args.prompt if args.prompt else "".join(sys.stdin.readlines())
    if not prompt.strip():
        print("No prompt provided.", file=sys.stderr)
        return 2

    resp = client.chat(prompt=prompt, system=SYSTEM_PROMPT)
    print(resp.text)
    speak(resp.text, enabled=cfg.tts_enabled, voice_rate_wpm=cfg.voice_rate_wpm)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    result = run_command(args.command)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.exit_code


def cmd_open(args: argparse.Namespace) -> int:
    ok = open_url(args.url)
    if not ok:
        print("Failed to open URL", file=sys.stderr)
        return 1
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    url = search_web(args.query, engine=args.engine)
    if url:
        print(url)
        return 0
    # If browser cannot open, at least print the URL we would open
    from urllib.parse import quote_plus
    q = quote_plus(args.query)
    if args.engine == "google":
        fallback = f"https://www.google.com/search?q={q}"
    elif args.engine == "bing":
        fallback = f"https://www.bing.com/search?q={q}"
    else:
        fallback = f"https://duckduckgo.com/?q={q}"
    print(fallback)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="jarvis", description="Mini JARVIS assistant CLI")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("chat", help="Chat with the LLM")
    c.add_argument("prompt", nargs=argparse.REMAINDER, help="Prompt text (or pipe via stdin)")
    c.set_defaults(func=cmd_chat)

    r = sub.add_parser("run", help="Run a shell command")
    r.add_argument("command", nargs=argparse.REMAINDER, help="Command to run")
    r.set_defaults(func=cmd_run)

    o = sub.add_parser("open", help="Open a URL in the browser")
    o.add_argument("url")
    o.set_defaults(func=cmd_open)

    s = sub.add_parser("search", help="Search the web and open results")
    s.add_argument("query", nargs=argparse.REMAINDER)
    s.add_argument("--engine", choices=["duckduckgo", "google", "bing"], default="duckduckgo")
    s.set_defaults(func=cmd_search)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)

    # join remaining args into a single string for chat/run/search
    if ns.cmd == "chat":
        if hasattr(ns, "prompt") and isinstance(ns.prompt, list):
            ns.prompt = " ".join(ns.prompt).strip()
    elif ns.cmd == "run":
        if hasattr(ns, "command") and isinstance(ns.command, list):
            ns.command = " ".join(ns.command).strip()
    elif ns.cmd == "search":
        if hasattr(ns, "query") and isinstance(ns.query, list):
            ns.query = " ".join(ns.query).strip()

    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
