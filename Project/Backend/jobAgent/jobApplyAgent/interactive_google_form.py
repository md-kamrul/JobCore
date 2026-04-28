from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .google_form_apply import (
    MissingInfo,
    _attach_to_chrome,
    _detect_input_type,
    _fill_block,
    _find_question_title,
    _is_required,
    _make_driver,
    _make_stealth_driver,
    _auto_check_email_record_permissions,
    _peek_dropdown_options,
    is_google_form_url,
    resolve_final_url,
)

logger = logging.getLogger(__name__)


@dataclass
class QuestionRef:
    label: str
    required: bool
    input_type: str
    options: List[str]
    occurrence: int  # nth occurrence of this label on the page


def _page_text(driver) -> str:
    try:
        return (driver.find_element(By.TAG_NAME, "body").text or "").lower()
    except Exception:
        return ""


def _is_block_fillable(block) -> bool:
    input_type, _ = _detect_input_type(block)
    return input_type in {"text", "email", "textarea", "radio", "checkbox", "dropdown", "file"}


def _has_question_heading(block) -> bool:
    for sel in ("div[role='heading']", "span.M7eMe", "div.M7eMe", "div.Qr7Oae"):
        try:
            if block.find_elements(By.CSS_SELECTOR, sel):
                return True
        except Exception:
            continue
    return False


def _norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _is_dropdown_placeholder_option(text: str) -> bool:
    t = _norm_text(text)
    if not t:
        return True

    # English placeholder variants
    if t in {"choose", "choose an option", "select", "select an option", "option", "--"}:
        return True

    # Bengali placeholder variants
    if "বাছুন" in t or "নির্বাচন করুন" in t:
        return True

    # Placeholder variants wrapped with helper hints, e.g. "Choose (select)"
    cleaned = re.sub(r"\(.*?\)", "", t).strip()
    if cleaned in {"choose", "select", "choose option", "select option"}:
        return True

    return False


def _normalize_options(options: Optional[List[str]], *, input_type: str = "") -> List[str]:
    if not options:
        return []

    out: List[str] = []
    seen = set()
    for raw in options:
        parts = [p.strip() for p in re.split(r"[\r\n]+", str(raw or "")) if p.strip()]
        if not parts and str(raw or "").strip():
            parts = [str(raw).strip()]
        for part in parts:
            if (input_type or "").lower() == "dropdown" and _is_dropdown_placeholder_option(part):
                continue
            key = _norm_text(part)
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(part)
    return out


def _is_email_record_checkbox_question(q: QuestionRef) -> bool:
    if not q or (q.input_type or "").lower() != "checkbox":
        return False
    text = _norm_text(" ".join([q.label or "", *[str(o or "") for o in (q.options or [])]]))
    if "record my email" in text or "record email" in text:
        return True
    if "email" in text and any(k in text for k in ("record", "save", "store", "keep")):
        return True
    if "ইমেইল" in text and any(k in text for k in ("রেকর্ড", "সংরক্ষণ", "সেভ", "রাখ")):
        return True
    return False


def _scan_questions(driver, wait: Optional[WebDriverWait] = None) -> List[QuestionRef]:
    blocks = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

    seen_count: Dict[str, int] = {}
    questions: List[QuestionRef] = []

    for block in blocks:
        if not _is_block_fillable(block):
            continue

        label = _find_question_title(block).rstrip("*").strip()
        if not label:
            continue

        required = _is_required(block)
        input_type, options = _detect_input_type(block)

        if input_type == "dropdown" and wait is not None:
            dropdown_options = _peek_dropdown_options(block, wait, driver)
            if dropdown_options:
                options = _normalize_options((options or []) + dropdown_options, input_type=input_type)

        options = _normalize_options(options, input_type=input_type)

        # Some forms render each checkbox/radio option as a separate listitem.
        # If the block lacks a heading and the "label" equals a single option,
        # treat it as an option-only row, not a question.
        if input_type in {"checkbox", "radio"} and options:
            if not _has_question_heading(block):
                if len(options) == 1 and _norm_text(label) == _norm_text(options[0]):
                    continue

        occ = seen_count.get(label, 0)
        seen_count[label] = occ + 1

        questions.append(
            QuestionRef(
                label=label,
                required=required,
                input_type=input_type,
                options=options,
                occurrence=occ,
            )
        )

    return questions


def _find_question_block(driver, question: QuestionRef):
    blocks = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
    matches = []
    for block in blocks:
        if not _is_block_fillable(block):
            continue
        label = _find_question_title(block).rstrip("*").strip()
        if label == question.label:
            matches.append(block)

    if len(matches) > question.occurrence:
        return matches[question.occurrence]

    # fallback: contains
    for block in blocks:
        try:
            if question.label.lower() in (block.text or "").lower():
                return block
        except Exception:
            continue

    raise NoSuchElementException(f"Could not find question block for '{question.label}'")


