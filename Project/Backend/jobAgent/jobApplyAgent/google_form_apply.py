from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .profile_resolver import normalize_profile, resolve_answer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MissingInfo:
    label: str
    required: bool
    input_type: str
    options: List[str]


def is_google_form_url(url: str) -> bool:
    if not url:
        return False
    try:
        u = urlparse(url)
    except Exception:
        return False

    host = (u.netloc or "").lower()
    path = (u.path or "").lower()

    if host.endswith("forms.gle"):
        return True

    if "docs.google.com" in host and path.startswith("/forms"):
        return True

    return False


def resolve_final_url(url: str, *, timeout_s: int = 15) -> str:
    try:
        resp = requests.get(url, timeout=timeout_s, allow_redirects=True)
        return resp.url or url
    except Exception:
        return url


def _make_driver(*, headless: bool = True) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US")

    try:
        return webdriver.Chrome(options=options)
    except WebDriverException as exc:
        logger.error("Failed to start Chrome WebDriver: %s", exc)
        raise


def _text(el) -> str:
    try:
        return (el.text or "").strip()
    except Exception:
        return ""


def _choice_text(el) -> str:
    """Best-effort extraction of choice label text for radio/checkbox options."""
    # 1) Direct visible text
    t = _text(el)
    if t:
        return t

    # 2) aria-label often carries the option text
    try:
        aria = (el.get_attribute("aria-label") or "").strip()
        if aria:
            return aria
    except Exception:
        pass

    # 3) Fallback: scan descendants for any non-empty text
    try:
        parts = []
        for child in el.find_elements(By.CSS_SELECTOR, "span, div"):
            ct = _text(child)
            if ct:
                parts.append(ct)
        if parts:
            # pick the most informative chunk
            parts.sort(key=len, reverse=True)
            return parts[0]
    except Exception:
        pass

    return ""


def _find_question_title(block) -> str:
    for sel in ("div[role='heading']", "span.M7eMe", "div.M7eMe", "div.Qr7Oae"):
        try:
            t = block.find_element(By.CSS_SELECTOR, sel)
            title = _text(t)
            if title:
                return title
        except NoSuchElementException:
            continue
    # fallback: first line of text
    full = _text(block)
    return full.split("\n", 1)[0].strip() if full else ""


def _is_required(block) -> bool:
    try:
        if block.find_elements(By.CSS_SELECTOR, "span[aria-label*='Required']"):
            return True
    except Exception:
        pass

    title = _find_question_title(block)
    return title.endswith("*")


def _detect_input_type(block) -> Tuple[str, List[str]]:
    # Google Forms often uses a contenteditable textbox instead of <input>/<textarea>
    # Example: <div role="textbox" aria-multiline="true|false" contenteditable="true">...
    textboxes = block.find_elements(By.CSS_SELECTOR, "div[role='textbox']")
    if textboxes:
        try:
            multiline = (textboxes[0].get_attribute("aria-multiline") or "").strip().lower() == "true"
        except Exception:
            multiline = False
        return ("textarea" if multiline else "text"), []

    # file upload
    if block.find_elements(By.CSS_SELECTOR, "input[type='file']"):
        return "file", []

    if block.find_elements(By.CSS_SELECTOR, "textarea"):
        return "textarea", []

    # google forms sometimes uses type=text for email too; still check
    if block.find_elements(By.CSS_SELECTOR, "input[type='email']"):
        return "email", []

    if block.find_elements(By.CSS_SELECTOR, "input[type='text']"):
        return "text", []

    radios = block.find_elements(By.CSS_SELECTOR, "div[role='radio']")
    if radios:
        options = [_choice_text(r) for r in radios]
        options = [o.strip() for o in options if (o or "").strip()]
        # de-dupe while preserving order
        seen = set()
        options = [o for o in options if not (o in seen or seen.add(o))]
        return "radio", options

    checkboxes = block.find_elements(By.CSS_SELECTOR, "div[role='checkbox']")
    if checkboxes:
        options = [_choice_text(c) for c in checkboxes]
        options = [o.strip() for o in options if (o or "").strip()]
        seen = set()
        options = [o for o in options if not (o in seen or seen.add(o))]
        return "checkbox", options

    if block.find_elements(By.CSS_SELECTOR, "div[role='listbox']"):
        return "dropdown", []

    return "unknown", []


