from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel

from .config import JarvisConfig
from .orchestrator import Orchestrator
from .memory import ConversationMemory


console = Console()


def run_chat(session: str) -> None:
    config = JarvisConfig.load()
    orch = Orchestrator(config)

    data_dir = Path.cwd() / "jarvis_data"
    mem = ConversationMemory(data_dir / "memory.db")

    console.print(Panel.fit("J.A.R.V.I.S. CLI — type 'exit' to quit", title="Jarvis"))

    history = mem.recent(session, limit=20)
    messages: List[dict] = [orch.build_system_message()] + history

    while True:
        try:
            user = console.input("[bold cyan]You[/] › ")
        except (EOFError, KeyboardInterrupt):
            console.print("\nBye.")
            break
        if user.strip().lower() in {"exit", ":q", "quit"}:
            break
        if not user.strip():
            continue

        messages.append({"role": "user", "content": user})
        mem.append(session, "user", user)

        res = orch.step(messages)
        assistant_text = res["content"]
        messages = res["messages"]
        mem.append(session, "assistant", assistant_text)

        console.print(f"[bold green]Jarvis[/]: {assistant_text}")


def run_ask(text: str, session: str) -> None:
    config = JarvisConfig.load()
    orch = Orchestrator(config)

    data_dir = Path.cwd() / "jarvis_data"
    mem = ConversationMemory(data_dir / "memory.db")

    messages: List[dict] = [orch.build_system_message()] + mem.recent(session, limit=10)
    messages.append({"role": "user", "content": text})

    res = orch.step(messages)
    assistant_text = res["content"]

    console.print(assistant_text)

    mem.append(session, "user", text)
    mem.append(session, "assistant", assistant_text)


def run_tools_list() -> None:
    config = JarvisConfig.load()
    orch = Orchestrator(config)
    specs = orch.tool_specs()
    for spec in specs:
        fn = spec["function"]
        console.print(f"- [bold]{fn['name']}[/]: {fn['description']}")


def run_config_show() -> None:
    cfg = JarvisConfig.load()
    console.print(
        Panel.fit(
            f"provider: {cfg.provider}\nmodel: {cfg.model}\nbase_dir: {cfg.base_dir}\nallowed_commands: {cfg.allowed_commands}",
            title="Config",
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="jarvis", description="J.A.R.V.I.S. CLI Assistant")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_chat = sub.add_parser("chat", help="Interactive chat session")
    p_chat.add_argument("--session", default="default", help="Session name for memory")

    p_ask = sub.add_parser("ask", help="Ask a single question")
    p_ask.add_argument("text", help="Prompt to ask")
    p_ask.add_argument("--session", default="default", help="Session name for memory")

    sub.add_parser("tools", help="List available tools")
    sub.add_parser("config", help="Show resolved config")

    args = parser.parse_args()

    if args.cmd == "chat":
        run_chat(args.session)
    elif args.cmd == "ask":
        run_ask(args.text, args.session)
    elif args.cmd == "tools":
        run_tools_list()
    elif args.cmd == "config":
        run_config_show()
    else:
        parser.print_help()
