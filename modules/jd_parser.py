
import re
from dataclasses import dataclass, field

from .resume_parser import extract_skills, extract_experience_years
from .skills_data import DEGREE_KEYWORDS

# Spelled-out numbers up to twelve, so JDs that write "three years" etc.
# are still picked up instead of falling through to "Not specified".
_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_NUM = r"(\d+(?:\.\d+)?|" + "|".join(_NUMBER_WORDS) + r")"
_YRS = r"(?:years?|yrs?)"

MIN_EXPERIENCE_PATTERNS = [
    # "3-5 years", "3 to 5 yrs" — take the lower bound of a range
    re.compile(rf"{_NUM}\+?\s*(?:-|–|to)\s*\d+(?:\.\d+)?\s*{_YRS}", re.I),
    # "minimum of 3 years", "min. 3 yrs"
    re.compile(rf"(?:minimum|min\.?)\s*(?:of)?\s*{_NUM}\+?\s*{_YRS}", re.I),
    # "at least 3 years"
    re.compile(rf"at\s*least\s*{_NUM}\+?\s*{_YRS}", re.I),
    # "3+ years"
    re.compile(rf"{_NUM}\+\s*{_YRS}", re.I),
    # "Experience: 3 years", "Experience required - 3+ years" (number after the word)
    re.compile(rf"experience\s*(?:required)?\s*[:\-]?\s*(?:of)?\s*{_NUM}\+?\s*{_YRS}", re.I),
    # "3 years of relevant experience", "3 years' experience", "3 yrs experience"
    re.compile(rf"{_NUM}\s*{_YRS}'?s?\s*(?:of)?\s*(?:[\w-]+\s+){{0,3}}experience", re.I),
]


def _parse_number(token: str):
    token = token.lower()
    if token in _NUMBER_WORDS:
        return float(_NUMBER_WORDS[token])
    try:
        return float(token)
    except ValueError:
        return None


@dataclass
class JobDescription:
    title: str
    raw_text: str
    required_skills: set = field(default_factory=set)
    min_experience_years: float = 0.0
    required_education: list = field(default_factory=list)


def guess_title(text: str) -> str:
    for line in text.splitlines()[:5]:
        line = line.strip()
        if 2 <= len(line.split()) <= 8 and not line.endswith("."):
            return line
    return "Untitled Role"


def extract_min_experience(text: str) -> float:
    for pattern in MIN_EXPERIENCE_PATTERNS:
        match = pattern.search(text)
        if match:
            value = _parse_number(match.group(1))
            if value is not None:
                return value
    return 0.0


def extract_required_education(text: str) -> list:
    found = []
    for degree in DEGREE_KEYWORDS:
        if re.search(re.escape(degree), text, re.I):
            found.append(degree.strip("."))
    seen, unique = set(), []
    for d in found:
        if d.lower() not in seen:
            seen.add(d.lower())
            unique.append(d)
    return unique


def parse_job_description(text: str, title_override: str = "") -> JobDescription:
    return JobDescription(
        title=title_override.strip() or guess_title(text),
        raw_text=text,
        required_skills=extract_skills(text),
        min_experience_years=extract_min_experience(text),
        required_education=extract_required_education(text),
    )
