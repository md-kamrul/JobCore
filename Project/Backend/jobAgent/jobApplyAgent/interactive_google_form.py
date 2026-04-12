from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .google_form_apply import (
    MissingInfo,
    _detect_input_type,
    _fill_block,
    _find_question_title,
    _is_required,
    _make_driver,
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

        if input_type == "dropdown" and not options and wait is not None:
            options = _peek_dropdown_options(block, wait, driver)

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

    questions = _scan_questions(driver, wait)
    if not questions:
        driver.quit()
        return {"ok": False, "error": "no_questions", "message": "Could not find any fillable questions on the form.", "finalUrl": final_url}

    return {"ok": True, "driver": driver, "wait": wait, "finalUrl": final_url, "questions": questions, "index": 0}


def next_prompt(questions: List[QuestionRef], index: int) -> Tuple[Optional[QuestionRef], str]:
    if index >= len(questions):
        return None, ""

    q = questions[index]
    msg = f"{q.label}"
    if q.required:
        msg += " (required)"
    # If there are explicit options (radio/checkbox/dropdown), show them as a numbered list
    if q.options:
        opts = q.options
        opt_lines = []
        for i, o in enumerate(opts, start=1):
            opt_lines.append(f"{i}. {o}")
        msg += "\nOptions:\n" + "\n".join(opt_lines)
        if q.input_type == "checkbox":
            msg += ("\n\nSelect one or more options by number or text, separated by commas or semicolons. "
                     "(e.g. 1,3 or Option A; Option B)")
        else:
            msg += "\n\nReply with the option number (e.g. 1) or the option text."
    if q.input_type == "file":
        msg += "\nPlease send a local file path to upload."

    return q, msg


def answer_current_and_advance(
    *,
    driver,
    wait: WebDriverWait,
    questions: List[QuestionRef],
    index: int,
    answer: str,
    timeout_s: int = 25,
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
        )
    except WebDriverException as exc:
        logger.info("Interactive fill failed for '%s' (%s): %s", q.label, q.input_type, exc)
        return {
            "status": "error",
            "message": f"Could not fill the field for '{q.label}'. Please try again or apply manually. ({exc})",
        }
    except Exception as exc:
        logger.info("Interactive fill failed for '%s' (%s): %s", q.label, q.input_type, exc)
        return {
            "status": "error",
            "message": f"Could not fill the field for '{q.label}'. Please try again or apply manually.",
        }

    # Move to next question on this page
    index += 1
    if index < len(questions):
        nq, prompt = next_prompt(questions, index)
        return {"status": "needs_info", "index": index, "question": nq, "prompt": prompt}

    # End of page questions: click Submit if present else Next
    submit_btn = _find_nav_button(driver, "submit")
    if submit_btn:
        _click_button(driver, submit_btn)
        # confirmation
        try:
            WebDriverWait(driver, timeout_s).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'response has been recorded')]" )
                )
            )
        except TimeoutException:
            pass
        return {"status": "submitted", "message": "✅ Submitted the form."}

    next_btn = _find_nav_button(driver, "next")
    if not next_btn:
        return {"status": "error", "message": "Could not find Next/Submit button on the form."}

    _click_button(driver, next_btn)

    # Wait for next page and rescan
    WebDriverWait(driver, timeout_s).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']")))
    new_questions = _scan_questions(driver, wait)
    if not new_questions:
        return {"status": "error", "message": "Could not find questions on the next page."}

    nq, prompt = next_prompt(new_questions, 0)
    return {
        "status": "needs_info",
        "index": 0,
        "questions": new_questions,
        "question": nq,
        "prompt": prompt,
    }
