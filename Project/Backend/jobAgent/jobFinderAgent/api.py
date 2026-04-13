from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from dotenv import load_dotenv
from jobAgent import run_job_search
from conversationalAgent import handle_conversation
from applyUrlAgents import agent_a_extract_apply_url, agent_b_format_apply_url_message
from selenium.webdriver.support.ui import WebDriverWait

# Allow importing sibling agent packages (jobApplyAgent)
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jobApplyAgent.google_form_apply import is_google_form_url, resolve_final_url
from jobApplyAgent.interactive_google_form import (
    answer_current_and_advance,
    is_gmail_logged_in,
    load_form_after_login,
    next_prompt,
    start_gmail_login_session,
    start_interactive_session,
)
from jobApplyAgent.profile_resolver import normalize_profile, resolve_answer
from jobApplyAgent.state import create_session, delete_session, get_session, update_session_answers

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication


def _build_missing_payload(session, *, question, prompt):
    missing = []
    if question:
        missing = [{
            'label': question.label,
            'required': question.required,
            'input_type': question.input_type,
            'options': question.options,
        }]
    return {
        'success': True,
        'status': 'needs_info',
        'message': prompt,
        'applicationId': session.application_id,
        'missing': missing,
        'applyUrl': session.apply_url,
    }


def _build_confirm_payload(session, *, question, prompt, suggested_answer: str):
    missing = []
    if question:
        missing = [{
            'label': question.label,
            'required': question.required,
            'input_type': question.input_type,
            'options': question.options,
        }]
    msg = prompt or ""
    if suggested_answer:
        msg = (
            f"{msg}\n\nI found a possible answer in your profile."
            "\nConfirm to use it or click Edit to provide a different answer."
        ).strip()
    return {
        'success': True,
        'status': 'needs_confirm',
        'message': msg,
        'applicationId': session.application_id,
        'missing': missing,
        'suggestedAnswer': suggested_answer,
        'applyUrl': session.apply_url,
    }


def _auto_answer_or_prompt(session):
    profile = normalize_profile(session.profile)

    current_q, prompt = next_prompt(session.questions, session.index)
    if not current_q:
        delete_session(session.application_id)
        return {
            'success': True,
            'status': 'error',
            'message': '⚠️ No pending question found. Please click Apply again.',
            'applyUrl': session.apply_url,
        }

    auto_answer = resolve_answer(current_q.label, profile, session.answers)
    if (current_q.input_type or '').lower() == 'file' and not auto_answer:
        auto_answer = profile.get('resume_path')

    if auto_answer:
        return _build_confirm_payload(
            session,
            question=current_q,
            prompt=prompt,
            suggested_answer=str(auto_answer),
        )

    return _build_missing_payload(session, question=current_q, prompt=prompt)

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


@app.route('/api/apply/gmail-login', methods=['POST'])
def start_gmail_login():
    """Open a visible real Chrome browser to Gmail login. Returns applicationId for polling."""
    try:
        data = request.json or {}
        apply_url = (data.get('applyUrl') or '').strip()
        profile = data.get('profile') or {}

        if not apply_url:
            return jsonify({'success': False, 'message': 'applyUrl is required'}), 400

        final_url = resolve_final_url(apply_url)
        session = create_session(apply_url=final_url, profile=profile)

        init = start_gmail_login_session(final_url, headless=False)
        if not init.get('ok'):
            delete_session(session.application_id)
            return jsonify({'success': False,
                            'message': init.get('message', 'Failed to open Gmail login')})

        session.driver = init['driver']
        session.wait   = init['wait']
        # Store port so polling can reconnect if the CDP session drops
        session.debug_port = init.get('debug_port', 0)

        return jsonify({
            'success': True,
            'status': 'awaiting_login',
            'applicationId': session.application_id,
            'message': 'A browser window has opened. Please log in with your Gmail account to continue.',
        })
    except Exception as e:
        logger.error(f"Error starting gmail login: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Failed to open Gmail login: {str(e)}'}), 500


@app.route('/api/apply/gmail-login/status', methods=['GET'])
def gmail_login_status():
    """
    Poll for Gmail login completion.
    Handles CDP session drops by reconnecting to the real Chrome process.
    On success, navigates to the form and returns the first question.
    """
    application_id = request.args.get('applicationId', '').strip()
    if not application_id:
        return jsonify({'success': False, 'message': 'applicationId is required'}), 400

    session = get_session(application_id)
    if not session or not session.driver:
        return jsonify({'success': False, 'message': 'Session not found or expired.'}), 404

    try:
        # is_gmail_logged_in now returns (bool, driver) — driver may be a fresh reconnection
        logged_in, fresh_driver = is_gmail_logged_in(
            session.driver, debug_port=session.debug_port
        )

        # Always save the (possibly reconnected) driver back onto the session
        if fresh_driver is not session.driver:
            session.driver = fresh_driver
            session.wait   = WebDriverWait(fresh_driver, 25)

        if not logged_in:
            return jsonify({'success': True, 'status': 'awaiting_login',
                            'applicationId': application_id})

        # Login confirmed — navigate to the form and scan questions
        result = load_form_after_login(
            session.driver, session.wait, session.apply_url
        )
        if not result.get('ok'):
            delete_session(application_id)
            return jsonify({'success': True, 'status': 'error',
                            'message': f"⚠️ {result.get('message', 'Could not load form after login.')}"})

        session.questions = result['questions']
        session.index     = result.get('index', 0)

        return jsonify(_auto_answer_or_prompt(session))

    except Exception as e:
        logger.error(f"Error checking gmail login status: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


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

        return jsonify(_auto_answer_or_prompt(session))

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

        user_answer_raw = answers.get(current_q.label)
        if user_answer_raw is None:
            user_answer_raw = answers.get('default')

        # Checkbox answers may arrive as a list (multi-select). Convert to the comma-separated
        # format expected by the Google Forms filler.
        if isinstance(user_answer_raw, (list, tuple, set)):
            user_answer = ", ".join([str(v).strip() for v in user_answer_raw if str(v).strip()])
        else:
            user_answer = str(user_answer_raw or "").strip()
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
            return jsonify(_auto_answer_or_prompt(session))

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
