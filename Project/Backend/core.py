import pandas as pd
import torch
import numpy as np
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer, util as st_util

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_SAVE_PATH = "./models/flan_t5_interview_finetuned"
 
DATASET_PATH = "Software Questions.csv" # The file in the folder is CSV


def _has_model_weights(path: str) -> bool:
    """Return True only when local checkpoint files are present."""
    if not os.path.isdir(path):
        return False

    files = set(os.listdir(path))
    direct_weights = {
        "model.safetensors",
        "pytorch_model.bin",
        "tf_model.h5",
        "flax_model.msgpack",
    }
    if any(name in files for name in direct_weights):
        return True

    # Handle sharded checkpoints.
    has_safe_index = "model.safetensors.index.json" in files
    has_bin_index = "pytorch_model.bin.index.json" in files
    has_safe_shard = any(name.startswith("model-") and name.endswith(".safetensors") for name in files)
    has_bin_shard = any(name.startswith("pytorch_model-") and name.endswith(".bin") for name in files)
    return (has_safe_index and has_safe_shard) or (has_bin_index and has_bin_shard)

def load_dataset() -> pd.DataFrame:
    """Load and clean the dataset."""
    if os.path.exists("Software Questions.xlsx"):
        df = pd.read_excel("Software Questions.xlsx")
    else:
        df = pd.read_csv("Software Questions.csv", encoding='latin-1')
    
    # Cleaning columns (ensure they match)
    df.columns = [c.strip() for c in df.columns]
    return df

def load_finetuned_model():
    """Load fine-tuned model. Falls back to base flan-t5 if not found."""
    fallback = "google/flan-t5-base"

    if _has_model_weights(MODEL_SAVE_PATH):
        print(f"Loading fine-tuned model from: {MODEL_SAVE_PATH}")
        primary_path = MODEL_SAVE_PATH
    else:
        print(
            f"Fine-tuned model folder exists but has no model weights at '{MODEL_SAVE_PATH}'. "
            f"Using '{fallback}' as fallback."
        )
        primary_path = fallback

    # Try primary first; if local files are incomplete/corrupt, fail over gracefully.
    try:
        tokenizer = AutoTokenizer.from_pretrained(primary_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(
            primary_path,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
        ).to(DEVICE)
    except OSError as e:
        if primary_path != fallback:
            print(f"Failed to load local checkpoint ({e}). Falling back to '{fallback}'.")
            tokenizer = AutoTokenizer.from_pretrained(fallback)
            model = AutoModelForSeq2SeqLM.from_pretrained(
                fallback,
                torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
            ).to(DEVICE)
        else:
            raise

    model.eval()
    return tokenizer, model

def load_semantic_model(df: pd.DataFrame):
    """Load SentenceTransformer + pre-compute dataset answer embeddings."""
    sem_model = SentenceTransformer('all-MiniLM-L6-v2')
    # Pre-compute embeddings for ALL dataset answers
    dataset_embeddings = sem_model.encode(
        df['Answer'].tolist(),
        convert_to_tensor=True
    )
    return sem_model, dataset_embeddings

def get_questions(df, category="Mixed", difficulty="Mixed", num_questions=5) -> list[dict]:
    """Return filtered & shuffled list of question dicts."""
    pool = df.copy()
    if category != "Mixed":
        pool = pool[pool['Category'].str.lower() == category.lower()]
    if difficulty != "Mixed":
        pool = pool[pool['Difficulty'].str.lower() == difficulty.lower()]
    
    if len(pool) == 0:
        return []

    sample_size = min(num_questions, len(pool))
    questions = pool.sample(sample_size).to_dict('records')
    return questions

def generate_model_answer(question, category, difficulty, tokenizer, model) -> str:
    """Generate reference answer using fine-tuned model."""
    prompt = (
        f"Answer this software engineering interview question concisely. "
        f"Category: {category}. "
        f"Difficulty: {difficulty}. "
        f"Question: {question}"
    )
    inputs = tokenizer(
        prompt,
        return_tensors='pt',
        max_length=192,
        truncation=True
    ).to(DEVICE)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,
            length_penalty=1.0
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def evaluate_answer(question, user_answer, correct_answer, category, difficulty,
                    tokenizer, ft_model, sem_model, dataset_embeddings, df) -> dict:
    """
    Evaluate user answer. Returns dict with scores and feedback.
    Scoring: 60% sem_vs_dataset + 25% sem_vs_model + 15% length
    """
    # Generate model's reference answer
    model_ref_answer = generate_model_answer(question, category, difficulty, tokenizer, ft_model)

    # Encode user answer and reference answers
    emb_user    = sem_model.encode(user_answer,       convert_to_tensor=True)
    emb_correct = sem_model.encode(correct_answer,    convert_to_tensor=True) # Could use pre-computed if we knew the index
    emb_model   = sem_model.encode(model_ref_answer,  convert_to_tensor=True)

    # Cosine similarity
    sem_vs_dataset = float(st_util.cos_sim(emb_correct, emb_user)[0][0])
    sem_vs_model   = float(st_util.cos_sim(emb_model,   emb_user)[0][0])

    # Length score
    user_word_count    = len(user_answer.split())
    expected_min_words = 8
    expected_good_words = 15
    len_score = min(max((user_word_count - expected_min_words) /
                        (expected_good_words - expected_min_words), 0.0), 1.0)

    # Combined score (Formula from prompt/notebook)
    combined    = (0.60 * sem_vs_dataset +
                   0.25 * sem_vs_model   +
                   0.15 * len_score)
    
    final_score = round(min(max(combined * 10, 0.0), 10.0), 1)

    # Verdict and Feedback (Derived from notebook but simplified for the Dict return)
    if final_score >= 7.5:   verdict = "Excellent!"
    elif final_score >= 6.0: verdict = "Good"
    elif final_score >= 4.5: verdict = "Needs Improvement"
    else:                    verdict = "Incorrect / Incomplete"

    feedback_parts = []
    if sem_vs_dataset >= 0.72:
        feedback_parts.append("Your answer captures the correct meaning very well.")
    elif sem_vs_dataset >= 0.55:
        feedback_parts.append("You understand the concept but could be more precise.")
    elif sem_vs_dataset >= 0.38:
        feedback_parts.append("Partial understanding. missing core ideas.")
    else:
        feedback_parts.append("Your answer doesn't align with the expected concept.")

    if user_word_count < expected_min_words:
        feedback_parts.append(f"Answer is too brief ({user_word_count} words). Aim for at least 15 words.")

    return {
        "score":            final_score,
        "verdict":          verdict,
        "sem_vs_dataset":   round(sem_vs_dataset, 3),
        "sem_vs_model":     round(sem_vs_model,   3),
        "length_score":     round(len_score,       3),
        "word_count":       user_word_count,
        "feedback":         " ".join(feedback_parts),
        "model_ref_answer": model_ref_answer,
        "correct_answer":   correct_answer
    }
