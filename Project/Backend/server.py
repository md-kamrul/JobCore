import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import core  # their core script

app = FastAPI(title="AI Mock Interviewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global memory for dataset and models to mimic Streamlit's caching
dataset = None
tokenizer = None
ft_model = None
sem_model = None
dataset_embeddings = None

@app.on_event("startup")
def startup_event():
    global dataset, tokenizer, ft_model, sem_model, dataset_embeddings
    print("Loading dataset...")
    dataset = core.load_dataset()
    print(f"Dataset loaded. Size: {len(dataset)}")
    
    print("Loading models... (This might take a while)")
    try:
        tokenizer, ft_model = core.load_finetuned_model()
        sem_model, dataset_embeddings = core.load_semantic_model(dataset)
        print("Models loaded successfully.")
    except Exception as e:
        print(f"Warning: Failed to load models: {e}")

class QuestionRequest(BaseModel):
    role: str
    level: str

class EvaluateRequest(BaseModel):
    question: str
    answer: str
    correct_answer: str
    category: str
    difficulty: str

ROLE_MAP = {
    "Frontend Developer": "Front-end",
    "Backend Developer": "Back-end",
    "Full Stack Developer": "Full-stack",
    "AI Engineer": "Artificial Intelligence"
}

LEVEL_MAP = {
    "junior": "Easy",
    "mid-level": "Medium",
    "senior": "Hard"
}

@app.post("/api/interview/question")
def get_question(req: QuestionRequest):
    if dataset is None:
        raise HTTPException(status_code=503, detail="Dataset not loaded")
        
    cat = ROLE_MAP.get(req.role, "Mixed")
    diff = LEVEL_MAP.get(req.level, "Mixed")
    
    qs = core.get_questions(dataset, cat, diff, 1)
    if not qs:
        qs = core.get_questions(dataset, "Mixed", "Mixed", 1)
        if not qs:
            raise HTTPException(status_code=404, detail="No questions found.")
            
    q_data = qs[0]
    return {
        "question": q_data["Question"],
        "questionData": q_data
    }

@app.post("/api/interview/evaluate")
def evaluate_interview_answer(req: EvaluateRequest):
    if ft_model is None or sem_model is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    result = core.evaluate_answer(
        req.question,
        req.answer,
        req.correct_answer,
        req.category,
        req.difficulty,
        tokenizer,
        ft_model,
        sem_model,
        dataset_embeddings,
        dataset
    )
    
    eval_text = f"Verdict: {result['verdict']}\nScore: {result['score']}/10\n\nFeedback: {result['feedback']}\n\nReference Answer: {result['model_ref_answer']}\nDataset Answer: {result['correct_answer']}"
    return {
        "evaluation": eval_text,
        "score": result["score"],
        "verdict": result["verdict"]
    }

@app.get("/api/info")
def get_info():
    return {
        "dataset_size": len(dataset) if dataset is not None else 0,
        "topics": len(dataset['Category'].unique()) if dataset is not None else 0,
        "device": core.DEVICE.upper()
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5002, reload=True)
