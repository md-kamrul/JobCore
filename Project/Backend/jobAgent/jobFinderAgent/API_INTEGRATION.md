# Job Agent API Integration

This guide explains how the frontend Job Agent page integrates with the backend service.

## Integration Topology

- Frontend page: ../../Frontend/src/pages/JobAgent.jsx
- Backend API: ./api.py
- Base URL: http://localhost:5001

The frontend uses the backend for:

- conversational chat and job search
- apply-link extraction from job details
- interactive Google Form auto-apply flow
- Gmail sign-in handoff and polling when required by forms

## Run Integration Locally

### 1) Start backend

```bash
cd /Users/kamrul/Developer/CSE499/JobCore/Project/Backend/jobAgent/jobFinderAgent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api.py
```

### 2) Start frontend

```bash
cd /Users/kamrul/Developer/CSE499/JobCore/Project/Frontend
npm install
npm run dev
```

### 3) Open app

- Frontend: http://localhost:5173
- Go to /job-agent

## Endpoint Contract

### GET /api/health

Health check used for service verification.

### POST /api/chat

Main chat endpoint.

Request:

```json
{
  "message": "find some mern jobs in bangladesh",
  "history": []
}
```

Response fields:

- success: boolean
- type: conversation | job_results
- message: response text or job result payload
- is_search: boolean

### POST /api/search-jobs

Optional direct endpoint for search-only behavior.

### POST /api/extract-apply-url

Request:

```json
{
  "detailsUrl": "https://example.com/job-details"
}
```

Response includes:

- applyUrl
- found
- isGoogleForm
- message

### POST /api/apply/start

Starts interactive auto-apply session.

Request:

```json
{
  "applyUrl": "https://forms.gle/...",
  "profile": {
    "full_name": "Candidate Name",
    "email": "candidate@example.com",
    "cv_name": "resume.pdf",
    "cv_download_url": "https://signed-url"
  },
  "headless": true
}
```

Possible statuses:

- needs_info
- needs_confirm
- submitted
- error

### POST /api/apply/continue

Continues session with user response.

Request:

```json
{
  "applicationId": "...",
  "answers": {
    "What is your name?": "md. kamrul islam"
  },
  "headless": true
}
```

### POST /api/apply/gmail-login

Starts visible browser login when form requires Google sign-in.

### GET /api/apply/gmail-login/status

Frontend polls this endpoint until login completes.

Query string:

- applicationId

## Frontend Behavior Notes

- Frontend currently uses hardcoded backend base URL http://localhost:5001.
- Auto-apply logic is message-driven and can ask user for missing form answers.
- For file upload fields, backend expects local file resolution logic and can use profile CV data.

## Expected Service Dependencies

- OPENAI_API_KEY
- SERPAPI_API_KEY
- local Chrome installation for Google Form automation

## Troubleshooting

- 400 with query/message required:
  - Ensure frontend is sending non-empty message.
- Unknown or expired applicationId:
  - Restart apply flow from the latest job card.
- Form not submitted:
  - Some forms enforce restrictions (sign-in, permissions, file policies).
- Backend starts but searches fail:
  - Confirm SERPAPI_API_KEY is configured and valid.
