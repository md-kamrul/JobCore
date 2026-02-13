# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os
from pathlib import Path

# Load variables from .env
env_path = Path(__file__).parent / ".env.local"
load_dotenv(dotenv_path=env_path)

# Create FastAPI app
app = FastAPI()
PORT = int(os.getenv("PORT", 5000))

# OpenAI client
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Middlewares - CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request bodies
class QuestionRequest(BaseModel):
    role: str
    level: str

class EvaluateRequest(BaseModel):
    role: str
    level: str
    question: str
    answer: str

# Simple test route
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Mock Interview API "}

@app.get("/health")
async def health():
    return {"message": "Server is running"}

# 1) Route: Get an interview question
@app.post("/api/interview/question")
async def get_question(request: QuestionRequest):
    try:
        user_prompt = f"""
You are an expert interviewer.
Generate ONE interview question for a {request.level} {request.role}.
Return only the question text, no explanation.
"""

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful interview assistant."},
                {"role": "user", "content": user_prompt},
            ],
        )

        question = completion.choices[0].message.content.strip()

        return {"question": question}
    except Exception as error:
        print(f"Error generating question: {error}")
        raise HTTPException(status_code=500, detail="Failed to generate question")

# 2) Route: Evaluate an answer
@app.post("/api/interview/evaluate")
async def evaluate_answer(request: EvaluateRequest):
    try:
        user_prompt = f"""
You are an interviewer.
Role: {request.role}
Level: {request.level}

Interview Question: "{request.question}"
Candidate Answer: "{request.answer}"

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
    except Exception as error:
        print(f"Error evaluating answer: {error}")
        raise HTTPException(status_code=500, detail="Failed to evaluate answer")

# Run with: uvicorn main:app --reload --port 5000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
