from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
import os
import re
import tempfile
import urllib.request
from dotenv import load_dotenv
from jobAgent import run_job_search
from conversationalAgent import handle_conversation
from applyUrlAgents import agent_a_extract_apply_url, agent_b_format_apply_url_message
from selenium.webdriver.support.ui import WebDriverWait

# Allow importing sibling agent packages (jobApplyAgent)
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jobApplyAgent.google_form_apply import (
    is_google_form_url,
    resolve_final_url,
    _auto_check_email_record_permissions,
)
from jobApplyAgent.interactive_google_form import (
    answer_current_and_advance,
    is_gmail_logged_in,
    load_form_after_login,
    next_prompt,
    resume_upload_agent,
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

DEFAULT_RESUME_UPLOAD_PATH = "/Users/kamrul/Downloads/cv.pdf"


# ── CV download helper ────────────────────────────────────────────────────────

def _prepare_cv(profile: dict) -> dict:
    """
    If profile contains a Supabase signed URL (cv_download_url), download the
    file to a system temp directory and set profile['resume_path'] to that
    local path so Selenium can upload it via send_keys().

    Returns the (possibly mutated) profile dict.
    """
    download_url = (profile.get("cv_download_url") or "").strip()
    cv_name      = (profile.get("cv_name") or "").strip()

    if not download_url:
        return profile   # no CV URL supplied — leave resume_path as-is

    # Derive a safe local filename from cv_name
    safe_name = re.sub(r"[^\w.\-]", "_", cv_name) if cv_name else "cv_file"
    ext = os.path.splitext(safe_name)[1] or ".pdf"
    tmp_path = os.path.join(tempfile.gettempdir(), f"jobcore_{safe_name}")

    try:
        logger.info("Downloading CV from Supabase to %s", tmp_path)
        urllib.request.urlretrieve(download_url, tmp_path)
        profile["resume_path"] = tmp_path
        logger.info("CV ready at %s", tmp_path)
    except Exception as exc:
        logger.warning("CV download failed: %s", exc)
        # Don't overwrite any existing resume_path if download fails

    return profile


def _is_dropdown_placeholder_option(text: str) -> bool:
    t = re.sub(r"\s+", " ", str(text or "").strip().lower())
    if not t:
        return True

    if t in {"choose", "choose an option", "select", "select an option", "option", "--"}:
        return True
    if "বাছুন" in t or "নির্বাচন করুন" in t:
        return True

    cleaned = re.sub(r"\(.*?\)", "", t).strip()
    if cleaned in {"choose", "select", "choose option", "select option"}:
        return True

    return False


def _normalize_options(options, *, input_type: str = ""):
    if not isinstance(options, (list, tuple)):
        return []
    out = []
    seen = set()
    for raw in options:
        parts = [p.strip() for p in re.split(r"[\r\n]+", str(raw or "")) if p.strip()]
        if not parts and str(raw or "").strip():
            parts = [str(raw).strip()]
        for part in parts:
            if (input_type or "").lower() == "dropdown" and _is_dropdown_placeholder_option(part):
                continue
            key = re.sub(r"\s+", " ", part).strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(part)
    return out


def _is_email_record_checkbox(question) -> bool:
    if not question:
        return False
    if str(getattr(question, "input_type", "") or "").lower() != "checkbox":
        return False

    label = str(getattr(question, "label", "") or "")
    options = getattr(question, "options", None) or []
    text = re.sub(r"\s+", " ", f"{label} {' '.join([str(o or '') for o in options])}").strip().lower()

    if "record my email" in text or "record email" in text:
        return True
    if "email" in text and any(k in text for k in ("record", "save", "store", "keep")):
        return True
    if "ইমেইল" in text and any(k in text for k in ("রেকর্ড", "সংরক্ষণ", "সেভ", "রাখ")):
        return True
    return False


def _build_missing_payload(session, *, question, prompt):
    missing = []
    if question:
        question.options = _normalize_options(question.options, input_type=question.input_type)
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
        question.options = _normalize_options(question.options, input_type=question.input_type)
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


def _resolve_resume_upload_answer(raw_answer: object) -> str:
    answer = str(raw_answer or "").strip()
    if answer == "1" or not answer:
        return DEFAULT_RESUME_UPLOAD_PATH
    return answer


def _auto_answer_or_prompt(session):
    profile = normalize_profile(session.profile)

    # Pre-task: check Google Form email-record permission checkbox before normal Q&A.
    if session.driver:
        try:
            _auto_check_email_record_permissions(session.driver)
        except Exception:
            pass

    # Auto-check consent-like email-record checkbox before asking any other questions.
    # This keeps the chat flow focused on actual application questions.
    auto_guard = 0
    while auto_guard < 8:
        auto_guard += 1

        current_q, prompt = next_prompt(session.questions, session.index)
        if not current_q:
            delete_session(session.application_id)
            return {
                'success': True,
                'status': 'error',
                'message': '⚠️ No pending question found. Please click Apply again.',
                'applyUrl': session.apply_url,
            }

        if (current_q.input_type or '').lower() == 'file':
            return _build_missing_payload(session, question=current_q, prompt=prompt)

        current_q.options = _normalize_options(current_q.options, input_type=current_q.input_type)

        if _is_email_record_checkbox(current_q):
            # Permission checkbox was handled by the pre-task; skip it in the queue.
            session.index += 1
            continue

        auto_answer = resolve_answer(current_q.label, profile, session.answers, options=current_q.options)

        if auto_answer:
            return _build_confirm_payload(
                session,
                question=current_q,
                prompt=prompt,
                suggested_answer=str(auto_answer),
            )

        return _build_missing_payload(session, question=current_q, prompt=prompt)

    return {
        'success': True,
        'status': 'error',
        'message': '⚠️ Could not advance form automatically. Please click Apply again.',
        'applyUrl': session.apply_url,
    }

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
        profile   = _prepare_cv(profile)          # download CV to local temp file if URL present
        session   = create_session(apply_url=final_url, profile=profile)

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
    On success, navigates to the form and returns the first question.
    The login_completed flag on the session ensures this only fires once
    even if the frontend polls again before it stops.
    """
    application_id = request.args.get('applicationId', '').strip()
    if not application_id:
        return jsonify({'success': False, 'message': 'applicationId is required'}), 400

    session = get_session(application_id)
    if not session or not session.driver:
        return jsonify({'success': False, 'message': 'Session not found or expired.'}), 404

    # ── Guard: already processed — return awaiting_login so the frontend
    # ignores any in-flight poll that arrives after the first success. ──────
    if session.login_completed:
        return jsonify({'success': True, 'status': 'awaiting_login',
                        'applicationId': application_id})

    try:
        logged_in, fresh_driver = is_gmail_logged_in(
            session.driver, debug_port=session.debug_port
        )

        if fresh_driver is not session.driver:
            session.driver = fresh_driver
            session.wait   = WebDriverWait(fresh_driver, 25)

        if not logged_in:
            return jsonify({'success': True, 'status': 'awaiting_login',
                            'applicationId': application_id})

        # ── Login confirmed — mark as done BEFORE building the response ──────
        # This ensures any concurrent poll that arrives while we are loading
        # the form will get awaiting_login and be silently ignored.
        session.login_completed = True

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

        if (current_q.input_type or '').lower() == 'file':
            user_answer = _resolve_resume_upload_answer(user_answer)
            step = resume_upload_agent(
                driver=session.driver,
                wait=session.wait,
                questions=session.questions,
                index=session.index,
                answer=user_answer,
            )
        else:
            step = answer_current_and_advance(
                driver=session.driver,
                wait=session.wait,
                questions=session.questions,
                index=session.index,
                answer=user_answer,
            )

        status = step.get('status')
        progress_messages = step.get('progressMessages') or []
        if status == 'submitted':
            delete_session(application_id)
            return jsonify({
                'success': True,
                'status': 'submitted',
                'message': step.get('message') or '✅ Submitted the form.',
                'progressMessages': progress_messages,
                'applyUrl': session.apply_url,
            })

        if status == 'needs_retry':
            # Fill failed on a required field — do NOT delete session or advance index.
            # Re-ask the exact same question with a "please try again" prefix.
            q = step.get('question')
            prompt = step.get('prompt', '')
            missing = [{
                'label': q.label,
                'required': q.required,
                'input_type': q.input_type,
                'options': q.options,
            }] if q else []
            retry_message = f"⚠️ Please answer this question again...\n\n{prompt}" if prompt else \
                            "⚠️ Please answer this question again..."
            return jsonify({
                'success': True,
                'status': 'needs_info',
                'message': retry_message,
                'applicationId': session.application_id,
                'missing': missing,
                'progressMessages': progress_messages,
                'applyUrl': session.apply_url,
            })

        if status == 'needs_info':
            # Update session state (either advanced on same page or moved to new page)
            session.index = int(step.get('index', session.index))
            if step.get('questions') is not None:
                session.questions = step.get('questions')
            response = _auto_answer_or_prompt(session)
            if progress_messages:
                response['progressMessages'] = progress_messages
            return jsonify(response)

        # error — unrecoverable
        delete_session(application_id)
        return jsonify({
            'success': True,
            'status': 'error',
            'message': f"⚠️ {step.get('message') or 'Auto-apply could not complete.'}",
            'progressMessages': progress_messages,
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
