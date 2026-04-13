# jobApplyAgent (Agent-B)

Auto-apply logic for job links.

## Google Forms auto-fill (Selenium)

This module is used by the main Job Agent API (Flask) in `jobFinderAgent`.

### Install (recommended: use the same venv as `jobFinderAgent`)

From `JobCore/Project/Backend/jobAgent/jobFinderAgent`:

- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

`requirements.txt` in `jobFinderAgent` includes `selenium` after this update.

### Notes

- Requires Google Chrome installed locally.
- Some forms require sign-in or permission; those cannot be automated reliably.
- File upload questions can be handled if you pass a local file path as `resumePath` in the profile.
