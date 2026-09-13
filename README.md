# Talent Radar — AI Recruitment Platform

A Streamlit app that screens resumes against a job description, scores and
ranks candidates, flags skill gaps, and drafts interview questions.

## Features

- **Resume parsing** — extracts text from PDF, DOCX, or TXT resumes and pulls
  out name, email, phone, skills, years of experience, and education.
- **Job description parsing** — extracts the role title, required skills,
  minimum experience, and required education from pasted or uploaded text.
- **Matching** — combines TF-IDF semantic similarity with explicit skill-set
  overlap, experience comparison, and education matching.
- **Skill-gap analysis** — shows exactly which required skills each candidate
  is missing.
- **Interview question generation** — drafts technical, skill-gap, and
  behavioral questions per candidate. Works fully offline with built-in
  templates; optionally calls an LLM hosted on NVIDIA's OpenAI-compatible API
  (`integrate.api.nvidia.com`) for sharper, more specific questions if
  `NVIDIA_API_KEY` is set.
- **Ranking dashboard** — a sortable leaderboard, per-candidate detail cards,
  and one-click CSV export. Scoring weights are adjustable from the sidebar.

## Project structure

```
ai_recruitment/
├── app.py                       # Streamlit UI
├── modules/
│   ├── skills_data.py           # Skill keyword database
│   ├── text_extraction.py       # PDF/DOCX/TXT -> plain text
│   ├── resume_parser.py         # Resume -> structured Candidate
│   ├── jd_parser.py             # JD text -> structured JobDescription
│   ├── matcher.py                # Similarity / skill / experience scoring
│   ├── ranker.py                 # Weighted overall score + ranking
│   └── question_generator.py     # Interview question generation
├── requirements.txt
└── README.md
```

## Try it instantly with sample data

The `sample_data/` folder includes a ready-to-use job description and four
resumes spanning strong, moderate, and weak fits — no need to write your own
test data first:

- `job_description_fullstack_developer.txt` — paste into the JD box or upload it
- `resume_maya_chen.txt` — strong fit, well-rounded full-stack profile
- `resume_rahul_verma.txt` — strong/overqualified senior full-stack + DevOps profile
- `resume_arjun_mehta.txt` — moderate fit, backend-only, missing React/TypeScript
- `resume_priya_iyer.txt` — poor fit, UI/UX designer with no backend overlap

Upload all four resumes alongside the sample JD and hit **Screen Candidates**
to see the full range of scores, skill-gap tags, and interview questions in
action.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## Optional: LLM-generated interview questions

By default, interview questions are generated from a built-in template bank
(no API key needed). To have an LLM generate more specific questions instead,
this app calls NVIDIA's OpenAI-compatible endpoint
(`https://integrate.api.nvidia.com/v1`) using the `nvidia/nemotron-3.5-lightning-30b-a3b`
model.

Set your key as an environment variable — **never hardcode it into `app.py`
or `question_generator.py`**, especially if this project might ever end up
in version control or be shared with anyone else:

```bash
export NVIDIA_API_KEY=your_key_here   # Windows (PowerShell): $env:NVIDIA_API_KEY="your_key_here"
streamlit run app.py
```

Or, for local development only, create a `.env` file (already gitignored — see below)
and load it with `python-dotenv`, or set it in your shell profile.

Toggle "Use NVIDIA-hosted LLM for sharper interview questions" in the
sidebar. If the API call fails for any reason (bad key, network issue,
malformed response), the app automatically falls back to the offline
templates — screening never breaks because of the LLM call.

**If you've ever pasted your API key in plain text anywhere (chat, code,
a doc)**, treat it as compromised and rotate/regenerate it from your NVIDIA
account settings before using it for anything real.

## How scoring works

Each candidate gets four sub-scores (0–100):

| Score | What it measures |
|---|---|
| Skill match | % of the JD's detected required skills present on the resume |
| Relevance | TF-IDF cosine similarity between the full resume and JD text |
| Experience | Candidate's years of experience vs. the JD's stated minimum |
| Education | Whether the candidate meets the JD's stated degree requirement |

These are combined into an **overall score** using weights you control from
the sidebar (defaults: 40% skills, 30% relevance, 20% experience, 10%
education).

## Customizing the skills database

Edit `modules/skills_data.py` to add or remove skills/categories — both
resume and JD parsing automatically pick up any changes.

## Notes & limitations

- Skill, name, and experience extraction are heuristic (regex + keyword
  matching), not a full NLP pipeline — always sanity-check the AI-generated
  ranking during actual hiring decisions rather than relying on it as the
  sole signal.
- This tool is not a substitute for compliant, fair hiring practices; treat
  its output as a first-pass triage aid for a human recruiter.
