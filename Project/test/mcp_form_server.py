from __future__ import annotations

import uuid
import time
from dataclasses import dataclass
from typing import Optional, Literal

from mcp.server.fastmcp import FastMCP

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from webdriver_manager.chrome import ChromeDriverManager

mcp = FastMCP("google-form-submit")


QuestionType = Literal["text", "paragraph", "radio", "checkbox", "dropdown", "unknown"]


@dataclass
class QuestionInfo:
    index: int
    text: str
    qtype: QuestionType
    options: list[str]


@dataclass
class FormSession:
    driver: webdriver.Chrome
    url: str
    created_at: float
    questions: list[QuestionInfo]


_sessions: dict[str, FormSession] = {}


def _pause(seconds: int) -> None:
    time.sleep(max(0, int(seconds)))


def _start_chrome(visible: bool = True) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()

    if not visible:
        options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _click_submit(driver: webdriver.Chrome, timeout_seconds: int) -> None:
    wait = WebDriverWait(driver, timeout_seconds)

    submit_xpaths = [
        "//div[@role='button' and (@aria-label='Submit' or @data-tooltip='Submit')]",
        "//span[normalize-space()='Submit']/ancestor::*[@role='button'][1]",
        "//div[@role='button'][.//span[normalize-space()='Submit']]",
    ]

    last_error: Optional[Exception] = None
    for xpath in submit_xpaths:
        try:
            el = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            try:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
                    el,
                )
                el.click()
            except WebDriverException:
                driver.execute_script("arguments[0].click();", el)
            return
        except Exception as e:
            last_error = e

    if last_error:
        raise last_error
    raise RuntimeError("Submit button not found")


def _clean_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _guess_question_type_and_options(question_block) -> tuple[QuestionType, list[str]]:
    # Best-effort based on accessibility roles within the listitem.
    if question_block.find_elements(By.CSS_SELECTOR, "textarea"):
        return "paragraph", []

    if question_block.find_elements(By.CSS_SELECTOR, "input[type='text'], input:not([type])"):
        return "text", []

    radios = question_block.find_elements(By.CSS_SELECTOR, "[role='radio']")
    if radios:
        opts: list[str] = []
        for r in radios:
            label = _clean_text(r.get_attribute("aria-label") or r.text or "")
            if label:
                opts.append(label)
        return "radio", opts

    checks = question_block.find_elements(By.CSS_SELECTOR, "[role='checkbox']")
    if checks:
        opts = []
        for c in checks:
            label = _clean_text(c.get_attribute("aria-label") or c.text or "")
            if label:
                opts.append(label)
        return "checkbox", opts

    # Dropdowns are often listbox/combobox.
    if question_block.find_elements(By.CSS_SELECTOR, "[role='listbox'], [role='combobox']"):
        return "dropdown", []

    return "unknown", []


def _extract_question_infos(driver: webdriver.Chrome, timeout_seconds: int, max_questions: int = 50) -> list[QuestionInfo]:
    """Extract questions with a stable index reference and best-effort type/options."""

    WebDriverWait(driver, timeout_seconds).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem'], form"))
    )

    infos: list[QuestionInfo] = []
    seen: set[str] = set()

    list_items = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
    for idx, item in enumerate(list_items):
        candidates = item.find_elements(By.CSS_SELECTOR, "[role='heading']")
        if not candidates:
            candidates = item.find_elements(By.CSS_SELECTOR, "div[dir='auto'], span[dir='auto']")

        picked: Optional[str] = None
        for el in candidates:
            if not el.is_displayed():
                continue
            text = _clean_text(el.text)
            if not text:
                continue
            low = text.lower()
            if low in {"required", "submit", "next", "back"}:
                continue
            picked = text
            break

        if not picked:
            continue

        # Avoid duplicates when Google Forms repeats title blocks.
        if picked in seen:
            continue
        seen.add(picked)

        qtype, options = _guess_question_type_and_options(item)
        infos.append(QuestionInfo(index=idx, text=picked, qtype=qtype, options=options))
        if len(infos) >= max_questions:
            break

    return infos


def _get_question_block(driver: webdriver.Chrome, question_index: int, timeout_seconds: int):
    WebDriverWait(driver, timeout_seconds).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']"))
    )
    blocks = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
    if question_index < 0 or question_index >= len(blocks):
        raise IndexError(f"Question index out of range: {question_index}")
    return blocks[question_index]


def _select_by_text(options: list[str], answer: str) -> Optional[int]:
    ans = _clean_text(answer).lower()
    if not ans:
        return None
    # Allow numeric selection: "1" chooses first option.
    if ans.isdigit():
        i = int(ans) - 1
        return i if 0 <= i < len(options) else None
    for i, opt in enumerate(options):
        if _clean_text(opt).lower() == ans:
            return i
    for i, opt in enumerate(options):
        if ans in _clean_text(opt).lower():
            return i
    return None