def _pick_best_option(options: List[str], answer: str) -> Optional[str]:
    if not options or not answer:
        return None

    a = answer.strip().lower()

    # numeric selection: '1' or '1.' or 'option 1' -> map to option index
    m = re.search(r"\b(\d{1,3})\b", a)
    if m:
        try:
            idx = int(m.group(1))
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except Exception:
            pass

    # single-letter selection: 'a' -> 1, 'b' -> 2
    if len(a) == 1 and a.isalpha():
        idx = ord(a.lower()) - ord("a") + 1
        if 1 <= idx <= len(options):
            return options[idx - 1]

    # exact / case-insensitive
    for o in options:
        if o.strip().lower() == a:
            return o

    # contains
    for o in options:
        if a in o.strip().lower() or o.strip().lower() in a:
            return o

    # light fuzzy: choose option with max token overlap
    a_tokens = set(re.findall(r"[a-z0-9]+", a))
    best = None
    best_score = 0
    for o in options:
        o_tokens = set(re.findall(r"[a-z0-9]+", o.lower()))
        score = len(a_tokens & o_tokens)
        if score > best_score:
            best_score = score
            best = o
    return best if best_score > 0 else None


def _is_interactable(el) -> bool:
    try:
        if not el.is_displayed():
            return False
        if not el.is_enabled():
            return False
        if el.get_attribute("readonly") is not None:
            return False
        if (el.get_attribute("aria-disabled") or "").strip().lower() == "true":
            return False
        if el.get_attribute("disabled") is not None:
            return False
        return True
    except Exception:
        return False


def _scroll_into_view(driver: webdriver.Chrome, el) -> None:
    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            el,
        )
    except Exception:
        return


def _safe_click(driver: webdriver.Chrome, el) -> None:
    _scroll_into_view(driver, el)
    try:
        el.click()
        return
    except WebDriverException:
        # Try an ActionChains click (often helps when overlays/scroll issues exist)
        try:
            ActionChains(driver).move_to_element(el).pause(0.05).click(el).perform()
            return
        except Exception:
            # Final fallback: JS click
            driver.execute_script("arguments[0].click();", el)


