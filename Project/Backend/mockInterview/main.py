from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os
from pathlib import Path

# Load environment variables from .env.local
env_path = Path(__file__).parent / ".env.local"
load_dotenv(dotenv_path=env_path)

app = FastAPI()
PORT = int(os.getenv("PORT", 5002))

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    role: str
    level: str

class EvaluateRequest(BaseModel):
    role: str
    level: str
    question: str
    answer: str


def fallback_question(role: str, level: str) -> str:
    role_key = role.lower().strip()

    role_questions = {
        "frontend developer": "How would you optimize a React app that renders a large list frequently?",
        "backend developer": "How would you design a scalable REST API with caching and rate limiting?",
        "full stack developer": "How would you deliver a feature end-to-end from UI to database?",
        "ai engineer": "How would you evaluate and monitor an ML model in production?",
    }

    return role_questions.get(
        role_key,
        f"As a {level} {role}, describe a complex technical problem you solved and explain your architecture decisions.",
    )


def fallback_evaluation(answer: str) -> str:
    cleaned_answer = answer.strip()
    if len(cleaned_answer) < 40:
        score = 4
        detail = "Your answer is too short and lacks technical depth."
    elif len(cleaned_answer) < 120:
        score = 6
        detail = "You covered some points, but the explanation needs more structure and concrete examples."
    else:
        score = 8
        detail = "Good coverage and clarity. Add more measurable impact and trade-off discussion for a stronger answer."

    return (
        f"Score: {score}/10\n"
        f"Feedback: {detail}\n"
        "How to improve: Use a clear structure (problem, approach, outcome), mention tools/technologies, "
        "and include one real example with metrics."
    )


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Mock Interview API"}


@app.get("/health")
async def health():
    return {"message": "Server is running"}


@app.post("/api/interview/question")
async def get_question(request: QuestionRequest):
    try:
        user_prompt = (
            f"Generate ONE interview question for a {request.level} {request.role}. "
            "Return only the question text."
        )

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful interview assistant."},
                {"role": "user", "content": user_prompt},
            ],
        )

        question = completion.choices[0].message.content.strip()
        return {"question": question}
    except Exception:
        return {
            "question": fallback_question(request.role, request.level),
            "fallback": True,
            "note": "AI provider unavailable, returned local fallback question.",
        }


@app.post("/api/interview/evaluate")
async def evaluate_answer(request: EvaluateRequest):
    try:
        user_prompt = f"""
You are an interviewer.
Role: {request.role}
Level: {request.level}

Interview Question: \"{request.question}\"
Candidate Answer: \"{request.answer}\"

1) Give a score out of 10.
2) Give very short feedback (2-3 lines).
3) Suggest how to improve.

Respond in clear text.
"""

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict but fair interviewer."},
                {"role": "user", "content": user_prompt},
            ],
        )

        evaluation = completion.choices[0].message.content.strip()
        return {"evaluation": evaluation}
    except Exception:
        return {
            "evaluation": fallback_evaluation(request.answer),
            "fallback": True,
            "note": "AI provider unavailable, returned local fallback evaluation.",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
