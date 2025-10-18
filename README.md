### Mini JARVIS Assistant (CLI)

A minimal, local-first J.A.R.V.I.S.-style assistant you can run from your terminal. It can:

- Run shell commands safely and print their output
- Open URLs and perform web searches
- Chat via an LLM (OpenAI or local Ollama), with graceful offline fallback
- Optionally speak responses using text-to-speech

This is not AGI, but a practical, hackable starter that combines voice/LLM/system control patterns inspired by J.A.R.V.I.S.

### Quick start

1) Install (editable) with optional extras:

```bash
python3 -m pip install -e .[http,tts,openai]
```

2) Copy and edit environment configuration:

```bash
cp .env.example .env
# set OPENAI_API_KEY or run a local Ollama server
```

3) Try some commands:

```bash
python3 -m jarvis_assistant --version
python3 -m jarvis_assistant run "echo hello"
python3 -m jarvis_assistant search "mini jarvis assistant"
printf "Explain event loop in 1 sentence" | python3 -m jarvis_assistant chat
```

If your PATH includes `~/.local/bin`, you can use the console command:

```bash
jarvis --version
```

### Configuration

Environment variables (load from `.env` if `python-dotenv` is installed):

- `JARVIS_LLM_PROVIDER`: `auto` | `openai` | `ollama` | `none` (default: `auto`)
- `OPENAI_API_KEY`: your OpenAI API key
- `OPENAI_MODEL`: model name (default: `gpt-4o-mini`)
- `OLLAMA_BASE_URL`: e.g. `http://127.0.0.1:11434`
- `OLLAMA_MODEL`: e.g. `llama3.1`
- `JARVIS_TTS`: `true` to enable local TTS (default: `false`)
- `JARVIS_TTS_RATE_WPM`: optional speech rate (e.g. `180`)

Notes:
- With `auto`, the assistant will use OpenAI if the SDK and API key are available; otherwise it will attempt to reach a local Ollama server; if neither is available, it falls back to offline mode and prints a helpful message.
- TTS uses `pyttsx3`; if unavailable or errors occur, it silently skips.

### Commands

```bash
jarvis chat <prompt...>           # chat with the configured LLM
jarvis run <command...>           # run a shell command
jarvis open <url>                 # open a URL in your default browser
jarvis search <query...> [--engine duckduckgo|google|bing]
```

You can also use module form:

```bash
python3 -m jarvis_assistant chat "hello"
```

Piping is supported for `chat`:

```bash
printf "What is 2+2?" | jarvis chat
```

### Roadmap ideas

- Add microphone input and wake-word detection
- Add tool-use via structured actions
- Add memory/store and configurable system prompts
- Add richer desktop automation (window/app control)

### License

MIT
