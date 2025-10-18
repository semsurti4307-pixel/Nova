# Jarvis (CLI)

Create a practical, local-first J.A.R.V.I.S.-style assistant you can run from your terminal.

## Quick start

1) Python 3.10+

2) Install deps:

```bash
pip install -r requirements.txt
```

3) (Optional) Set OpenAI key for online LLM:

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
export $(grep -v '^#' .env | xargs -d'\n')
```

4) Run

```bash
python -m jarvis chat
# or
python -m jarvis ask "Summarize this repo"
```

Without an `OPENAI_API_KEY`, Jarvis falls back to an offline echo provider so you can still try the flow and tools.

## Config

Edit `config.yaml`:

```yaml
jarvis:
  provider: openai
  model: gpt-4o-mini
  system_prompt: |
    You are J.A.R.V.I.S., a precise, helpful assistant. Be concise.
paths:
  base_dir: .
tools:
  allowed_commands: [ls, pwd, echo]
```

- `base_dir`: all file operations are confined under this path
- `allowed_commands`: strict allowlist for `run_safe_command`

## Tools (built-in)
- `open_url(url)`: open link in default browser
- `read_file(path)`: read file under `base_dir`
- `write_file(path, content, mode)`: write/append text file
- `run_safe_command(command, args, timeout_s)`: allowlisted shell command
- `search_files(pattern, limit)`: glob under `base_dir`

## Safety
- File and shell access are confined and allowlisted
- Jarvis prints and confirms any tool outcome in the chat loop

