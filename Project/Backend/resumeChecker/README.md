# Resume Checker Backend

Flask API for ATS-style resume analysis.

## Features

- Accepts PDF resume uploads
- Compares resume with target role and optional job description
- Returns:
  - JD Match percentage
  - Missing keywords
  - Profile summary with recommendations

## Tech

- Flask
- Flask-CORS
- PyPDF2
- OpenAI Python SDK

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r Requirements.txt
python app.py
```

Default URL: http://localhost:5004

## Environment

Create .env.local in this directory:

```env
OPENAI_API_KEY=
```

## API Endpoints

### GET /

Returns service info and endpoint descriptions.

### GET /health

Returns backend health and whether OpenAI key is configured.

### POST /check_resume

Multipart form-data fields:

- file: PDF file (required)
- position: target position string (required)
- description: job description text (optional)
- analysis_type: summary or percentage (optional, default summary)

Example using curl:

```bash
curl -X POST http://localhost:5004/check_resume \
  -F "file=@/absolute/path/to/resume.pdf" \
  -F "position=Frontend Developer" \
  -F "description=React, JavaScript, REST API" \
  -F "analysis_type=summary"
```

## Response Shape

Success response includes:

```json
{
  "success": true,
  "analysis": "{...json string...}",
  "recommendation": "{...json string...}",
  "parsed": {
    "JD Match": "65%",
    "MissingKeywords": ["Laravel", "Shopify"],
    "Profile Summary": "..."
  }
}
```

## Frontend Integration

The frontend page at /resume-checker calls:

- http://localhost:5004/check_resume

## Troubleshooting

- Missing OPENAI_API_KEY: ensure .env.local exists in this folder.
- PDF parsing fails: try a text-based PDF (not a scanned image-only PDF).
- CORS/network issues: verify frontend and backend are running and reachable on expected ports.