def _normalize_button_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _find_nav_button(driver, kind: str):
    # kind: 'submit' or 'next'
    candidates = []
    if kind == "submit":
        candidates = ["submit", "send", "finish", "apply", "জমা", "সাবমিট"]
    else:
        candidates = ["next", "continue", "পরবর্তী", "এগিয়ে", "পরের"]

    buttons = driver.find_elements(By.CSS_SELECTOR, "[role='button']")
    for b in buttons:
        try:
            if not b.is_displayed():
                continue
        except Exception:
            continue

        text = _normalize_button_text(b.text)
        aria = _normalize_button_text(b.get_attribute("aria-label") or "")

        hay = f"{text} {aria}".strip()
        if not hay:
            continue

        if any(c in hay for c in candidates):
            return b

    # fallback: some forms put text inside span inside button
    for c in candidates:
        try:
            el = driver.find_element(
                By.XPATH,
                f"//*[@role='button'][.//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{c}')]]",
            )
            return el
        except NoSuchElementException:
            continue

    return None


def _click_button(driver, btn) -> None:
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
    try:
        btn.click()
        return
    except WebDriverException:
        # try JS click
        driver.execute_script("arguments[0].click();", btn)


def _is_submission_confirmed(driver, timeout_s: int = 25) -> bool:
    """Best-effort verification that the form was actually submitted."""
    success_markers = [
        "response has been recorded",
        "your response has been recorded",
        "thanks for submitting",
        "submit another response",
        "edit your response",
        "your response has been submitted",
    ]
    failure_markers = [
        "this is a required question",
        "required question",
        "please answer this question",
    ]

    deadline = time.time() + max(3, int(timeout_s))
    while time.time() < deadline:
        url = _safe_current_url(driver).lower()
        body = _page_text(driver)

        if "formresponse" in url:
            return True

        if any(m in body for m in success_markers):
            return True

        if any(m in body for m in failure_markers):
            return False

        try:
            has_questions = bool(driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']"))
        except Exception:
            has_questions = False

        if not has_questions:
            submit_btn = _find_nav_button(driver, "submit")
            next_btn = _find_nav_button(driver, "next")
            if submit_btn is None and next_btn is None:
                return True

        time.sleep(0.35)

    return False


def start_gmail_login_session(apply_url: str, *, headless: bool = False, timeout_s: int = 25):
    """
    Launch real Chrome at the Gmail sign-in page.
    Returns ok=True with driver, wait, debug_port, and apply_url.
    The debug_port lets callers reconnect if the CDP session drops during login.
    """
    try:
        driver, port, _proc = _make_stealth_driver(headless=headless)
    except Exception as exc:
        return {"ok": False, "error": "driver_failed", "message": str(exc)}

    wait = WebDriverWait(driver, timeout_s)
    try:
        driver.get("https://accounts.google.com/signin/v2/identifier?hl=en")
    except Exception as exc:
        try:
            driver.quit()
        except Exception:
            pass
        return {"ok": False, "error": "open_failed", "message": str(exc)}

    return {
        "ok": True,
        "driver": driver,
        "wait": wait,
        "debug_port": port,
        "apply_url": apply_url,
    }


def _safe_current_url(driver) -> str:
    """Return driver.current_url, re-raising only non-session errors."""
    try:
        return driver.current_url or ""
    except Exception:
        return ""


def _driver_is_alive(driver) -> bool:
    """Quick check — False if the WebDriver session is stale/dead."""
    try:
        _ = driver.current_url
        return True
    except Exception:
        return False


def is_gmail_logged_in(driver, *, debug_port: int = 0) -> tuple:
    """
    Check whether the user has completed Gmail login.

    Returns (logged_in: bool, driver).
    If the CDP session dropped, tries to reconnect on debug_port and returns
    the fresh driver. Callers MUST use the returned driver going forward.
    """
    # ── Reconnect if the session went stale ─────────────────────────────────
    if not _driver_is_alive(driver):
        if not debug_port:
            logger.warning("Driver session lost and no debug_port to reconnect.")
            return False, driver
        try:
            logger.info("Session stale — reconnecting to Chrome on port %s", debug_port)
            driver = _attach_to_chrome(debug_port)
            logger.info("Reconnected successfully on port %s", debug_port)
        except Exception as exc:
            logger.warning("Reconnect failed: %s", exc)
            return False, driver

    try:
        url = driver.current_url or ""
    except Exception:
        return False, driver

    # ── Google rejected the automated browser → go back to sign-in ──────────
    if "signin/rejected" in url:
        try:
            driver.get("https://accounts.google.com/signin/v2/identifier?hl=en")
        except Exception:
            pass
        return False, driver

    # ── Still on a Google sign-in page ──────────────────────────────────────
    sign_in_paths = [
        "accounts.google.com/signin",
        "accounts.google.com/v3/signin",
        "accounts.google.com/ServiceLogin",
        "accounts.google.com/o/oauth2",
        "accounts.google.com/AccountChooser",
        "accounts.google.com/v3/signin/challenge",
        "accounts.google.com/v3/signin/identifier",
    ]
    for marker in sign_in_paths:
        if marker in url:
            return False, driver

    # ── Still on accounts.google.com — read page text ───────────────────────
    if "accounts.google.com" in url:
        try:
            # Switch to the foremost tab in case a new one opened during OAuth
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
            body = driver.find_element(By.TAG_NAME, "body").text.lower()
            blocking = ["sign in", "couldn't sign you in", "not secure", "try again"]
            if any(p in body for p in blocking):
                return False, driver
        except Exception:
            pass

    # ── Any other URL means login succeeded ─────────────────────────────────
    return True, driver


def load_form_after_login(driver, wait, apply_url: str, *, timeout_s: int = 25):
    """Navigate to the Google Form after Gmail login and scan questions."""
    try:
        # Switch to the foremost tab (login may have opened extra tabs)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])

        driver.get(apply_url)
        WebDriverWait(driver, timeout_s).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']"))
        )
        _auto_check_email_record_permissions(driver)
        questions = _scan_questions(driver, wait)
        if not questions:
            return {"ok": False, "error": "no_questions",
                    "message": "Could not find any fillable questions on the form."}
        return {"ok": True, "driver": driver, "wait": wait, "questions": questions, "index": 0}
    except TimeoutException:
        return {"ok": False, "error": "load_timeout",
                "message": "Timed out waiting for the form to load after login."}
    except Exception as exc:
        return {"ok": False, "error": "load_failed", "message": str(exc)}


