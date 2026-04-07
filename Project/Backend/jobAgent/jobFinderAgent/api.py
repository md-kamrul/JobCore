from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from dotenv import load_dotenv
from jobAgent import run_job_search
from conversationalAgent import handle_conversation
from applyUrlAgents import agent_a_extract_apply_url, agent_b_format_apply_url_message

# Allow importing sibling agent packages (jobApplyAgent)
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jobApplyAgent.google_form_apply import is_google_form_url, resolve_final_url
from jobApplyAgent.interactive_google_form import (
    answer_current_and_advance,
    next_prompt,
    start_interactive_session,
)
from jobApplyAgent.state import create_session, delete_session, get_session, update_session_answers

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Job Agent API is running"})

@app.route('/api/search-jobs', methods=['POST'])
def search_jobs():
    """Search for jobs based on user query."""
    try:
        data = request.json
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                "error": "Query is required"
            }), 400
        
        logger.info(f"Received job search query: {user_query}")
        
        # Run the async job search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_job_search(None, user_query, None))
            logger.info("Job search completed successfully")
            
            return jsonify({
                "success": True,
                "result": result,
                "query": user_query
            })
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Error processing job search: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An error occurred while searching for jobs. Please try again."
        }), 500


@app.route('/api/extract-apply-url', methods=['POST'])
def extract_apply_url():
    """Extract an external apply URL from a job details page."""
    try:
        data = request.json or {}
        details_url = (data.get('detailsUrl') or data.get('url') or '').strip()

        if not details_url:
            return jsonify({
                "success": False,
                "error": "detailsUrl is required"
            }), 400

        logger.info(f"Extracting apply URL from: {details_url}")
        result = agent_a_extract_apply_url(details_url)
        message = agent_b_format_apply_url_message(result)

        return jsonify({
            "success": True,
            "detailsUrl": result.details_url,
            "applyUrl": result.apply_url,
            "found": result.found,
            "reason": result.reason,
            "message": message,
            "isGoogleForm": bool(result.apply_url and is_google_form_url(resolve_final_url(result.apply_url))),
        })

    except Exception as e:
        logger.error(f"Error extracting apply url: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An error occurred while extracting the apply link. Please try again."
        }), 500


@app.route('/api/apply/start', methods=['POST'])
def start_apply():
    """Agent-B: Auto-apply flow. If applyUrl is a Google Form, try to fill and submit via Selenium.

    Request JSON:
      - applyUrl: string
      - profile: object (best-effort)
      - headless: bool (optional, default true)

    Response JSON:
      - message: chat bubble text
      - status: submitted|needs_info|error
      - applicationId: present when needs_info
      - missing: list when needs_info
    """

    try:
        data = request.json or {}
        apply_url = (data.get('applyUrl') or data.get('url') or '').strip()
        profile = data.get('profile') or {}
        headless = bool(data.get('headless', True))

        if not apply_url:
            return jsonify({
                'success': False,
                'message': 'applyUrl is required'
            }), 400

        final_url = resolve_final_url(apply_url)
        if not is_google_form_url(final_url):
            return jsonify({
                'success': True,
                'status': 'error',
                'applyUrl': final_url,
                'message': '⚠️ This apply link is not a Google Form. Please open it and apply manually.'
            })

        session = create_session(apply_url=final_url, profile=profile)
        init = start_interactive_session(final_url, headless=headless)
        if not init.get('ok'):
            delete_session(session.application_id)
            return jsonify({
                'success': True,
                'status': 'error',
                'applyUrl': final_url,
                'message': f"⚠️ {init.get('message') or 'Auto-apply could not start.'}",
            })

        session.driver = init['driver']
        session.wait = init['wait']
        session.questions = init['questions']
        session.index = init.get('index', 0)

        q, prompt = next_prompt(session.questions, session.index)
        missing = []
        if q:
            missing = [{
                'label': q.label,
                'required': q.required,
                'input_type': q.input_type,
                'options': q.options,
            }]

        return jsonify({
            'success': True,
            'message': prompt or "",
            'status': 'needs_info',
            'applicationId': session.application_id,
            'applyUrl': final_url,
            'missing': missing,
        })

    except Exception as e:
        logger.error(f"Error in apply start: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Auto-apply failed: {str(e)}"
        }), 500


