from __future__ import annotations

import logging
import os
import re
import shutil
import socket
import subprocess
import time
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

# ── Persistent Chrome profile used for Gmail login ───────────────────────────
# Stored in the user's home so cookies/session survive across restarts.
_JOBCORE_PROFILE_DIR = os.path.expanduser("~/.jobcore_chrome_profile")

# macOS Chrome locations (tried in order)
_CHROME_PATHS_MAC = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
]


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


def _find_chrome_binary() -> str:
    """Return path to the system Chrome/Chromium binary."""
    for path in _CHROME_PATHS_MAC:
        if os.path.isfile(path):
            return path
    found = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if found:
        return found
    raise FileNotFoundError(
        "Could not find Chrome or Chromium. Please install Google Chrome."
    )


def _free_port() -> int:
    """Return a free TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _make_driver(*, headless: bool = True) -> webdriver.Chrome:
    """Standard Selenium driver — used for Google Forms (no Gmail login needed)."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )
        return driver
    except WebDriverException as exc:
        logger.error("Failed to start Chrome WebDriver: %s", exc)
        raise


def _make_stealth_driver(*, headless: bool = False):
    """
    Launch the REAL system Chrome via subprocess with remote debugging,
    then attach Selenium to it via debuggerAddress.

    Returns (driver, port, proc) so callers can store the port for reconnection.
    The Chrome process is accessible via driver._chrome_proc.
    """
    chrome_bin = _find_chrome_binary()
    port = _free_port()
    os.makedirs(_JOBCORE_PROFILE_DIR, exist_ok=True)

    cmd = [
        chrome_bin,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={_JOBCORE_PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1280,900",
        "--lang=en-US",
    ]
    if headless:
        cmd += ["--headless=new", "--disable-gpu"]

    logger.info("Launching real Chrome: %s (port %s)", chrome_bin, port)
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    _wait_for_port(port, timeout_s=15)

    driver = _attach_to_chrome(port)
    driver._chrome_proc = proc   # type: ignore[attr-defined]
    driver._debug_port = port    # type: ignore[attr-defined]
    return driver, port, proc


def _attach_to_chrome(port: int, *, retries: int = 15) -> webdriver.Chrome:
    """
    Connect a new Selenium WebDriver to the Chrome already running on `port`.
    Called both on first launch and whenever the session goes stale.
    """
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    last_exc: Exception = RuntimeError("never tried")
    for _ in range(retries):
        try:
            driver = webdriver.Chrome(options=options)
            # Switch to the most-recently-opened tab
            if driver.window_handles:
                driver.switch_to.window(driver.window_handles[-1])
            return driver
        except Exception as exc:
            last_exc = exc
            time.sleep(1)

    raise RuntimeError(
        f"Could not attach Selenium to Chrome on port {port}: {last_exc}"
    ) from last_exc


def _wait_for_port(port: int, *, timeout_s: float = 15) -> None:
    """Block until the TCP port accepts connections or timeout expires."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.3)
    raise TimeoutError(f"Chrome remote debugging port {port} did not open within {timeout_s}s")


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


def _is_placeholder_option(text: str) -> bool:
    t = re.sub(r"\s+", " ", (text or "").strip().lower())
    if not t:
        return True
    if t in {
        "select",
        "select an option",
        "choose",
        "choose an option",
        "please select",
        "pick one",
        "option",
        "--",
    }:
        return True

    # Common Bengali placeholders seen in forms, e.g. "বাছুন (select)"
    if "বাছুন" in t or "নির্বাচন করুন" in t:
        return True

    # Placeholder variants that include helper words in parenthesis.
    cleaned = re.sub(r"\(.*?\)", "", t).strip()
    if cleaned in {"select", "choose", "select option", "choose option"}:
        return True

    return False


def _ensure_listbox_open(listbox, driver: webdriver.Chrome) -> None:
    """Ensure listbox popup is open and focused."""
    _safe_click(driver, listbox)
    try:
        expanded = (listbox.get_attribute("aria-expanded") or "").strip().lower()
    except Exception:
        expanded = ""

    if expanded == "true":
        return

    for key in (Keys.ENTER, Keys.SPACE, Keys.ARROW_DOWN):
        try:
            listbox.send_keys(key)
            expanded = (listbox.get_attribute("aria-expanded") or "").strip().lower()
            if expanded == "true":
                return
        except Exception:
            continue


def _options_from_listbox_popup(listbox, driver: webdriver.Chrome, *, include_hidden: bool) -> List[Any]:
    """Read option elements from popup container linked to this listbox only."""
    popup_ids = []
    for attr in ("aria-controls", "aria-owns"):
        try:
            raw = (listbox.get_attribute(attr) or "").strip()
        except Exception:
            raw = ""
        if raw:
            popup_ids.extend([p.strip() for p in raw.split() if p.strip()])

    for popup_id in popup_ids:
        try:
            container = driver.find_element(By.ID, popup_id)
        except Exception:
            continue

        opts = container.find_elements(By.CSS_SELECTOR, "div[role='option'], li[role='option']")
        if not include_hidden:
            visible_opts = []
            for o in opts:
                try:
                    if o.is_displayed():
                        visible_opts.append(o)
                except Exception:
                    continue
            opts = visible_opts

        if opts:
            return opts

    return []


def _class_based_dropdown_rows(listbox, driver: webdriver.Chrome, *, include_hidden: bool) -> List[Tuple[str, Any]]:
    """Extract dropdown option rows from known Google Forms class structure.

    Some forms expose option text inside elements with classes:
      OA0qNb ncFHed QXL7Te
    """
    containers: List[Any] = []

    # Prefer popup containers linked to the active listbox.
    for attr in ("aria-controls", "aria-owns"):
        try:
            raw = (listbox.get_attribute(attr) or "").strip()
        except Exception:
            raw = ""
        if not raw:
            continue
        for popup_id in [p.strip() for p in raw.split() if p.strip()]:
            try:
                containers.append(driver.find_element(By.ID, popup_id))
            except Exception:
                continue

    # Fallback to whole page search if popup linkage is missing.
    if not containers:
        containers = [driver]

    rows: List[Tuple[str, Any]] = []
    seen = set()
    selectors = (
        ".OA0qNb.ncFHed.QXL7Te",
        "div.OA0qNb.ncFHed.QXL7Te",
        "span.OA0qNb.ncFHed.QXL7Te",
    )

    for container in containers:
        for sel in selectors:
            try:
                candidates = container.find_elements(By.CSS_SELECTOR, sel)
            except Exception:
                candidates = []

            for c in candidates:
                if not include_hidden:
                    try:
                        if not c.is_displayed():
                            continue
                    except Exception:
                        continue

                label = (_choice_text(c) or _text(c) or "").strip()
                if not label:
                    continue

                # Resolve clickable option container (role=option) when possible.
                click_target = c
                try:
                    role = (c.get_attribute("role") or "").strip().lower()
                except Exception:
                    role = ""

                if role != "option":
                    try:
                        click_target = c.find_element(By.XPATH, "./ancestor::*[@role='option'][1]")
                    except Exception:
                        click_target = c

                key = label.lower()
                if key in seen:
                    continue
                seen.add(key)
                rows.append((label, click_target))

    return rows


def _read_open_dropdown_options(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    *,
    include_hidden: bool = False,
    listbox=None,
):
    def _visible_overlay_options(drv):
        # Prefer popup options tied to this listbox.
        scoped = _options_from_listbox_popup(listbox, drv, include_hidden=False) if listbox is not None else []
        if scoped:
            return scoped

        # Fallback: any visible option on page.
        opts = drv.find_elements(By.CSS_SELECTOR, "div[role='option'], li[role='option']")
        visible = []
        for o in opts:
            try:
                if o.is_displayed():
                    visible.append(o)
            except Exception:
                continue
        return visible if visible else False

    # Make sure dropdown overlay is actually open.
    wait.until(_visible_overlay_options)

    options = []
    if listbox is not None:
        options = _options_from_listbox_popup(listbox, driver, include_hidden=include_hidden)

    if not options:
        all_opts = driver.find_elements(By.CSS_SELECTOR, "div[role='option'], li[role='option']")
        if include_hidden:
            options = all_opts
        else:
            options = []
            for o in all_opts:
                try:
                    if o.is_displayed():
                        options.append(o)
                except Exception:
                    continue

    rows = []
    for o in options or []:
        label = _choice_text(o) or _text(o)
        label = (label or "").strip()
        if label:
            rows.append((label, o))

    seen = set()
    dedup = []
    for label, el in rows:
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        dedup.append((label, el))

    # Class-based fallback for forms that render option text with OA0qNb ncFHed QXL7Te.
    class_rows = _class_based_dropdown_rows(listbox, driver, include_hidden=include_hidden) if listbox is not None else []
    if class_rows:
        existing = {label.lower() for label, _ in dedup}
        for label, el in class_rows:
            if label.lower() in existing:
                continue
            dedup.append((label, el))
            existing.add(label.lower())

    return dedup


def _peek_dropdown_options(block, wait: WebDriverWait, driver: webdriver.Chrome) -> List[str]:
    """Open dropdown and return all option labels for chat prompting."""
    try:
        listbox = _first_visible(block, "div[role='listbox']")
        _ensure_listbox_open(listbox, driver)

        visible_rows = _read_open_dropdown_options(driver, wait, include_hidden=False, listbox=listbox)
        visible_labels = [label for label, _ in visible_rows]
        visible_non_placeholder = [label for label in visible_labels if not _is_placeholder_option(label)]

        # If visible list is placeholder-only, fetch all DOM options as fallback.
        labels = visible_labels
        if not visible_non_placeholder:
            all_rows = _read_open_dropdown_options(driver, wait, include_hidden=True, listbox=listbox)
            all_labels = [label for label, _ in all_rows]
            if all_labels:
                labels = all_labels

        # Some Google Forms lazily materialize options; when scraping still yields
        # only placeholder/one item, enumerate options via keyboard navigation.
        non_placeholder = [label for label in labels if not _is_placeholder_option(label)]
        if len(non_placeholder) <= 1:
            nav_labels = _collect_dropdown_options_by_navigation(listbox, driver)
            if nav_labels:
                labels = nav_labels

        try:
            listbox.send_keys(Keys.ESCAPE)
        except Exception:
            pass

        filtered_labels = [label for label in labels if not _is_placeholder_option(label)]
        # Chat should present only actionable options in serial order.
        return filtered_labels or labels
    except Exception:
        return []


def _active_dropdown_option_text(listbox, driver: webdriver.Chrome) -> str:
    """Return current active option label from aria-activedescendant when available."""
    try:
        active_id = (listbox.get_attribute("aria-activedescendant") or "").strip()
        if not active_id:
            return ""
        active_el = driver.find_element(By.ID, active_id)
        label = _choice_text(active_el) or _text(active_el)
        if label:
            return label.strip()
        data_value = (active_el.get_attribute("data-value") or "").strip()
        return data_value
    except Exception:
        return ""


def _collect_dropdown_options_by_navigation(listbox, driver: webdriver.Chrome, *, max_steps: int = 120) -> List[str]:
    """Enumerate dropdown options by keyboard navigation (fallback for lazy-rendered menus)."""
    labels: List[str] = []
    seen = set()

    def _add(label: str) -> None:
        t = (label or "").strip()
        if not t:
            return
        key = t.lower()
        if key in seen:
            return
        seen.add(key)
        labels.append(t)

    try:
        _safe_click(driver, listbox)
        try:
            listbox.send_keys(Keys.HOME)
        except Exception:
            pass

        # Capture currently focused option if present.
        _add(_active_dropdown_option_text(listbox, driver))

        stale_hits = 0
        for _ in range(max_steps):
            listbox.send_keys(Keys.ARROW_DOWN)
            current = _active_dropdown_option_text(listbox, driver)
            if not current:
                continue
            before = len(labels)
            _add(current)
            if len(labels) == before:
                stale_hits += 1
            else:
                stale_hits = 0

            # If we've moved through a cycle without finding new options, stop.
            if stale_hits >= 8 and len(labels) > 1:
                break
    except Exception:
        return labels

    return labels


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
        radios = block.find_elements(By.CSS_SELECTOR, "div[role='radio']")

        # Match using extracted labels (more reliable than element .text)
        target = re.sub(r"\s+", " ", (best or "").strip().lower())
        if target:
            for r in radios:
                label_text = _choice_text(r) or _text(r)
                if not label_text:
                    try:
                        label_text = _text(r.find_element(By.XPATH, ".."))
                    except Exception:
                        label_text = ""
                label_norm = re.sub(r"\s+", " ", (label_text or "").strip().lower())
                if label_norm and label_norm == target:
                    _safe_click(driver, r)
                    return

        # Fallback: numeric selection (e.g., "2")
        m = re.search(r"\b(\d{1,3})\b", str(value or ""))
        if m:
            try:
                idx = int(m.group(1))
                if 1 <= idx <= len(radios):
                    _safe_click(driver, radios[idx - 1])
                    return
            except Exception:
                pass

        # Only default to the first option when no user input was provided
        if not str(value or "").strip() and radios:
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
        # Precompute checkbox labels for matching
        checkbox_labels = []
        for c in checkboxes:
            label_text = _choice_text(c) or _text(c)
            if not label_text:
                try:
                    label_text = _text(c.find_element(By.XPATH, ".."))
                except Exception:
                    label_text = ""
            checkbox_labels.append((label_text, c))

        clicked = set()
        for d in desired:
            best = _pick_best_option(options, d) or d
            target = re.sub(r"\s+", " ", (best or "").strip().lower())
            matched = False
            if target:
                for label_text, c in checkbox_labels:
                    label_norm = re.sub(r"\s+", " ", (label_text or "").strip().lower())
                    if label_norm and label_norm == target:
                        if c not in clicked:
                            _safe_click(driver, c)
                            clicked.add(c)
                        matched = True
                        break
            if matched:
                continue

            # Fallback: numeric selection (e.g., "1")
            m = re.search(r"\b(\d{1,3})\b", d)
            if m:
                try:
                    idx = int(m.group(1))
                    if 1 <= idx <= len(checkboxes):
                        c = checkboxes[idx - 1]
                        if c not in clicked:
                            _safe_click(driver, c)
                            clicked.add(c)
                except Exception:
                    pass
        return

    if input_type == "dropdown":
        listbox = _first_visible(block, "div[role='listbox']")
        _ensure_listbox_open(listbox, driver)

        visible_rows = _read_open_dropdown_options(driver, wait, include_hidden=False, listbox=listbox)
        all_rows = _read_open_dropdown_options(driver, wait, include_hidden=True, listbox=listbox)
        rows = all_rows or visible_rows
        actionable_rows = [(label, el) for label, el in rows if not _is_placeholder_option(label)] or rows
        labels = [label for label, _ in actionable_rows]
        best_text = _pick_best_option([t for t in labels if t], value)

        for label_text, opt_el in actionable_rows:
            if best_text and label_text.strip().lower() == best_text.strip().lower():
                _safe_click(driver, opt_el)
                return

        m = re.search(r"\b(\d{1,3})\b", str(value or ""))
        if m:
            try:
                idx = int(m.group(1))
                if 1 <= idx <= len(actionable_rows):
                    _safe_click(driver, actionable_rows[idx - 1][1])
                    return
            except Exception:
                pass

        # Default only when value is empty.
        if not str(value or "").strip() and actionable_rows:
            _safe_click(driver, actionable_rows[0][1])
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

                if input_type == "dropdown" and not options:
                    options = _peek_dropdown_options(block, wait, driver)

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
