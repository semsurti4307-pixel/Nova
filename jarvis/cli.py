import argparse
import os
import sys
from typing import Optional

from .agent import Agent
from .llm.simple import SimpleRuleBasedModel
from .tools.registry import ToolRegistry
from .tools.files import FileReadTool, FileWriteTool, FileListTool
from .tools.system import SystemShellTool
from .tools.web import HttpGetTool
from .utils.logging import get_logger


logger = get_logger(__name__)


def build_registry(allow_system: bool) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(FileReadTool())
    registry.register(FileWriteTool())
    registry.register(FileListTool())
    registry.register(HttpGetTool())
    registry.register(SystemShellTool(allow_system=allow_system))
    return registry


def run_repl(agent: Agent) -> int:
    print("Mini JARVIS ready. Type 'exit' or Ctrl-D to quit.")
    try:
        while True:
            try:
                user_input = input("You> ").strip()
            except EOFError:
                print()
                break
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit"}:
                break
            response = agent.respond(user_input)
            print(f"JARVIS> {response}")
    except KeyboardInterrupt:
        print()
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jarvis",
        description=(
            "A minimal local assistant with basic tools (files, web, shell)."
        ),
    )
    parser.add_argument(
        "-m",
        "--message",
        help="One-shot message for the assistant to respond to.",
    )
    parser.add_argument(
        "--repl",
        action="store_true",
        help="Start an interactive REPL session.",
    )
    parser.add_argument(
        "--allow-system",
        action="store_true",
        help=(
            "Allow running system shell commands via the system.shell tool."
        ),
    )

    args = parser.parse_args(argv)

    registry = build_registry(allow_system=args.allow_system)
    model = SimpleRuleBasedModel()
    agent = Agent(model=model, tools=registry)

    if args.repl or (args.message is None):
        return run_repl(agent)

    response = agent.respond(args.message)
    print(response)
    return 0
