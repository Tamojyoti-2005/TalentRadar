
import os
import random

from .skills_data import SKILL_TO_CATEGORY

CATEGORY_TEMPLATES = {
    "Programming Languages": [
        "Walk me through a challenging bug you debugged in {skill} and how you found the root cause.",
        "What {skill} features or idioms do you rely on most, and why?",
        "How do you approach writing testable, maintainable code in {skill}?",
    ],
    "Web & Frontend": [
        "How would you optimize the performance of a {skill} application with a slow initial load?",
        "Describe how you manage state in a complex {skill} app.",
        "How do you approach accessibility and cross-browser compatibility when working with {skill}?",
    ],
    "Backend & Frameworks": [
        "How would you design a scalable API using {skill}?",
        "Tell me about a time you had to optimize a slow endpoint built with {skill}.",
        "How do you handle authentication and authorization in {skill}?",
    ],
    "Data Science & ML": [
        "Describe an end-to-end {skill} project you worked on, including how you validated the results.",
        "How do you handle overfitting or data leakage when working with {skill}?",
        "What metrics would you use to evaluate a model in a {skill} project, and why?",
    ],
    "Data & Databases": [
        "How would you optimize a slow query in {skill}?",
        "Describe how you'd design a schema in {skill} for a high-write-volume application.",
        "How do you ensure data quality and consistency when working with {skill}?",
    ],
    "Cloud & DevOps": [
        "Describe how you'd design a fault-tolerant deployment pipeline using {skill}.",
        "How do you monitor and troubleshoot issues in a {skill}-based production environment?",
        "Walk me through how you'd scale an application horizontally using {skill}.",
    ],
    "Mobile": [
        "How do you handle offline support and data sync in a {skill} app?",
        "What's your approach to performance profiling on {skill}?",
    ],
    "Design & Product": [
        "Walk me through your design process using {skill}, from research to final handoff.",
        "How do you incorporate user feedback into your {skill} workflow?",
    ],
    "Business & Analytics": [
        "Describe a time you used {skill} to influence a business decision.",
        "How do you prioritize competing stakeholder requests using {skill}?",
    ],
    "Soft Skills": [
        "Tell me about a time your {skill} made a difference in a difficult project.",
        "Give an example of how you've demonstrated {skill} under pressure.",
    ],
    "Security": [
        "How would you assess and mitigate risks related to {skill} in a production system?",
        "Describe a security incident you've handled involving {skill}.",
    ],
}

GENERIC_BEHAVIORAL_QUESTIONS = [
    "Tell me about a project you're most proud of and your specific role in it.",
    "Describe a time you disagreed with a teammate or manager. How did you handle it?",
    "How do you prioritize tasks when everything feels urgent?",
    "Tell me about a time you had to learn a new tool or technology quickly.",
    "Describe a mistake you made at work and what you learned from it.",
]

GAP_PROBE_TEMPLATE = (
    "This role calls for {skill}, which isn't clearly reflected on your resume. "
    "Have you worked with it before, or with something comparable? How would you ramp up quickly?"
)


def _template_questions(matched_skills, missing_skills, num_technical=5, num_gap=3, num_behavioral=3):
    questions = []

    matched_list = list(matched_skills)
    random.shuffle(matched_list)
    for skill in matched_list[:num_technical]:
        category = SKILL_TO_CATEGORY.get(skill, "Soft Skills")
        template = random.choice(CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["Soft Skills"]))
        questions.append({"type": "Technical", "skill": skill, "question": template.format(skill=skill)})

    missing_list = list(missing_skills)
    random.shuffle(missing_list)
    for skill in missing_list[:num_gap]:
        questions.append({"type": "Skill Gap", "skill": skill, "question": GAP_PROBE_TEMPLATE.format(skill=skill)})

    behavioral = random.sample(GENERIC_BEHAVIORAL_QUESTIONS, k=min(num_behavioral, len(GENERIC_BEHAVIORAL_QUESTIONS)))
    for q in behavioral:
        questions.append({"type": "Behavioral", "skill": "-", "question": q})

    return questions


NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"


def _try_llm_questions(candidate_name, role_title, matched_skills, missing_skills):
    """
    Optional enhancement: if NVIDIA_API_KEY is set, ask an LLM hosted on
    NVIDIA's OpenAI-compatible API (build.nvidia.com / integrate.api.nvidia.com)
    for sharper interview questions. Returns None (triggering the offline
    template fallback) on any error, missing key, or missing SDK.
    """
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        import json

        client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key)
        prompt = f"""You are helping a recruiter prepare for an interview.
Role: {role_title}
Candidate's matched skills: {', '.join(list(matched_skills)[:15]) or 'none listed'}
Candidate's missing/required skills: {', '.join(list(missing_skills)[:10]) or 'none'}

Generate 8 interview questions total: 4 technical questions probing depth on
the matched skills, 2 questions probing the missing/gap skills, and 2
behavioral questions relevant to this role.

Respond ONLY with a JSON array, no other text, in this exact format:
[{{"type": "Technical", "skill": "<skill>", "question": "<question>"}}, ...]
"""
        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            max_tokens=1200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content or ""
        text = text.strip().strip("```json").strip("```").strip()
        parsed = json.loads(text)
        if isinstance(parsed, list) and parsed:
            return parsed
    except Exception:
        return None
    return None


def generate_questions(candidate_name, role_title, matched_skills, missing_skills, use_llm=False):
    if use_llm:
        llm_questions = _try_llm_questions(candidate_name, role_title, matched_skills, missing_skills)
        if llm_questions:
            return llm_questions
    return _template_questions(matched_skills, missing_skills)