def _set_value_js(driver: webdriver.Chrome, el, value: str) -> None:
    """Best-effort JS value set + input events for stubborn Google Forms fields."""
    try:
        tag = (el.tag_name or "").lower()
    except Exception:
        tag = ""

    # contenteditable textbox
    try:
        if (el.get_attribute("contenteditable") or "").strip().lower() == "true":
            driver.execute_script(
                """
                const el = arguments[0];
                const value = arguments[1];
                el.focus();
                el.textContent = value;
                el.dispatchEvent(new InputEvent('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                """,
                el,
                value,
            )
            return
    except Exception:
        pass

    # input/textarea
    if tag in {"input", "textarea"}:
        driver.execute_script(
            """
            const el = arguments[0];
            const value = arguments[1];
            el.focus();
            el.value = value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            el,
            value,
        )


def _select_all_and_clear(el) -> None:
    """Cross-platform select-all + clear."""
    try:
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.BACKSPACE)
        return
    except Exception:
        pass
    try:
        el.send_keys(Keys.COMMAND, "a")
        el.send_keys(Keys.BACKSPACE)
    except Exception:
        return


def _first_visible(block, css: str):
    els = block.find_elements(By.CSS_SELECTOR, css)
    for el in els:
        if _is_interactable(el):
            return el
    for el in els:
        try:
            if el.is_displayed():
                return el
        except Exception:
            continue
    raise NoSuchElementException(f"No visible element for selector: {css}")


def _first_present(block, css: str):
    els = block.find_elements(By.CSS_SELECTOR, css)
    if not els:
        raise NoSuchElementException(f"No element found for selector: {css}")
    return els[0]


def _clear_and_type(driver: webdriver.Chrome, el, value: str) -> None:
    _safe_click(driver, el)

    # Some Google Forms fields are contenteditable and don't implement clear().
    try:
        if (el.get_attribute("contenteditable") or "").strip().lower() == "true":
            _select_all_and_clear(el)
            try:
                el.send_keys(value)
                return
            except WebDriverException:
                _set_value_js(driver, el, value)
                return
    except Exception:
        pass

    try:
        el.clear()
    except WebDriverException:
        _select_all_and_clear(el)

    try:
        el.send_keys(value)
        return
    except WebDriverException:
        # If JS click was used, focus may not be on the element; try active element.
        try:
            active = driver.switch_to.active_element
            if active and active != el:
                _select_all_and_clear(active)
                active.send_keys(value)
                return
        except Exception:
            pass
        # Final fallback: JS set value.
        _set_value_js(driver, el, value)


def _fill_block(
    block,
    *,
    label: str,
    input_type: str,
    options: List[str],
    value: str,
    wait: WebDriverWait,
    driver: webdriver.Chrome,
) -> None:
    if input_type in {"text", "email"}:
        # Prefer real inputs, but support Google Forms' contenteditable textbox too.
        try:
            inp = _first_visible(block, "input[type='text'], input[type='email']")
        except NoSuchElementException:
            inp = _first_visible(block, "div[role='textbox']")
        _clear_and_type(driver, inp, value)
        return

    if input_type == "textarea":
        # Paragraph answer can be <textarea> OR contenteditable div[role=textbox].
        try:
            ta = _first_visible(block, "textarea")
        except NoSuchElementException:
            ta = _first_visible(block, "div[role='textbox']")
        _clear_and_type(driver, ta, value)
        return

    if input_type == "file":
        file_input = _first_present(block, "input[type='file']")
        _scroll_into_view(driver, file_input)
        try:
            file_input.send_keys(value)
        except WebDriverException:
            # Some forms wrap/overlay the real input. JS-click can help focus before send_keys.
            try:
                _safe_click(driver, file_input)
            except Exception:
                pass
            file_input.send_keys(value)
        return

    if input_type == "radio":
        best = _pick_best_option(options, value) or value
        # click the option whose text matches
        radios = block.find_elements(By.CSS_SELECTOR, "div[role='radio']")
        for r in radios:
            if _text(r).strip().lower() == best.strip().lower():
                _safe_click(driver, r)
                return
        # fallback: click first
        if radios:
            _safe_click(driver, radios[0])
        return

    if input_type == "checkbox":
        # support comma-separated list
        desired = [v.strip() for v in re.split(r"[,;/]", value) if v.strip()]
        checkboxes = block.find_elements(By.CSS_SELECTOR, "div[role='checkbox']")
        if not desired:
            if checkboxes:
                _safe_click(driver, checkboxes[0])
            return
        for d in desired:
            best = _pick_best_option(options, d)
            for c in checkboxes:
                if best and _text(c).strip().lower() == best.strip().lower():
                    _safe_click(driver, c)
        return

    if input_type == "dropdown":
        listbox = _first_visible(block, "div[role='listbox']")
        _safe_click(driver, listbox)

        def _visible_overlay_options(drv):
            opts = drv.find_elements(By.CSS_SELECTOR, "div[role='option']")
            visible = []
            for o in opts:
                try:
                    if o.is_displayed():
                        visible.append(o)
                except Exception:
                    continue
            return visible if visible else False

        overlay_options = wait.until(_visible_overlay_options)
        texts = [_text(o) for o in overlay_options]
        best_text = _pick_best_option([t for t in texts if t], value)
        for o in overlay_options:
            if best_text and _text(o).strip().lower() == best_text.strip().lower():
                _safe_click(driver, o)
                return
        _safe_click(driver, overlay_options[0])
        return


def apply_google_form(
    apply_url: str,
    *,
    profile: Dict[str, Any] | None,
    extra_answers: Dict[str, Any] | None = None,
    headless: bool = True,
    timeout_s: int = 25,
    max_pages: int = 10,
) -> Dict[str, Any]:
    """Attempts to fill and submit a Google Form.

    Returns a dict with:
      - status: 'submitted' | 'needs_info' | 'error'
      - missing: list of MissingInfo-like dicts (if needs_info)
      - message: user-friendly message
    """

    final_url = resolve_final_url(apply_url)

    if not is_google_form_url(final_url):
        return {
            "status": "error",
            "message": "This link is not a Google Form.",
            "finalUrl": final_url,
        }

    normalized_profile = normalize_profile(profile)

    driver = None
    try:
        driver = _make_driver(headless=headless)
        wait = WebDriverWait(driver, timeout_s)

        driver.get(final_url)

        # Guard: sign-in required / permission screens
        page_text = ""
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        except Exception:
            page_text = ""

        if "sign in" in page_text and "continue" in page_text:
            return {
                "status": "error",
                "message": "This Google Form requires sign-in. Auto-apply can’t proceed.",
                "finalUrl": final_url,
            }

        if "you need permission" in page_text or "request access" in page_text:
            return {
                "status": "error",
                "message": "This Google Form requires permission/access. Auto-apply can’t proceed.",
                "finalUrl": final_url,
            }

        for _ in range(max_pages):
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='listitem']")))
            blocks = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

            missing: List[MissingInfo] = []

            for block in blocks:
                label = _find_question_title(block).rstrip("*").strip()
                if not label:
                    continue

                required = _is_required(block)
                input_type, options = _detect_input_type(block)

                value = resolve_answer(label, normalized_profile, extra_answers)

                # Special case: file upload can use resume_path
                if input_type == "file" and not value:
                    value = normalized_profile.get("resume_path")

                if required and not value:
                    missing.append(
                        MissingInfo(
                            label=label,
                            required=required,
                            input_type=input_type,
                            options=options,
                        )
                    )
                    continue

                if value:
                    try:
                        _fill_block(
                            block,
                            label=label,
                            input_type=input_type,
                            options=options,
                            value=value,
                            wait=wait,
                            driver=driver,
                        )
                    except Exception as exc:
                        logger.info("Failed to fill question '%s' (%s): %s", label, input_type, exc)
                        if required:
                            missing.append(
                                MissingInfo(
                                    label=label,
                                    required=required,
                                    input_type=input_type,
                                    options=options,
                                )
                            )

            if missing:
                return {
                    "status": "needs_info",
                    "message": "Some required information is missing.",
                    "missing": [m.__dict__ for m in missing],
                    "finalUrl": final_url,
                }

            # Next or Submit
            def find_button(text: str):
                xpath = f"//span[normalize-space(text())='{text}']/ancestor::div[@role='button']"
                try:
                    return driver.find_element(By.XPATH, xpath)
                except NoSuchElementException:
                    return None

            submit_btn = find_button("Submit")
            next_btn = find_button("Next")

            if submit_btn:
                submit_btn.click()
                # confirmation
                try:
                    wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'response has been recorded')]" )
                        )
                    )
                except TimeoutException:
                    # not all forms show exact text; still consider best-effort submitted
                    pass

                return {
                    "status": "submitted",
                    "message": "✅ Application submitted successfully.",
                    "finalUrl": final_url,
                }

            if next_btn:
                next_btn.click()
                continue

            return {
                "status": "error",
                "message": "Could not find Next/Submit button on the form.",
                "finalUrl": final_url,
            }

        return {
            "status": "error",
            "message": "Form has too many pages; stopped for safety.",
            "finalUrl": final_url,
        }

    except TimeoutException:
        return {
            "status": "error",
            "message": "Timed out while loading the Google Form.",
            "finalUrl": final_url,
        }
    except Exception as exc:
        logger.error("Google Form apply error: %s", exc, exc_info=True)
        return {
            "status": "error",
            "message": f"Auto-apply failed: {exc}",
            "finalUrl": final_url,
        }
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass
