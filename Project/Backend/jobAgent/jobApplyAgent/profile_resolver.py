from __future__ import annotations

import re
from typing import Any, Dict, Optional


def _first_non_empty(*vals: Any) -> Optional[str]:
    for v in vals:
        if v is None:
            continue
        if isinstance(v, str) and v.strip():
            return v.strip()
        if not isinstance(v, str) and v:
            return str(v)
    return None


def normalize_profile(profile: Dict[str, Any] | None) -> Dict[str, str]:
    """Flattens/normalizes profile keys (best-effort)."""
    profile = profile or {}

    def g(*keys: str) -> Optional[str]:
        for k in keys:
            if k in profile and profile[k] is not None:
                return str(profile[k]).strip()
        return None

    name = _first_non_empty(g("name"), g("fullName"), g("full_name"), g("full_name"), g("username"))
    email = _first_non_empty(g("email"), g("mail"))
    phone = _first_non_empty(g("phone"), g("phoneNumber"), g("mobile"), g("mobileNumber"))

    website = _first_non_empty(g("website"), g("portfolio"), g("portfolioUrl"), g("site"))
    linkedin = _first_non_empty(g("linkedin"), g("linkedinUrl"))
    github = _first_non_empty(g("github"), g("githubUrl"))

    address = _first_non_empty(g("address"), g("location"))
    city = _first_non_empty(g("city"))
    country = _first_non_empty(g("country"))

    resume_path = _first_non_empty(g("resumePath"), g("resume_file"), g("cvPath"))

    first_name = None
    last_name = None
    if name:
        parts = [p for p in re.split(r"\s+", name) if p]
        if parts:
            first_name = parts[0]
            last_name = parts[-1] if len(parts) > 1 else ""

    out: Dict[str, str] = {}
    for k, v in {
        "name": name,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "website": website,
        "linkedin": linkedin,
        "github": github,
        "address": address,
        "city": city,
        "country": country,
        "resume_path": resume_path,
    }.items():
        if v is not None and str(v).strip():
            out[k] = str(v).strip()

    return out


def resolve_answer(question_label: str, profile: Dict[str, str], extra_answers: Dict[str, Any] | None = None) -> Optional[str]:
    """Best-effort mapping from Google Form question label -> profile/extra answer."""
    extra_answers = extra_answers or {}

    # If the UI provides an explicit answer keyed by the label, prefer it.
    direct = _first_non_empty(extra_answers.get(question_label))
    if direct:
        return direct

    label = (question_label or "").strip().lower()

    def has(*words: str) -> bool:
        return any(w in label for w in words)

    if has("email"):
        return profile.get("email")

    if has("phone", "mobile", "contact number", "whatsapp"):
        return profile.get("phone")

    if has("first name", "firstname"):
        return profile.get("first_name") or profile.get("name")

    if has("last name", "lastname", "surname"):
        return profile.get("last_name")

    if has("name", "full name"):
        return profile.get("name")

    if has("linkedin"):
        return profile.get("linkedin")

    if has("github"):
        return profile.get("github")

    if has("portfolio", "website", "site", "url"):
        return profile.get("website")

    if has("address"):
        return profile.get("address")

    if has("city"):
        return profile.get("city")

    if has("country"):
        return profile.get("country")

    # fallback: if extra answers provides a generic 'default'
    return _first_non_empty(extra_answers.get("default"))
