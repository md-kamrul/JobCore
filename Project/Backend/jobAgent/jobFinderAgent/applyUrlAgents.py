import logging
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApplyUrlResult:
    details_url: str
    apply_url: str
    found: bool
    reason: str


_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _is_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def _normalize_candidate_url(candidate: str, base_url: str) -> Optional[str]:
    if not candidate:
        return None

    candidate = candidate.strip().strip('"').strip("'")
    if not candidate or candidate.lower().startswith(("javascript:", "#")):
        return None

    # handle relative links
    joined = urljoin(base_url, candidate)

    if not _is_http_url(joined) and not joined.lower().startswith(("mailto:", "tel:")):
        return None

    return joined


def agent_a_extract_apply_url(details_url: str, *, timeout_s: int = 20) -> ApplyUrlResult:
    """Agent-A: visits a job details page and tries to extract the external apply link.

    This is best-effort scraping. Some job sites require JS rendering or block bots; in those
    cases we fall back to returning the original details URL.
    """

    if not details_url or not _is_http_url(details_url):
        return ApplyUrlResult(
            details_url=details_url or "",
            apply_url=details_url or "",
            found=False,
            reason="invalid_details_url",
        )

    try:
        session = requests.Session()
        response = session.get(
            details_url,
            headers={
                "User-Agent": _USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=timeout_s,
            allow_redirects=True,
        )
        response.raise_for_status()
    except Exception as exc:
        logger.warning("Apply URL extraction fetch failed: %s", exc)
        return ApplyUrlResult(
            details_url=details_url,
            apply_url=details_url,
            found=False,
            reason="fetch_failed",
        )

    final_url = response.url or details_url

    # Basic HTML parse
    try:
        soup = BeautifulSoup(response.text or "", "lxml")
    except Exception as exc:
        logger.warning("Apply URL extraction parse failed: %s", exc)
        return ApplyUrlResult(
            details_url=details_url,
            apply_url=final_url,
            found=False,
            reason="parse_failed",
        )

    apply_text_re = re.compile(r"\bapply\b", re.IGNORECASE)

    def candidate_urls_from_tag(tag):
        candidates = []

        # anchor href
        if tag.name == "a":
            candidates.append(tag.get("href"))

        # common data attributes
        for attr in (
            "data-href",
            "data-url",
            "data-apply-url",
            "data-applylink",
            "data-apply-link",
            "data-action-url",
        ):
            candidates.append(tag.get(attr))

        # onclick handlers sometimes contain URL
        onclick = tag.get("onclick")
        if onclick and isinstance(onclick, str):
            # crude extraction of http(s)://...
            m = re.search(r"(https?://[^\"'\s)]+)", onclick)
            if m:
                candidates.append(m.group(1))

        return [c for c in candidates if c]

    # Prefer likely apply buttons/links
    likely_tags = []
    for tag in soup.find_all(["a", "button"]):
        text = (tag.get_text(" ") or "").strip()
        attrs = " ".join(
            [
                str(tag.get("id") or ""),
                " ".join(tag.get("class") or []),
                str(tag.get("aria-label") or ""),
            ]
        )

        if apply_text_re.search(text) or apply_text_re.search(attrs):
            likely_tags.append(tag)

    # Also consider anchors whose href contains 'apply'
    for tag in soup.find_all("a", href=True):
        href = tag.get("href") or ""
        if "apply" in href.lower():
            likely_tags.append(tag)

    # Deduplicate while keeping order
    seen_ids = set()
    ordered_tags = []
    for t in likely_tags:
        key = id(t)
        if key in seen_ids:
            continue
        seen_ids.add(key)
        ordered_tags.append(t)

    for tag in ordered_tags:
        for raw in candidate_urls_from_tag(tag):
            normalized = _normalize_candidate_url(raw, final_url)
            if not normalized:
                continue

            # Ignore self-referential hash links
            if normalized.rstrip("/") == final_url.rstrip("/"):
                continue

            return ApplyUrlResult(
                details_url=details_url,
                apply_url=normalized,
                found=True,
                reason="apply_button_link_found",
            )

    # Fallback: look for meta tags that might contain external apply links
    for meta in soup.find_all("meta"):
        content = meta.get("content") or ""
        if "apply" in content.lower() and "http" in content.lower():
            m = re.search(r"(https?://\S+)", content)
            if m:
                normalized = _normalize_candidate_url(m.group(1), final_url)
                if normalized:
                    return ApplyUrlResult(
                        details_url=details_url,
                        apply_url=normalized,
                        found=True,
                        reason="meta_url_found",
                    )

    return ApplyUrlResult(
        details_url=details_url,
        apply_url=final_url,
        found=False,
        reason="no_apply_link_found",
    )


def agent_b_format_apply_url_message(result: ApplyUrlResult) -> str:
    """Agent-B: turns Agent-A result into a user-facing chat message."""

    if result.found and result.apply_url:
        return (
            "✅ I found the application link.\n\n"
            f"Apply here: {result.apply_url}"
        )

    # Best-effort fallback
    if result.apply_url:
        return (
            "⚠️ I couldn’t reliably find an external apply button on that page.\n\n"
            f"Here’s the job link I checked: {result.apply_url}"
        )

    return "⚠️ I couldn’t extract an apply link from that job page."