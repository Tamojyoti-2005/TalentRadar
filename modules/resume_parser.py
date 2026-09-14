
import re
from dataclasses import dataclass, field

from .skills_data import ALL_SKILLS, DEGREE_KEYWORDS

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?){2,4}\d{3,4}")

# e.g. "5 years of experience", "3+ yrs", "experience: 4 years"
EXPERIENCE_PATTERNS = [
    # allows a few descriptive words between "years of" and "experience",
    # e.g. "5 years of professional experience", "3 years of hands-on industry experience"
    re.compile(r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s*(?:of)?\s*(?:[\w-]+\s+){0,3}experience", re.I),
    re.compile(r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)", re.I),
]


@dataclass
class Candidate:
    filename: str
    raw_text: str
    name: str = "Unknown Candidate"
    email: str = ""
    phone: str = ""
    skills: set = field(default_factory=set)
    experience_years: float = 0.0
    education: list = field(default_factory=list)


def guess_name(text: str, filename: str) -> str:
    """
    Heuristic: the candidate's name is usually the first non-empty line
    that isn't an email/phone/URL and is reasonably short.
    """
    for line in text.splitlines()[:8]:
        line = line.strip()
        if not line:
            continue
        if EMAIL_RE.search(line) or "http" in line.lower():
            continue
        if any(ch.isdigit() for ch in line):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w[0].isalpha()):
            return line.title()
    # fallback: use the filename without extension
    base = filename.rsplit(".", 1)[0]
    return base.replace("_", " ").replace("-", " ").title()


def extract_email(text: str) -> str:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = PHONE_RE.search(text)
    return match.group(0).strip() if match else ""


def extract_skills(text: str) -> set:
    found = set()
    lower_text = text.lower()
    for skill in ALL_SKILLS:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill.lower()) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, lower_text):
            found.add(skill)
    return found


def extract_experience_years(text: str) -> float:
    for pattern in EXPERIENCE_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    # fallback: estimate from the span between the earliest and latest
    # 4-digit years mentioned anywhere in the document (education + jobs)
    all_years = [int(y) for y in re.findall(r"\b((?:19|20)\d{2})\b", text)]
    if all_years:
        span = max(all_years) - min(all_years)
        if 0 < span < 45:
            return float(span)
    return 0.0


def extract_education(text: str) -> list:
    found = []
    for degree in DEGREE_KEYWORDS:
        if re.search(re.escape(degree), text, re.I):
            found.append(degree.strip("."))
    # de-duplicate while preserving order
    seen = set()
    unique = []
    for d in found:
        if d.lower() not in seen:
            seen.add(d.lower())
            unique.append(d)
    return unique


def parse_resume(filename: str, text: str) -> Candidate:
    return Candidate(
        filename=filename,
        raw_text=text,
        name=guess_name(text, filename),
        email=extract_email(text),
        phone=extract_phone(text),
        skills=extract_skills(text),
        experience_years=extract_experience_years(text),
        education=extract_education(text),
    )