def start_interactive_session(apply_url: str, *, headless: bool = True, timeout_s: int = 25):
    final_url = resolve_final_url(apply_url)
    if not is_google_form_url(final_url):
        return {"ok": False, "error": "not_google_form", "message": "This link is not a Google Form.", "finalUrl": final_url}

    driver = _make_driver(headless=headless)
    wait = WebDriverWait(driver, timeout_s)

    # Prefer opening the form in a new tab (visible mode). Selenium can't attach to an
    # existing user tab, but it can open an additional tab in the automated window.
    try:
        driver.get("about:blank")
        first_handle = driver.current_window_handle

        driver.execute_script("window.open(arguments[0], '_blank');", final_url)
        driver.switch_to.window(driver.window_handles[-1])

        # Close the initial blank tab if it still exists.
        try:
            if first_handle in driver.window_handles and len(driver.window_handles) > 1:
                driver.switch_to.window(first_handle)
                driver.close()
                driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass
    except Exception:
        driver.get(final_url)

    text = _page_text(driver)
    if "sign in" in text and "continue" in text:
        driver.quit()
        return {"ok": False, "error": "sign_in_required", "message": "This Google Form requires sign-in. Auto-apply can’t proceed.", "finalUrl": final_url}

    if "you need permission" in text or "request access" in text:
        driver.quit()
        return {"ok": False, "error": "permission_required", "message": "This Google Form requires permission/access. Auto-apply can’t proceed.", "finalUrl": final_url}

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']")))

    _auto_check_email_record_permissions(driver)

    questions = _scan_questions(driver, wait)
    if not questions:
        driver.quit()
        return {"ok": False, "error": "no_questions", "message": "Could not find any fillable questions on the form.", "finalUrl": final_url}

    return {"ok": True, "driver": driver, "wait": wait, "finalUrl": final_url, "questions": questions, "index": 0}


