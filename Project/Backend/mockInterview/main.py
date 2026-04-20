from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
import json
import uuid
import time
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / ".env.local"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="JobCore AI Mock Interview API",
    version="2.0.0"
)

PORT = int(os.getenv("PORT", 5002))
MODEL_API_URL = os.getenv("MODEL_API_URL", "http://localhost:5000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory session storage ────────────────────────────────────
sessions = {}

# ── Available options ────────────────────────────────────────────
ROLES = [
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Data Scientist",
    "Data Analyst",
    "Product Manager",
    "DevOps Engineer",
    "Mobile App Developer",
    "UI/UX Designer",
    "QA/Test Engineer",
]

TOPICS = {
    "Software Engineer": ["Python", "DSA", "OOP", "System Design", "Git", "Databases", "Behavioral", "HR", "Situational"],
    "Frontend Developer": ["JavaScript", "React", "CSS", "TypeScript", "Performance", "Behavioral", "HR", "Situational"],
    "Backend Developer": ["APIs", "Databases", "Authentication", "Caching", "Microservices", "System Design", "Behavioral", "HR", "Situational"],
    "Data Scientist": ["Machine Learning", "Statistics", "Deep Learning", "NLP", "Feature Engineering", "Behavioral", "HR", "Situational"],
    "Data Analyst": ["SQL", "Python", "Excel", "Visualization", "Statistics", "Behavioral", "HR", "Situational"],
    "Product Manager": ["Product Thinking", "Metrics", "Prioritization", "Strategy", "Behavioral", "HR", "Situational"],
    "DevOps Engineer": ["CI/CD", "Docker", "Kubernetes", "Cloud", "Monitoring", "Security", "Behavioral", "HR", "Situational"],
    "Mobile App Developer": ["Mobile Development", "Architecture", "Storage", "Performance", "Behavioral", "HR", "Situational"],
    "UI/UX Designer": ["Design Principles", "User Research", "Design Systems", "Design Process", "Behavioral", "HR", "Situational"],
    "QA/Test Engineer": ["Testing", "API Testing", "Performance Testing", "Automation", "Behavioral", "HR", "Situational"],
}

DIFFICULTIES = ["Easy", "Medium", "Hard"]

LEVEL_MAP = {
    "junior": "Easy",
    "mid-level": "Medium",
    "senior": "Hard",
    "easy": "Easy",
    "medium": "Medium",
    "hard": "Hard",
}


# ── Request / Response models ────────────────────────────────────

class StartRequest(BaseModel):
    role: str
    topic: Optional[str] = "Technical"
    difficulty: Optional[str] = "Medium"
    num_questions: Optional[int] = 5

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

class QuickQuestionRequest(BaseModel):
    role: str
    level: str

class QuickEvaluateRequest(BaseModel):
    role: str
    level: str
    question: str
    answer: str


# ── Helper functions ─────────────────────────────────────────────

def map_difficulty(level: str) -> str:
    return LEVEL_MAP.get(level.lower().strip(), "Medium")


def call_model_generate(role: str, topic: str, difficulty: str) -> dict:
    try:
        r = requests.post(
            f"{MODEL_API_URL}/generate",
            json={"role": role, "topic": topic, "difficulty": difficulty},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Model error (generate): {e}")
    return {"question": f"Tell me about your experience as a {role}.", "expected_skills": []}


def call_model_evaluate(role: str, topic: str, difficulty: str, question: str, answer: str) -> dict:
    try:
        r = requests.post(
            f"{MODEL_API_URL}/evaluate",
            json={"role": role, "topic": topic, "difficulty": difficulty, "question": question, "answer": answer},
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Model error (evaluate): {e}")
    return {
        "scores": {"clarity": 5, "correctness": 5, "relevance": 5, "depth": 5},
        "overall": 5,
        "feedback": "Could not reach the AI model. Please try again.",
        "improved_answer": "",
    }


# ── Endpoints: Quick mode (compatible with old frontend) ─────────

@app.get("/")
async def root():
    return {"message": "JobCore AI Mock Interview API v2.0", "model": "Qwen2.5-7B Fine-Tuned"}


@app.get("/health")
async def health():
    try:
        r = requests.get(f"{MODEL_API_URL}/health", timeout=5)
        model_ok = r.status_code == 200
    except:
        model_ok = False
    return {"api": "running", "model_server": "connected" if model_ok else "disconnected"}


@app.get("/options")
async def get_options():
    return {"roles": ROLES, "topics": TOPICS, "difficulties": DIFFICULTIES}


@app.post("/api/interview/question")
async def quick_question(request: QuickQuestionRequest):
    difficulty = map_difficulty(request.level)
    result = call_model_generate(request.role, "Technical", difficulty)
    return {"question": result.get("question", ""), "expected_skills": result.get("expected_skills", [])}


@app.post("/api/interview/evaluate")
async def quick_evaluate(request: QuickEvaluateRequest):
    difficulty = map_difficulty(request.level)
    result = call_model_evaluate(request.role, "Technical", difficulty, request.question, request.answer)

    scores = result.get("scores", {})
    overall = result.get("overall", 0)
    feedback = result.get("feedback", "")
    improved = result.get("improved_answer", "")

    evaluation = f"Score: {overall}/10\n\n"
    evaluation += f"Clarity: {scores.get('clarity', 0)}/10 | "
    evaluation += f"Correctness: {scores.get('correctness', 0)}/10 | "
    evaluation += f"Relevance: {scores.get('relevance', 0)}/10 | "
    evaluation += f"Depth: {scores.get('depth', 0)}/10\n\n"
    evaluation += f"Feedback: {feedback}\n\n"
    if improved:
        evaluation += f"Stronger answer: {improved}"

    return {"evaluation": evaluation, "scores": scores, "overall": overall}


# ── Endpoints: Session mode (for full interview flow) ────────────

@app.post("/api/interview/start")
async def start_interview(request: StartRequest):
    difficulty = map_difficulty(request.difficulty)

    session = {
        "id": str(uuid.uuid4()),
        "role": request.role,
        "topic": request.topic,
        "difficulty": difficulty,
        "num_questions": request.num_questions,
        "current_q": 1,
        "results": [],
        "status": "active",
        "started_at": time.time(),
    }

    result = call_model_generate(session["role"], session["topic"], session["difficulty"])
    session["current_question"] = result.get("question", "Tell me about yourself.")
    session["expected_skills"] = result.get("expected_skills", [])

    sessions[session["id"]] = session

    return {
        "session_id": session["id"],
        "question_number": 1,
        "total_questions": session["num_questions"],
        "question": session["current_question"],
        "expected_skills": session["expected_skills"],
        "difficulty": session["difficulty"],
    }


@app.post("/api/interview/answer")
async def submit_answer(request: AnswerRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Interview already completed")

    evaluation = call_model_evaluate(
        session["role"], session["topic"], session["difficulty"],
        session["current_question"], request.answer,
    )

    session["results"].append({
        "question_number": session["current_q"],
        "question": session["current_question"],
        "answer": request.answer,
        "scores": evaluation.get("scores", {}),
        "overall": evaluation.get("overall", 0),
        "feedback": evaluation.get("feedback", ""),
        "improved_answer": evaluation.get("improved_answer", ""),
    })

    # Adaptive difficulty
    score = evaluation.get("overall", 5)
    if score >= 8 and session["difficulty"] != "Hard":
        session["difficulty"] = {"Easy": "Medium", "Medium": "Hard"}[session["difficulty"]]
    elif score <= 4 and session["difficulty"] != "Easy":
        session["difficulty"] = {"Hard": "Medium", "Medium": "Easy"}[session["difficulty"]]

    # Check if done
    if session["current_q"] >= session["num_questions"]:
        session["status"] = "completed"
        return {
            "status": "completed",
            "question_number": session["current_q"],
            "evaluation": evaluation,
        }

    # Next question
    next_result = call_model_generate(session["role"], session["topic"], session["difficulty"])
    session["current_question"] = next_result.get("question", "Tell me more.")
    session["expected_skills"] = next_result.get("expected_skills", [])
    session["current_q"] += 1

    return {
        "status": "active",
        "question_number": session["current_q"],
        "total_questions": session["num_questions"],
        "evaluation": evaluation,
        "next_question": session["current_question"],
        "expected_skills": session["expected_skills"],
        "difficulty": session["difficulty"],
    }


@app.get("/api/interview/summary/{session_id}")
async def get_summary(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    results = session["results"]
    if not results:
        return {"session_id": session_id, "status": session["status"], "results": []}

    all_overall = [r["overall"] for r in results if r["overall"] > 0]
    avg_overall = round(sum(all_overall) / len(all_overall), 1) if all_overall else 0

    avg_scores = {}
    for key in ["clarity", "correctness", "relevance", "depth"]:
        vals = [r["scores"].get(key, 0) for r in results if r["scores"].get(key, 0) > 0]
        avg_scores[key] = round(sum(vals) / len(vals), 1) if vals else 0

    strongest = max(avg_scores, key=avg_scores.get) if avg_scores else ""
    weakest = min(avg_scores, key=avg_scores.get) if avg_scores else ""

    return {
        "session_id": session_id,
        "status": session["status"],
        "role": session["role"],
        "topic": session["topic"],
        "questions_answered": len(results),
        "average_overall": avg_overall,
        "average_scores": avg_scores,
        "strongest_area": strongest,
        "weakest_area": weakest,
        "results": results,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
