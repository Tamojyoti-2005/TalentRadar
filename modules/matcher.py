from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """Returns 0-100 TF-IDF cosine similarity between resume and JD text."""
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    except ValueError:
        return 0.0
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity) * 100, 2)


def compute_skill_match(resume_skills: set, jd_skills: set):
    """Returns (matched_skills, missing_skills, match_percentage)."""
    if not jd_skills:
        return set(), set(), 100.0
    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    percentage = round(len(matched) / len(jd_skills) * 100, 2)
    return matched, missing, percentage


def compute_experience_score(resume_years: float, required_years: float) -> float:
    """Returns 0-100: full score if resume meets/exceeds requirement."""
    if required_years <= 0:
        return 100.0
    if resume_years >= required_years:
        return 100.0
    return round(max(resume_years / required_years, 0) * 100, 2)


def compute_education_match(resume_education: list, required_education: list) -> float:
    if not required_education:
        return 100.0
    resume_ed_lower = {e.lower() for e in resume_education}
    for req in required_education:
        if req.lower() in resume_ed_lower:
            return 100.0
    return 0.0 if resume_education else 50.0  # partial credit if unclear
