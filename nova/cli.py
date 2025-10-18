from __future__ import annotations

import os
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
from .session import Session
from .voice import tts_save_wav, stt_from_wav

app = typer.Typer(add_completion=False)
console = Console()


def banner() -> None:
    console.print(Panel.fit("[bold cyan]Nova[/] — mini J.A.R.V.I.S. CLI", border_style="cyan"))


@app.callback()
def _main(ctx: typer.Context) -> None:
    load_dotenv()
    if ctx.invoked_subcommand is None:
        banner()
        console.print("Run 'nova help' for commands.")


@app.command(help="Run a quick self-test to verify install")
def doctor() -> None:
    banner()
    checks = {
        "python": sys.version,
        "cwd": os.getcwd(),
        "OPENAI_API_KEY set": bool(os.getenv("OPENAI_API_KEY")),
    }
    for key, value in checks.items():
        console.print(f"[bold]{key}[/]: {value}")


@app.command(help="Chat with Nova (LLM-backed)")
def chat(prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="User prompt")) -> None:
    banner()
    if not prompt:
        console.print("[yellow]Provide --prompt/-p, e.g. nova chat -p 'hello'\n")
        raise typer.Exit(code=2)

    # Use the simple agent/session for a single turn
    session = Session()
    obs = session.run(prompt)
    console.print(obs.text)


@app.command(help="Run an action directly: run:<cmd> | read:<path> | write:<path>::<content>")
def act(goal: str = typer.Argument(..., help="Goal/action, e.g. run:ls -la")) -> None:
    banner()
    session = Session()
    obs = session.run(goal)
    console.print(obs.text)


@app.command(help="Synthesize speech (stub)")
def tts(text: str = typer.Argument(...), out: str = typer.Option("/tmp/nova_tts.wav", "--out")) -> None:
    banner()
    res = tts_save_wav(text, out)
    console.print(res)


@app.command(help="Transcribe speech (stub)")
def stt(path: str = typer.Argument(...)) -> None:
    banner()
    res = stt_from_wav(path)
    console.print(res)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
