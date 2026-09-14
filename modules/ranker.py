

DEFAULT_WEIGHTS = {
    "semantic": 0.30,
    "skills": 0.40,
    "experience": 0.20,
    "education": 0.10,
}


def compute_overall_score(semantic_score, skill_score, experience_score,
                           education_score, weights=None) -> float:
    weights = weights or DEFAULT_WEIGHTS
    total = (
        semantic_score * weights["semantic"]
        + skill_score * weights["skills"]
        + experience_score * weights["experience"]
        + education_score * weights["education"]
    )
    return round(total, 2)


def rank_candidates(evaluations: list) -> list:
    """
    evaluations: list of dicts each containing at least 'overall_score'.
    Returns the list sorted descending by overall_score with a 'rank' field added.
    """
    ranked = sorted(evaluations, key=lambda e: e["overall_score"], reverse=True)
    for i, item in enumerate(ranked, start=1):
        item["rank"] = i
    return ranked


def suitability_label(score: float) -> str:
    if score >= 80:
        return "Excellent Fit"
    if score >= 65:
        return "Strong Fit"
    if score >= 50:
        return "Moderate Fit"
    if score >= 30:
        return "Weak Fit"
    return "Poor Fit"


# Distinct color per fit tier, used for badges and chart bars in the UI.
TIER_COLORS = {
    "Excellent Fit": "#16A34A",  # green
    "Strong Fit": "#0EA5E9",     # sky blue
    "Moderate Fit": "#EAB308",   # amber/yellow
    "Weak Fit": "#F97316",       # orange
    "Poor Fit": "#DC2626",       # red
}


def suitability_color(score: float) -> str:
    return TIER_COLORS[suitability_label(score)]
