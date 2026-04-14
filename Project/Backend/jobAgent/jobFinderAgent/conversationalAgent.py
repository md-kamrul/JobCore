"""
Conversational Agent - Handles general chat and routes to job search agent when needed
"""

from openai import AsyncOpenAI
import os
import logging
import re

logger = logging.getLogger(__name__)

# Client will be initialized lazily
_client = None


SEARCH_ACTION_TERMS = {
    "find", "search", "looking", "look", "need", "want", "show", "get", "seek", "seeking"
}

JOB_ENTITY_TERMS = {
    "job", "jobs", "position", "positions", "role", "roles", "opening", "openings",
    "opportunity", "opportunities", "vacancy", "vacancies", "internship", "internships"
}


def _normalize_bool(value) -> bool:
    """Normalize bool-like model outputs (true/false, yes/no, 1/0) to a Python bool."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "yes", "1", "job_search", "search"}:
            return True
        if v in {"false", "no", "0", "conversation", "chat"}:
            return False
    return False


def _normalize_confidence(value, default: float = 0.5) -> float:
    """Parse and clamp confidence to [0.0, 1.0]."""
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, conf))


def detect_job_search_intent(user_message: str) -> dict:
    """
    Deterministic intent detector for explicit job-search phrasing.
    Returns a dict compatible with analyze_user_intent output.
    """
    text = (user_message or "").strip().lower()
    if not text:
        return {
            "is_job_search": False,
            "confidence": 0.0,
            "reasoning": "Empty message"
        }

    has_action = any(re.search(rf"\b{re.escape(term)}\b", text) for term in SEARCH_ACTION_TERMS)
    has_job_entity = any(re.search(rf"\b{re.escape(term)}\b", text) for term in JOB_ENTITY_TERMS)

    # Strong patterns like "jobs in bangladesh", "find mern jobs", "looking for internship"
    strong_patterns = [
        r"\b(find|search|look(?:ing)?\s*for|show\s*me|get\s*me|need|want|seeking?)\b.*\b(job|jobs|position|positions|role|roles|opening|openings|opportunit(?:y|ies)|vacanc(?:y|ies)|internship|internships)\b",
        r"\b(job|jobs|position|positions|role|roles|opening|openings|opportunit(?:y|ies)|vacanc(?:y|ies)|internship|internships)\b\s+(in|at|for|near|around|remote|from)\b",
        r"\b(mern|frontend|front\s*end|backend|full\s*stack|react|node|django|python|java|developer|engineer|designer|data\s+scientist)\b.*\b(job|jobs|internship|internships|position|positions|role|roles)\b",
    ]

    matches_strong_pattern = any(re.search(pattern, text) for pattern in strong_patterns)

    is_job_search = matches_strong_pattern or (has_action and has_job_entity)
    confidence = 0.95 if matches_strong_pattern else (0.85 if is_job_search else 0.15)
    reasoning = "Deterministic keyword/pattern intent detection"

    return {
        "is_job_search": is_job_search,
        "confidence": confidence,
        "reasoning": reasoning
    }

def get_client():
    """Get or initialize the OpenAI client"""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url="https://api.tokenfactory.nebius.com/v1",
            api_key=os.getenv("NEBIUS_API_KEY"),
        )
    return _client

async def analyze_user_intent(user_message: str) -> dict:
    """
    Analyze user message to determine if it's a job search request or general conversation.
    Returns: {
        "is_job_search": bool,
        "confidence": float,
        "reasoning": str
    }
    """
    
    system_prompt = """You are an intent analyzer for a job search assistant. 
Your task is to determine if the user's message is requesting a job search or just having a conversation.

Job search indicators:
- Keywords like: find, search, looking for, need, want, show me, jobs, position, role, career, opportunity
- Mentions of job titles, industries, locations, or employment types
- Questions about job availability or requirements

General conversation indicators:
- Greetings (hi, hello, how are you)
- General questions about the service
- Casual conversation
- Clarifications or follow-up questions

