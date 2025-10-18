# Nova – mini J.A.R.V.I.S. CLI

Nova is a local-first AI assistant CLI inspired by J.A.R.V.I.S.

## Quickstart

1) Install

```bash
python3 -m pip install -e .
```

2) Configure environment

```bash
cp .env.example .env
# edit .env and add OPENAI_API_KEY
```

3) Verify

```bash
nova doctor
```

## Usage

- `nova act 'run:<cmd>'` – run a shell command
- `nova act 'read:<path>'` – read a file
- `nova act 'write:<path>::<content>'` – write content to a file
- `nova act 'get:<url>'` – fetch a web page
- `nova chat -p "<prompt>"` – LLM-backed chat (requires OPENAI_API_KEY)

Examples:

```bash
nova act 'run:echo hello'
nova act 'read:README.md'
nova act 'write:/tmp/hi.txt::Hello Nova'
nova act 'get:https://example.com'
```

## Notes

- Set `NOVA_MODEL` in `.env` to change the model (default: `gpt-4o-mini`).
- Web/chat features require internet and a valid OpenAI key.
