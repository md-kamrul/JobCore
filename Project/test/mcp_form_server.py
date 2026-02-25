from __future__ import annotations

import time
from typing import Optional

from mcp.server.fastmcp import FastMCP

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from webdriver_manager.chrome import ChromeDriverManager

mcp = FastMCP("google-form-submit")


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


@mcp.tool()
def submit_google_form(
    url: str,
    timeout_seconds: int = 30,
    visible_browser: bool = True,
    keep_browser_open_seconds: int = 2,
    pause_seconds: int = 5,
) -> str:
    """Open a Google Form URL in Chrome and click the Submit button.

    Limitations: This does not fill form fields. If your form has required questions,
    Google Forms will block submission.
    """

    if not url or not url.startswith("http"):
        raise ValueError("Please provide a valid URL starting with http/https")

    driver: Optional[webdriver.Chrome] = None
    try:
        # Task 1: Start Chrome
        driver = _start_chrome(visible=visible_browser)
        _pause(pause_seconds)

        # Task 2: Open the URL
        driver.get(url)
        _pause(pause_seconds)

        WebDriverWait(driver, timeout_seconds).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Task 3: Click Submit
        _pause(pause_seconds)

        _click_submit(driver, timeout_seconds=timeout_seconds)
        _pause(pause_seconds)
        time.sleep(max(0, keep_browser_open_seconds))

        # Best-effort confirmation detection (English UI)
        # Task 4: Confirm submission
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
            return "Clicked Submit. Confirmation message detected."
        except TimeoutException:
            _pause(pause_seconds)
            return "Clicked Submit. Confirmation message not detected (form may require fields or use different language)."

    finally:
        # Task 5: Close browser
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass

        _pause(pause_seconds)


if __name__ == "__main__":
    mcp.run()