def next_prompt(
    questions: List[QuestionRef],
    index: int,
    *,
    driver=None,
    wait: Optional[WebDriverWait] = None,
) -> Tuple[Optional[QuestionRef], str]:
    if index >= len(questions):
        return None, ""

    q = questions[index]

    if (q.input_type or "").lower() == "dropdown":
        try:
            if driver is not None and wait is not None:
                block = _find_question_block(driver, q)
                dropdown_options = _peek_dropdown_options(block, wait, driver)
                if dropdown_options:
                    q.options = _normalize_options((q.options or []) + dropdown_options, input_type=q.input_type)
        except Exception:
            pass

    q.options = _normalize_options(q.options, input_type=q.input_type)

    msg = f"{q.label}"
    if q.required:
        msg += " (required)"

    if (q.input_type or "").lower() == "dropdown":
        msg += "\nType: Dropdown"

    # If there are explicit options (radio/checkbox/dropdown), show them as a numbered list
    if q.options:
        opt_lines = []
        for i, o in enumerate(q.options, start=1):
            opt_lines.append(f"{i}. {o}")
        msg += "\nOptions:\n" + "\n".join(opt_lines)
        if _is_email_record_checkbox_question(q):
            msg += "\n\nReply yes to check this box, or no to leave it unchecked."
        elif q.input_type == "checkbox":
            msg += ("\n\nSelect one or more options by number or text, separated by commas or semicolons. "
                     "(e.g. 1,3 or Option A; Option B)")
        else:
            msg += "\n\nReply with the option number (e.g. 1) or the option text."

    if q.input_type == "file":
        msg += "\nType: File upload"
        msg += "\nReply with 1 to upload /Users/kamrul/Downloads/cv.pdf automatically."

    return q, msg


def resume_upload_agent(
    *,
    driver,
    wait: WebDriverWait,
    questions: List[QuestionRef],
    index: int,
    answer: str,
    timeout_s: int = 25,
) -> Dict[str, Any]:
    """Specialized resume upload handoff for Google Form file questions."""
    if index >= len(questions):
        return {"status": "error", "message": "No pending file-upload question to answer."}

    q = questions[index]
    if q.input_type != "file":
        return {"status": "error", "message": "Current question is not a file-upload field."}

    progress_messages: List[str] = []

    def _record_progress(message: str) -> None:
        if message and message not in progress_messages:
            progress_messages.append(message)

    result = answer_current_and_advance(
        driver=driver,
        wait=wait,
        questions=questions,
        index=index,
        answer=answer,
        timeout_s=timeout_s,
        progress_callback=_record_progress,
    )

    if progress_messages:
        result = {**result, "progressMessages": progress_messages}

    return result


def answer_current_and_advance(
    *,
    driver,
    wait: WebDriverWait,
    questions: List[QuestionRef],
    index: int,
    answer: str,
    timeout_s: int = 25,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    if index >= len(questions):
        return {"status": "error", "message": "No pending question to answer."}

    q = questions[index]

    block = _find_question_block(driver, q)
    try:
        _fill_block(
            block,
            label=q.label,
            input_type=q.input_type,
            options=q.options,
            value=answer,
            wait=wait,
            driver=driver,
            progress_callback=progress_callback,
        )
    except (WebDriverException, Exception) as exc:
        logger.info("Interactive fill failed for '%s' (%s): %s", q.label, q.input_type, exc)
        # If the field is required, ask the user to answer again instead of
        # killing the session.  Return needs_retry so the caller re-asks the
        # same question without advancing the index.
        if q.required:
            _, prompt = next_prompt(questions, index, driver=driver, wait=wait)
            return {
                "status": "needs_retry",
                "index": index,
                "question": q,
                "prompt": prompt,
            }
        # Non-required field — skip it and move on
        return {
            "status": "needs_info",
            "index": index + 1,
            "question": questions[index + 1] if index + 1 < len(questions) else None,
            "prompt": next_prompt(questions, index + 1, driver=driver, wait=wait)[1] if index + 1 < len(questions) else "",
        }

    # Move to next question on this page
    index += 1
    if index < len(questions):
        nq, prompt = next_prompt(questions, index, driver=driver, wait=wait)
        return {"status": "needs_info", "index": index, "question": nq, "prompt": prompt}

    # End of page questions: click Submit if present else Next
    submit_btn = _find_nav_button(driver, "submit")
    if submit_btn:
        _click_button(driver, submit_btn)
        if _is_submission_confirmed(driver, timeout_s=timeout_s):
            return {"status": "submitted", "message": "✅ Submitted the form."}

        return {
            "status": "error",
            "message": "Could not verify that the form was submitted. Please try again.",
        }

    next_btn = _find_nav_button(driver, "next")
    if not next_btn:
        return {"status": "error", "message": "Could not find Next/Submit button on the form."}

    _click_button(driver, next_btn)

    # Wait for next page and rescan
    WebDriverWait(driver, timeout_s).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']")))
    new_questions = _scan_questions(driver, wait)
    if not new_questions:
        return {"status": "error", "message": "Could not find questions on the next page."}

    nq, prompt = next_prompt(new_questions, 0, driver=driver, wait=wait)
    return {
        "status": "needs_info",
        "index": 0,
        "questions": new_questions,
        "question": nq,
        "prompt": prompt,
    }
