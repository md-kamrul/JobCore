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

    def _to_text(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, dict):
            parts = []
            for key in ("role", "title", "company", "period", "degree", "school", "gpa", "description", "summary"):
                v = value.get(key)
                if v:
                    parts.append(str(v).strip())
            return " - ".join([p for p in parts if p]) or None
        if isinstance(value, (list, tuple)):
            items = []
            for item in value:
                text = _to_text(item)
                if text:
                    items.append(text)
            return "; ".join(items) if items else None
        return str(value).strip()

    def g(*keys: str) -> Optional[str]:
        for k in keys:
            if k in profile and profile[k] is not None:
                return str(profile[k]).strip()
        return None

    name = _first_non_empty(
        g("full_name"), g("fullName"), g("full-name"), g("name"), g("username"), g("display_name")
    )
    email = _first_non_empty(g("email"), g("mail"))
    phone = _first_non_empty(g("phone"), g("phoneNumber"), g("mobile"), g("mobileNumber"))

    desired_role = _first_non_empty(g("desired_role"), g("desiredRole"), g("role"), g("title"), g("position"))
    bio = _first_non_empty(g("bio"), g("summary"), g("about"), g("about_me"), g("profile_summary"))

    website = _first_non_empty(g("website"), g("portfolio"), g("portfolioUrl"), g("site"))
    linkedin = _first_non_empty(g("linkedin"), g("linkedinUrl"))
    github = _first_non_empty(g("github"), g("githubUrl"))

    address = _first_non_empty(g("address"), g("location"))
    city = _first_non_empty(g("city"))
    country = _first_non_empty(g("country"))

    resume_path = _first_non_empty(g("resumePath"), g("resume_file"), g("cvPath"))

    work_experience = _first_non_empty(
        _to_text(g("work_experience")),
        _to_text(g("workExperience")),
        _to_text(g("experience")),
        _to_text(g("experienceSummary")),
    )
    years_experience = _first_non_empty(g("years_experience"), g("yearsExperience"), g("yearsOfExperience"), g("yoe"))

    education = _first_non_empty(
        _to_text(g("education")),
        _to_text(g("educationSummary")),
        _to_text(g("degree")),
        _to_text(g("school")),
    )

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
        "full_name": name,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "desired_role": desired_role,
        "bio": bio,
        "website": website,
        "linkedin": linkedin,
        "github": github,
        "address": address,
        "city": city,
        "country": country,
        "resume_path": resume_path,
        "work_experience": work_experience,
        "years_experience": years_experience,
        "education": education,
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

    def _norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()

    label_norm = _norm(label)
    label_tokens = set(label_norm.split())

    def _has_phrase(phrase: str) -> bool:
        p_norm = _norm(phrase)
        if not p_norm:
            return False
        if p_norm in label_norm:
            return True
        p_tokens = set(p_norm.split())
        return p_tokens.issubset(label_tokens)

    def has_any(*phrases: str) -> bool:
        return any(_has_phrase(p) for p in phrases)

    if has_any("email", "e-mail", "mail", "email address"):
        return profile.get("email")

    if has_any("phone", "mobile", "contact", "contact number", "whatsapp", "cell", "telephone", "tel"):
        return profile.get("phone")

    if has_any("first name", "firstname", "given name"):
        return profile.get("first_name") or profile.get("name")

    if has_any("last name", "lastname", "surname", "family name"):
        return profile.get("last_name")

    if has_any("full name", "name", "your name", "candidate name"):
        return profile.get("name")

    if has_any("linkedin", "linked in"):
        return profile.get("linkedin")

    if has_any("github", "git hub", "gitlab", "git lab"):
        return profile.get("github")

    if has_any("portfolio", "website", "site", "url", "personal site"):
        return profile.get("website")

    if has_any("resume", "cv", "curriculum vitae", "cover letter", "file upload", "upload"):
        return profile.get("resume_path")

    if has_any("address", "street", "location"):
        return profile.get("address")

    if has_any("city"):
        return profile.get("city")

    if has_any("country"):
        return profile.get("country")

    if has_any("desired role", "role", "position", "job title", "title", "designation"):
        return profile.get("desired_role")

    if has_any("experience", "work experience", "employment history", "work history", "professional experience"):
        return _first_non_empty(profile.get("work_experience"), profile.get("years_experience"))

    if has_any("years of experience", "years experience", "yoe", "experience years"):
        return _first_non_empty(profile.get("years_experience"), profile.get("work_experience"))

    if has_any("education", "degree", "university", "college", "school", "gpa", "cgpa"):
        return profile.get("education")

    if has_any("about", "bio", "summary", "profile summary", "about yourself"):
        return profile.get("bio")

    # fallback: if extra answers provides a generic 'default'
    return _first_non_empty(extra_answers.get("default"))
