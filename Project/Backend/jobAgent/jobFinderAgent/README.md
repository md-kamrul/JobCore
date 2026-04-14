# Job Finder Agent API

Flask backend for JobCore job search chat and auto-apply orchestration.

## What This Service Does

- Accepts natural-language chat requests from frontend
- Detects whether user message is:
   - general conversation, or
   - a job-search request
- Runs multi-agent search reasoning for job criteria
- Fetches job listings through Google Jobs (SerpAPI)
- Returns markdown job cards for frontend rendering
- Supports apply-link extraction and interactive Google Form application

## Runtime

- Framework: Flask
- Default Port: 5001
- Entry Point: api.py

## Dependencies

Install dependencies from requirements.txt.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment

Create .env in this folder.

```env
NEBIUS_API_KEY=
SERPAPI_API_KEY=

# Optional for extended scraping/auth flows
BRIGHT_DATA_API_KEY=
OPENAI_API_KEY=
```

Required in current implementation:

- NEBIUS_API_KEY
- SERPAPI_API_KEY

## Start Service

```bash
python api.py
```

Or use:

```bash
./start_api.sh
```

Health check:

```bash
curl http://localhost:5001/api/health
```

## API Endpoints

### GET /api/health

Returns service health.

### POST /api/chat

Primary conversational endpoint.

Request:

```json
{
   "message": "find frontend jobs in Bangladesh",
   "history": []
}
```

Response modes:

- type: conversation for regular assistant replies
- type: job_results when intent is job search

### POST /api/search-jobs

Direct job search endpoint.

Request:

```json
{
   "query": "junior mern jobs in dhaka"
}
```

### POST /api/extract-apply-url

Extracts external apply URL from a job details URL.

Request:

```json
{
   "detailsUrl": "https://..."
}
```

### POST /api/apply/start

Starts interactive Google Form auto-apply session.

Request:

```json
{
   "applyUrl": "https://forms.gle/...",
   "profile": {
      "full_name": "...",
      "email": "..."
   },
   "headless": true
}
```

### POST /api/apply/continue

Continues an existing apply session with user answers.

### POST /api/apply/gmail-login

Starts visible Chrome Gmail login flow when form requires sign-in.

### GET /api/apply/gmail-login/status

Poll endpoint used by frontend to detect completed login and continue form flow.

## Auto-Apply Flow Summary

1. Frontend asks backend to extract apply URL.
2. If URL is a Google Form, backend starts an interactive session.
3. Backend tries profile-based auto-answering first.
4. For missing answers, backend asks frontend for user input.
5. Frontend sends answer to continue endpoint.
6. Backend submits form after required fields are completed.

## Notes on Job Results

- Returns markdown-like structured job messages.
- Includes one demo job card at the top for product demonstration.
- Number of returned jobs depends on query and extracted limit (default 5).

## Frontend Integration

Used by frontend page:

- ../../Frontend/src/pages/JobAgent.jsx

See API integration details in API_INTEGRATION.md.

## Troubleshooting

- Missing NEBIUS_API_KEY:
   - Add key in .env and restart server.
- Missing SERPAPI_API_KEY:
   - Add key in .env. Search job scraping depends on this.
- Chrome automation fails:
   - Ensure Google Chrome is installed locally.
- Session expired during apply:
   - Restart apply flow from frontend.
- Slow responses:
   - AI routing and scraping can take 30 to 60 seconds.
