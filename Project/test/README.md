# Google Form Submit Agent (MCP + Selenium)

This folder contains:
- `mcp_form_server.py`: an MCP (stdio) server exposing tools to start a session, read questions, answer them, and submit.
- `test.py`: a simple CLI "agent" that asks for a Google Form URL, then prompts you question-by-question and submits at the end.

## Setup (macOS)

```bash
cd test
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
cd test
source .venv/bin/activate
python test.py
```

## Notes
- Requires Google Chrome installed.
- This is best-effort automation; Google Forms DOM can change, and required/validated fields may still block submission.
