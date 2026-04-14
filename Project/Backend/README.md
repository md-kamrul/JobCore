# Backend Services

This directory contains all backend services used by JobCore.

## Services

### 1) Job Agent Service

Path: jobAgent/jobFinderAgent

Purpose:
- Conversational job search API
- Intent routing (chat vs search)
- Apply link extraction
- Interactive Google Form auto-apply workflow

Runtime:
- Flask
- Port: 5001

Related module:
- jobAgent/jobApplyAgent (Selenium automation helpers)

### 2) Resume Checker Service

Path: resumeChecker

Purpose:
- ATS-style resume analysis against role/job description
- JD match score
- Missing keyword extraction
- Profile summary recommendations

Runtime:
- Flask
- Port: 5004

### 3) Mock Interview Service

Path: mockInterview

Purpose:
- Generate interview questions by role/level
- Evaluate candidate answers and provide feedback

Runtime:
- FastAPI
- Port: 5002 (default)

## Backend Architecture

```text
Frontend
  |- /job-agent       -> jobFinderAgent API (5001)
  |- /resume-checker  -> resumeChecker API (5004)
  |- /mock-interview  -> currently Vapi voice demo link (API available at 5002)

jobFinderAgent
  |- /api/chat
  |- /api/search-jobs
  |- /api/extract-apply-url
  |- /api/apply/*
  |- uses jobApplyAgent internals
```

## Setup

Create and use separate virtual environments per service.

### Job Agent

```bash
cd jobAgent/jobFinderAgent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api.py
```

### Resume Checker

```bash
cd resumeChecker
python3 -m venv .venv
source .venv/bin/activate
pip install -r Requirements.txt
python app.py
```

### Mock Interview

```bash
cd mockInterview
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5002 --reload
```

## Environment Variables

### jobFinderAgent/.env

```env
NEBIUS_API_KEY=
SERPAPI_API_KEY=
# Optional
BRIGHT_DATA_API_KEY=
OPENAI_API_KEY=
```

### resumeChecker/.env.local

```env
OPENAI_API_KEY=
```

### mockInterview/.env.local

```env
OPENAI_API_KEY=
PORT=5002
```

## Health Checks

- Job Agent: GET http://localhost:5001/api/health
- Resume Checker: GET http://localhost:5004/health
- Mock Interview: GET http://localhost:5002/health

## Notes

- Google Form automation requires local Google Chrome.
- Resume checker expects PDF upload from frontend.
- The mock interview backend is available as API, while the current frontend page primarily links to an external voice interview demo.