@app.route('/api/apply/continue', methods=['POST'])
def continue_apply():
    """Continue an auto-apply session with user-provided missing info."""
    try:
        data = request.json or {}
        application_id = (data.get('applicationId') or '').strip()
        answers = data.get('answers') or {}
        headless = bool(data.get('headless', True))

        if not application_id:
            return jsonify({
                'success': False,
                'message': 'applicationId is required'
            }), 400

        session = update_session_answers(application_id, answers)
        if not session:
            return jsonify({
                'success': False,
                'message': 'Unknown or expired application session. Please click Apply again.'
            }), 404

        if not session.driver or not session.wait or not session.questions:
            delete_session(application_id)
            return jsonify({
                'success': True,
                'status': 'error',
                'message': '⚠️ Application session is not active anymore. Please click Apply again.',
                'applyUrl': session.apply_url,
            })

        # Determine the current question label and grab the user answer
        current_q, _ = next_prompt(session.questions, session.index)
        if not current_q:
            delete_session(application_id)
            return jsonify({
                'success': True,
                'status': 'error',
                'message': '⚠️ No pending question found. Please click Apply again.',
                'applyUrl': session.apply_url,
            })

        user_answer = answers.get(current_q.label) or answers.get('default') or ''
        user_answer = str(user_answer).strip()
        if not user_answer:
            # re-ask
            _, prompt = next_prompt(session.questions, session.index)
            return jsonify({
                'success': True,
                'status': 'needs_info',
                'message': prompt,
                'applicationId': session.application_id,
                'missing': [{
                    'label': current_q.label,
                    'required': current_q.required,
                    'input_type': current_q.input_type,
                    'options': current_q.options,
                }],
                'applyUrl': session.apply_url,
            })

        step = answer_current_and_advance(
            driver=session.driver,
            wait=session.wait,
            questions=session.questions,
            index=session.index,
            answer=user_answer,
        )

        status = step.get('status')
        if status == 'submitted':
            delete_session(application_id)
            return jsonify({
                'success': True,
                'status': 'submitted',
                'message': step.get('message') or '✅ Submitted the form.',
                'applyUrl': session.apply_url,
            })

        if status == 'needs_info':
            # Update session state (either advanced on same page or moved to new page)
            session.index = int(step.get('index', session.index))
            if step.get('questions') is not None:
                session.questions = step.get('questions')
            q, prompt = next_prompt(session.questions, session.index)
            missing = []
            if q:
                missing = [{
                    'label': q.label,
                    'required': q.required,
                    'input_type': q.input_type,
                    'options': q.options,
                }]
            return jsonify({
                'success': True,
                'status': 'needs_info',
                'message': prompt,
                'applicationId': session.application_id,
                'missing': missing,
                'applyUrl': session.apply_url,
            })

        # error
        delete_session(application_id)
        return jsonify({
            'success': True,
            'status': 'error',
            'message': f"⚠️ {step.get('message') or 'Auto-apply could not complete.'}",
            'applyUrl': session.apply_url,
        })

    except Exception as e:
        logger.error(f"Error in apply continue: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f"Auto-apply failed: {str(e)}"
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint that intelligently routes between conversation and job search."""
    try:
        data = request.json
        message = data.get('message', '').strip()
        conversation_history = data.get('history', [])  # Optional conversation context
        
        if not message:
            return jsonify({
                "error": "Message is required"
            }), 400
        
        logger.info(f"Received chat message: {message}")
        
        # Use conversational agent to determine intent and respond
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Analyze conversation and determine next action
            conversation_result = loop.run_until_complete(
                handle_conversation(message, conversation_history)
            )
            
            if conversation_result["should_search"]:
                # User wants to search for jobs
                logger.info(f"Routing to job search agent: {conversation_result['reasoning']}")
                
                job_results = loop.run_until_complete(run_job_search(None, message, None))
                
                return jsonify({
                    "success": True,
                    "type": "job_results",
                    "message": job_results,
                    "is_search": True
                })
            else:
                # General conversation
                logger.info(f"Responding conversationally: {conversation_result['reasoning']}")
                
                return jsonify({
                    "success": True,
                    "type": "conversation",
                    "message": conversation_result["response"],
                    "is_search": False
                })
                
        finally:
            loop.close()
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An error occurred. Please try again."
        }), 500

if __name__ == '__main__':
    import os
    
    # Check API key
    if not os.getenv("NEBIUS_API_KEY"):
        logger.error("NEBIUS_API_KEY not found in .env file")
        print("❌ ERROR: NEBIUS_API_KEY not found in .env file")
        exit(1)
    
    logger.info("✅ API Key loaded successfully")
    logger.info("🚀 Starting Job Agent API Server...")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
