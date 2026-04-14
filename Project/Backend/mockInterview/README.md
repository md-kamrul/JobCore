# Mock Interview Backend

FastAPI service for generating interview questions and evaluating answers.

## Features

- Generate one interview question based on role and level
- Evaluate candidate answer with score and improvement tips
- Fallback local responses if AI provider call fails

## Tech

- FastAPI
- Uvicorn
- OpenAI Python SDK
- python-dotenv

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5002 --reload
```

Default URL: http://localhost:5002

## Environment

Create .env.local in this directory:

```env
OPENAI_API_KEY=
PORT=5002
```

## API Endpoints

### GET /

Returns welcome message.

### GET /health

Returns service status message.

### POST /api/interview/question

Request body:

```json
{
  "role": "Backend Developer",
  "level": "Junior"
}
```

Response:

```json
{
  "question": "How would you design a scalable REST API with caching and rate limiting?"
}
```

### POST /api/interview/evaluate

Request body:

```json
{
  "role": "Backend Developer",
  "level": "Junior",
  "question": "How would you design a scalable REST API?",
  "answer": "I would start by..."
}
```

Response:

```json
{
  "evaluation": "Score: 7/10\nFeedback: ..."
}
```

## Notes

- If OpenAI call fails, the service returns deterministic fallback responses.
- This backend API exists and is runnable, while the current frontend mock interview page mainly links to an external voice demo and keeps text mode as coming soon.
