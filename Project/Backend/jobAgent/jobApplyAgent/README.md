# jobApplyAgent

Google Form automation module used by the Job Finder API.

This package is imported by:

- ../jobFinderAgent/api.py

It is not intended to run as a standalone service.

## Purpose

- Detect Google Form apply links
- Start Selenium sessions for form filling
- Parse questions (text, email, textarea, radio, checkbox, dropdown, file)
- Resolve likely answers from user profile data
- Continue interactively when required answers are missing
- Handle Gmail sign-in gating flow when present

## Key Components

- google_form_apply.py
	- low-level form scanning/filling helpers
	- Chrome driver setup
	- URL normalization and Google Form detection
- interactive_google_form.py
	- interactive session lifecycle
	- question indexing
	- answer-and-advance orchestration
- profile_resolver.py
	- maps profile information into likely form answers
- state.py
	- in-memory session tracking for multi-step apply flow

## Runtime Requirements

- Python dependencies installed in jobFinderAgent virtual environment
- Google Chrome installed locally
- Compatible ChromeDriver/Selenium runtime

Use setup from jobFinderAgent directory:

```bash
cd ../jobFinderAgent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Integration Flow

1. Frontend requests apply URL extraction.
2. jobFinderAgent checks if URL is a Google Form.
3. If Google Form, jobApplyAgent starts interactive form session.
4. Module auto-fills what it can from profile.
5. Missing questions are returned to frontend for user response.
6. Responses are posted back and session continues until submitted or failed.

## Supported Inputs

- text
- email
- textarea
- radio
- checkbox
- dropdown
- file upload (requires local file path)

## Limitations

- Some forms require account permissions that may block automation.
- UI structure changes in Google Forms can affect selectors.
- File upload questions can be browser-policy sensitive.
- Long/complex dynamic forms may require manual fallback.

## Debug Tips

- Use non-headless mode for difficult forms to observe behavior.
- Validate that detected question label matches visible form text.
- Re-run apply flow if session expires or browser closes.