def _fill_question(driver: webdriver.Chrome, info: QuestionInfo, answer: str, timeout_seconds: int) -> str:
    block = _get_question_block(driver, info.index, timeout_seconds=timeout_seconds)

    # Text / paragraph
    if info.qtype in {"text", "paragraph"}:
        field = None
        if info.qtype == "paragraph":
            els = block.find_elements(By.CSS_SELECTOR, "textarea")
            field = els[0] if els else None
        else:
            els = block.find_elements(By.CSS_SELECTOR, "input[type='text'], input:not([type])")
            field = els[0] if els else None
        if field is None:
            raise RuntimeError("Could not find text field for this question")

        field.clear()
        field.send_keys(answer)
        return "Filled text"

    # Radio
    if info.qtype == "radio":
        radios = block.find_elements(By.CSS_SELECTOR, "[role='radio']")
        opts = info.options or [
            _clean_text(r.get_attribute("aria-label") or r.text or "") for r in radios
        ]
        choice = _select_by_text(opts, answer)
        if choice is None:
            raise ValueError(f"Invalid answer. Choose one of: {opts}")
        el = radios[choice]
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            el,
        )
        el.click()
        return f"Selected: {opts[choice]}"

    # Checkbox (comma-separated or numbers)
    if info.qtype == "checkbox":
        checks = block.find_elements(By.CSS_SELECTOR, "[role='checkbox']")
        opts = info.options or [
            _clean_text(c.get_attribute("aria-label") or c.text or "") for c in checks
        ]
        raw = _clean_text(answer)
        if not raw:
            return "Skipped"
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        selected: list[str] = []
        for part in parts:
            idx = _select_by_text(opts, part)
            if idx is None:
                raise ValueError(f"Invalid checkbox choice '{part}'. Options: {opts}")
            el = checks[idx]
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
                el,
            )
            el.click()
            selected.append(opts[idx])
        return f"Checked: {', '.join(selected)}"

    # Dropdown
    if info.qtype == "dropdown":
        boxes = block.find_elements(By.CSS_SELECTOR, "[role='listbox'], [role='combobox']")
        if not boxes:
            raise RuntimeError("Could not find dropdown")
        box = boxes[0]
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            box,
        )
        box.click()

        # Once opened, options appear with role=option.
        WebDriverWait(driver, timeout_seconds).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[role='option']"))
        )
        option_els = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
        option_texts = [_clean_text(o.text) for o in option_els if _clean_text(o.text)]
        choice = _select_by_text(option_texts, answer)
        if choice is None:
            raise ValueError(f"Invalid dropdown answer. Options: {option_texts}")
        option_els[choice].click()
        return f"Selected: {option_texts[choice]}"

    raise RuntimeError("Unsupported or unknown question type")


@mcp.tool()
def start_google_form_session(
    url: str,
    timeout_seconds: int = 30,
    visible_browser: bool = True,
    pause_seconds: int = 5,
    max_questions: int = 50,
) -> dict:
    """Start a Chrome session, open the Google Form, and return questions.

    Returns a session_id to be used with answer/submit tools.
    """

    if not url or not url.startswith("http"):
        raise ValueError("Please provide a valid URL starting with http/https")

    # Task 1: Start Chrome
    driver = _start_chrome(visible=visible_browser)
    _pause(pause_seconds)

    # Task 2: Open URL
    driver.get(url)
    _pause(pause_seconds)

    WebDriverWait(driver, timeout_seconds).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # Task 3: Read questions
    questions = _extract_question_infos(driver, timeout_seconds=timeout_seconds, max_questions=max_questions)
    _pause(pause_seconds)

    session_id = uuid.uuid4().hex
    _sessions[session_id] = FormSession(
        driver=driver,
        url=url,
        created_at=time.time(),
        questions=questions,
    )

    return {
        "session_id": session_id,
        "questions": [
            {
                "number": i + 1,
                "text": q.text,
                "type": q.qtype,
                "options": q.options,
            }
            for i, q in enumerate(questions)
        ],
    }


@mcp.tool()
def answer_google_form_question(
    session_id: str,
    question_number: int,
    answer: str,
    timeout_seconds: int = 30,
    pause_seconds: int = 5,
) -> str:
    """Answer a single question in an existing session."""

    if session_id not in _sessions:
        raise KeyError("Invalid session_id")

    session = _sessions[session_id]
    if question_number < 1 or question_number > len(session.questions):
        raise IndexError("question_number out of range")

    info = session.questions[question_number - 1]

    # Task: Fill question
    _pause(pause_seconds)
    status = _fill_question(session.driver, info, answer=answer, timeout_seconds=timeout_seconds)
    _pause(pause_seconds)
    return status


@mcp.tool()
def submit_google_form_session(
    session_id: str,
    timeout_seconds: int = 30,
    keep_browser_open_seconds: int = 2,
    pause_seconds: int = 5,
) -> str:
    """Click Submit in an existing session and try to detect confirmation."""

    if session_id not in _sessions:
        raise KeyError("Invalid session_id")

    driver = _sessions[session_id].driver

    # Task 1: Click Submit
    _pause(pause_seconds)
    _click_submit(driver, timeout_seconds=timeout_seconds)
    _pause(pause_seconds)
    time.sleep(max(0, keep_browser_open_seconds))

    # Task 2: Confirm submission
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(., 'Your response has been recorded') or contains(., 'Thanks for submitting') or contains(., 'response has been recorded')]",
                )
            )
        )
        _pause(pause_seconds)
        return "Submitted. Confirmation message detected."
    except TimeoutException:
        _pause(pause_seconds)
        return "Submitted. Confirmation message not detected (form may require fields or use different language)."


@mcp.tool()
def close_google_form_session(session_id: str, pause_seconds: int = 0) -> str:
    """Close the Chrome session and remove it from the server."""

    sess = _sessions.pop(session_id, None)
    if sess is None:
        return "Session already closed."
    try:
        sess.driver.quit()
    finally:
        _pause(pause_seconds)
    return "Session closed."


if __name__ == "__main__":
    mcp.run()
