"""
Conversational Agent - Handles general chat and routes to job search agent when needed
"""

from openai import AsyncOpenAI
import os
import logging

logger = logging.getLogger(__name__)

# Client will be initialized lazily
_client = None

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
            intent_data = json.loads(result)
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
    
    # Analyze user intent
    intent = await analyze_user_intent(user_message)
    
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