Respond ONLY with a JSON object in this exact format:
{
  "is_job_search": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}"""

    try:
        client = get_client()
        response = await client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-fast",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this message: '{user_message}'"}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse JSON response
        import json
        try:
            raw_intent_data = json.loads(result)
            intent_data = {
                "is_job_search": _normalize_bool(raw_intent_data.get("is_job_search")),
                "confidence": _normalize_confidence(raw_intent_data.get("confidence"), default=0.5),
                "reasoning": str(raw_intent_data.get("reasoning", "LLM intent analysis")).strip() or "LLM intent analysis"
            }
            logger.info(f"Intent analysis: {intent_data}")
            return intent_data
        except json.JSONDecodeError:
            # Fallback: check for job-related keywords
            job_keywords = ['find', 'search', 'looking', 'job', 'position', 'role', 'career', 
                          'opportunity', 'hiring', 'vacancy', 'work', 'employment']
            is_job_search = any(keyword in user_message.lower() for keyword in job_keywords)
            return {
                "is_job_search": is_job_search,
                "confidence": 0.7 if is_job_search else 0.3,
                "reasoning": "Keyword-based fallback analysis"
            }
            
    except Exception as e:
        logger.error(f"Error analyzing intent: {str(e)}")
        # Fallback to keyword detection
        job_keywords = ['find', 'search', 'looking', 'job', 'position', 'role', 'career']
        is_job_search = any(keyword in user_message.lower() for keyword in job_keywords)
        return {
            "is_job_search": is_job_search,
            "confidence": 0.5,
            "reasoning": "Fallback due to API error"
        }


async def generate_conversational_response(user_message: str, conversation_history: list = None) -> str:
    """
    Generate a conversational response for general chat (non-job-search queries).
    """
    
    system_prompt = """You are JobCore AI, a friendly and helpful job search assistant. 
You help users find jobs and answer questions about job searching, career advice, and the job market.

Your capabilities:
- Search for jobs based on user criteria (role, location, experience level, etc.)
- Provide career advice and job search tips
- Answer questions about job applications, resumes, and interviews
- Offer encouragement and support in job hunting

Be conversational, friendly, and helpful. Keep responses concise (2-4 sentences).
If the user seems to want to search for jobs, encourage them to provide details like:
- Job title or role they're interested in
- Preferred location (or remote work)
- Experience level
- Any specific requirements

Remember: You are an AI assistant focused on helping people find their ideal jobs."""

    try:
        client = get_client()
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Keep last 6 messages for context
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        response = await client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-fast",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content.strip()
        logger.info(f"Generated conversational response: {ai_response[:100]}...")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error generating conversational response: {str(e)}")
        return ("I'm here to help you find jobs! Tell me what kind of position you're looking for, "
                "and I'll search for the best opportunities for you. You can mention the job title, "
                "location, or any specific requirements you have.")


async def handle_conversation(user_message: str, conversation_history: list = None) -> dict:
    """
    Main conversation handler that routes to job search or general chat.
    
    Returns: {
        "type": "conversation" | "job_search",
        "response": str,
        "should_search": bool
    }
    """
    
    # Fast deterministic guard for explicit job-search queries.
    deterministic_intent = detect_job_search_intent(user_message)
    if deterministic_intent["is_job_search"] and deterministic_intent["confidence"] >= 0.8:
        logger.info(
            "Routing to job search agent - Deterministic detector (%s)",
            deterministic_intent["reasoning"]
        )
        return {
            "type": "job_search",
            "response": None,
            "should_search": True,
            "reasoning": deterministic_intent["reasoning"]
        }

    # Analyze user intent with LLM for less explicit/ambiguous messages.
    intent = await analyze_user_intent(user_message)

    # Safety override: if LLM misses obvious search phrasing, honor deterministic detector.
    if (not intent.get("is_job_search")) and deterministic_intent["is_job_search"]:
        logger.info(
            "Routing to job search agent - Heuristic override after LLM mismatch"
        )
        intent = deterministic_intent
    
    # If confidence is high that it's a job search, return instruction to search
    if intent["is_job_search"] and intent["confidence"] > 0.6:
        logger.info(f"Routing to job search agent - Confidence: {intent['confidence']}")
        return {
            "type": "job_search",
            "response": None,
            "should_search": True,
            "reasoning": intent["reasoning"]
        }
    
    # Otherwise, generate conversational response
    logger.info(f"Handling as conversation - Confidence: {intent['confidence']}")
    response = await generate_conversational_response(user_message, conversation_history)
    
    return {
        "type": "conversation",
        "response": response,
        "should_search": False,
        "reasoning": intent["reasoning"]
    }
