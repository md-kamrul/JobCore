# Mock Interview Backend

FastAPI service for generating interview questions and evaluating answers.

## Features

- Generate one interview question based on role and level
- Evaluate candidate answer with score and improvement tips
- Run a multi-question text-based mock interview session
- Return an end-of-interview summary with average scores and strongest/weakest areas
- Fallback local responses if AI provider call fails

## Tech

- FastAPI
- Uvicorn
- OpenAI Python SDK
- python-dotenv
- requests

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 5002 --reload
```

Default URL: http://localhost:5002

If you see ModuleNotFoundError for requests, install it in the same virtual environment with:

```bash
pip install requests
```

## Environment

Create .env.local in this directory:

```env
OPENAI_API_KEY=
MODEL_API_URL=http://localhost:5000
PORT=5002
```

## API Endpoints

### GET /options

Returns available roles, topics, and difficulty levels for the text interview setup screen.

### GET /

Returns welcome message.

### GET /health

Returns service status message.

### POST /api/interview/start

Starts a text interview session and returns the first question.

Request body:

```json
{
  "role": "Backend Developer",
  "topic": "Technical",
  "difficulty": "Medium",
  "num_questions": 5
}
```

### POST /api/interview/answer

Submits an answer for the active session and returns the next question or the completed state.

Request body:

```json
{
  "session_id": "uuid-from-start-response",
  "answer": "I would..."
}
```

### GET /api/interview/summary/{session_id}

Returns the final summary, average scores, and question-by-question breakdown for a completed session.

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
- The frontend mock interview page now includes a text-based mode that uses this API, while the voice option still opens an external Vapi demo.
