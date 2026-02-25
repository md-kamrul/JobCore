# Google Form Submit Agent (MCP + Selenium)

This folder contains:
- `mcp_form_server.py`: an MCP (stdio) server exposing a `submit_google_form` tool.
- `test.py`: a simple CLI "agent" that asks for a Google Form URL and calls the MCP tool.

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
- For real forms, submission may fail if the form has required fields. This demo only clicks the Submit button.
