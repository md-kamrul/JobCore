from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


_CURRENT_YEAR = datetime.now().year


# ─── Education helpers ────────────────────────────────────────────────────────

def _parse_end_year(period: str) -> Optional[int]:
    """Extract the end year from a period string like '2022-2026' or '2020-present'."""
    if not period:
        return None
    period = period.strip().lower()
    if "present" in period or "current" in period or "ongoing" in period or "running" in period:
        return _CURRENT_YEAR + 10  # treat as far future (still studying)
    # grab all 4-digit years
    years = [int(y) for y in re.findall(r"\b(20\d{2}|19\d{2})\b", period)]
    return max(years) if years else None


def _parse_start_year(period: str) -> Optional[int]:
    """Extract the start year from a period string."""
    if not period:
        return None
    years = [int(y) for y in re.findall(r"\b(20\d{2}|19\d{2})\b", period.strip())]
    return min(years) if years else None


def _classify_degree_level(degree: str) -> str:
    """Map a degree string to a broad academic level label."""
    d = (degree or "").strip().lower()

    if re.search(r"\bph\.?d\b|doctor(ate)?|d\.?phil", d):
        return "PhD"
    if re.search(r"\bm\.?sc\b|master|mba|m\.?phil|m\.?eng|msc|mtech|m\.?tech", d):
        return "Postgraduate"
    if re.search(r"\bb\.?sc\b|bachelor|b\.?tech|bsc|b\.?eng|b\.?e\b|undergraduate|honours|hons|b\.?s\b", d):
        return "Undergraduate"
    if re.search(r"\bhsc\b|higher secondary|a.?level|12th|class 12|intermediate|diploma", d):
        return "Higher Secondary"
    if re.search(r"\bssc\b|secondary|o.?level|10th|class 10|matriculation", d):
        return "Secondary"

    return "Student"


def _is_currently_enrolled(period: str) -> bool:
    """Return True if the degree period suggests currently enrolled (not yet graduated)."""
    end = _parse_end_year(period)
    if end is None:
        return False
    return end >= _CURRENT_YEAR


def _education_status_from_list(edu_list: List[Dict]) -> str:
    """
    Given the user's education records, derive a human-readable current academic status.
    Picks the most recent / currently-active degree and infers status from degree + period.
    """
    if not edu_list:
        return ""

    # Separate ongoing vs completed
    ongoing = [e for e in edu_list if _is_currently_enrolled(e.get("period", ""))]
    completed = [e for e in edu_list if not _is_currently_enrolled(e.get("period", ""))]

    def _end(e):
        return _parse_end_year(e.get("period", "")) or 0

    if ongoing:
        # pick the highest-level ongoing degree
        target = max(ongoing, key=_end)
        degree = target.get("degree", "")
        school = target.get("school", "")
        period = target.get("period", "")
        level = _classify_degree_level(degree)

        end_year = _parse_end_year(period)
        start_year = _parse_start_year(period)
        year_label = ""
        if start_year and end_year and end_year > start_year:
            total = end_year - start_year
            elapsed = _CURRENT_YEAR - start_year
            yr = min(max(elapsed + 1, 1), total)
            year_label = f" (Year {yr} of {total})"

        school_part = f" at {school}" if school else ""
        return f"Currently pursuing {degree}{school_part}{year_label}"

    # All completed — pick the most recently finished
    if completed:
        target = max(completed, key=_end)
        degree = target.get("degree", "")
        school = target.get("school", "")
        period = target.get("period", "")
        end_year = _parse_end_year(period) or ""
        school_part = f" from {school}" if school else ""
        grad_part = f" (Graduated {end_year})" if end_year else ""
        return f"Completed {degree}{school_part}{grad_part}"

    return ""


def _education_level_keyword(edu_list: List[Dict]) -> str:
    """
    Return a SHORT keyword for the current education level that can be matched
    against form options like 'Undergraduate', 'Postgraduate', 'PhD', etc.
    """
    if not edu_list:
        return ""

    ongoing = [e for e in edu_list if _is_currently_enrolled(e.get("period", ""))]
    pool = ongoing if ongoing else edu_list

    def _end(e):
        return _parse_end_year(e.get("period", "")) or 0

    target = max(pool, key=_end)
    return _classify_degree_level(target.get("degree", ""))


def _edu_list_to_text(edu_list: List[Dict]) -> str:
    """Convert a list of education dicts to a readable multi-line string."""
    lines = []
    for e in edu_list:
        parts = []
        if e.get("degree"):
            parts.append(e["degree"])
        if e.get("school"):
            parts.append(e["school"])
        if e.get("period"):
            parts.append(e["period"])
        if e.get("gpa"):
            parts.append(f"GPA: {e['gpa']}")
        if parts:
            lines.append(" | ".join(parts))
    return "; ".join(lines)


# ─────────────────────────────────────────────────────────────────────────────

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

    # ── Education: handle raw list-of-dicts from DB ──────────────────────────
    raw_edu = profile.get("education") or profile.get("educationSummary")
    edu_list: List[Dict] = []
    education_text = ""
    education_status = ""
    education_level = ""

    if isinstance(raw_edu, (list, tuple)):
        # Filter to only proper dicts (DB rows)
        edu_list = [e for e in raw_edu if isinstance(e, dict) and (e.get("degree") or e.get("school"))]
        education_text = _edu_list_to_text(edu_list)
        education_status = _education_status_from_list(edu_list)
        education_level = _education_level_keyword(edu_list)
    elif isinstance(raw_edu, str) and raw_edu.strip():
        education_text = raw_edu.strip()
    elif isinstance(raw_edu, dict):
        edu_list = [raw_edu]
        education_text = _edu_list_to_text(edu_list)
        education_status = _education_status_from_list(edu_list)
        education_level = _education_level_keyword(edu_list)

    if not education_text:
        education_text = _first_non_empty(
            _to_text(profile.get("degree")),
            _to_text(profile.get("school")),
        ) or ""
    # ──────────────────────────────────────────────────────────────────────────

    education = education_text or None

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
        "education_status": education_status or None,
        "education_level": education_level or None,
    }.items():
        if v is not None and str(v).strip():
            out[k] = str(v).strip()

    return out


def resolve_answer(
    question_label: str,
    profile: Dict[str, str],
    extra_answers: Dict[str, Any] | None = None,
    options: Optional[List[str]] = None,
) -> Optional[str]:
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

    if has_any(
        "resume", "cv", "curriculum vitae", "curriculum-vitae",
        "cover letter", "file upload", "upload", "upload file",
        "upload resume", "upload cv", "attach resume", "attach cv",
        "your resume", "your cv", "resume file", "cv file",
    ):
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

    if has_any("education", "degree", "university", "college", "school", "gpa", "cgpa", "academic qualification"):
        # For generic education questions return the formatted text summary
        return profile.get("education")

    if has_any(
        "education status", "academic status", "current status", "study status",
        "enrollment status", "student status", "currently studying", "academic level",
        "level of education", "education level", "qualification", "educational background",
    ):
        level = profile.get("education_level", "")
        status = profile.get("education_status", "")
        # If the form has options, try to match the level keyword directly
        # so _pick_best_option can find an exact/fuzzy match (e.g. "Undergraduate")
        if options:
            return _first_non_empty(level, status, profile.get("education"))
        # No options (free text field) — return the full descriptive status
        return _first_non_empty(status, level, profile.get("education"))

    if has_any("about", "bio", "summary", "profile summary", "about yourself"):
        return profile.get("bio")

    # fallback: if extra answers provides a generic 'default'
    return _first_non_empty(extra_answers.get("default"))
