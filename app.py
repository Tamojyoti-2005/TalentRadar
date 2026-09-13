"""
AI Recruitment Platform
Screens resumes, matches candidates to a job description, identifies skill
gaps, generates interview questions, and ranks applicants by suitability.

Run with:
    streamlit run app.py
"""
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from modules.text_extraction import extract_text, clean_text
from modules.resume_parser import parse_resume
from modules.jd_parser import parse_job_description
from modules.skills_data import SKILL_TO_CATEGORY, CATEGORY_COLORS, DEFAULT_CATEGORY_COLOR
from modules.matcher import (
    compute_semantic_similarity,
    compute_skill_match,
    compute_experience_score,
    compute_education_match,
)
from modules.ranker import compute_overall_score, rank_candidates, suitability_label, suitability_color
from modules.question_generator import generate_questions

st.set_page_config(
    page_title="Talent Radar | AI Recruitment",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Palette — a lively, multi-hue system rather than one safe accent color:
# a deep indigo base, a violet-to-coral hero gradient, and category/tier
# colors used consistently for skills and scores throughout the app.
# ---------------------------------------------------------------------------
INK = "#1B1436"          # near-black indigo for text/headers
SURFACE = "#FAF9FC"      # soft lavender-white page background
CARD = "#FFFFFF"
BORDER = "#EDE9F7"
VIOLET = "#6D28D9"
VIOLET_DEEP = "#4C1D95"
CORAL = "#F4664A"
GOLD = "#F5B942"
TEAL = "#0EA5E9"
GREEN = "#16A34A"
MUTED = "#6B6580"
SIDEBAR_BG_TOP = "#221A45"
SIDEBAR_BG_BOTTOM = "#150F2B"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Poppins', 'Helvetica Neue', Arial, sans-serif !important;
    }}

    /* ---- Force a single, deliberate theme everywhere (no light/dark collisions) ---- */
    .stApp {{
        background:
            radial-gradient(circle at 6% 8%, rgba(109, 40, 217, 0.30) 0%, rgba(109, 40, 217, 0) 40%),
            radial-gradient(circle at 95% 12%, rgba(244, 102, 74, 0.32) 0%, rgba(244, 102, 74, 0) 38%),
            radial-gradient(circle at 10% 60%, rgba(14, 165, 233, 0.28) 0%, rgba(14, 165, 233, 0) 38%),
            radial-gradient(circle at 92% 55%, rgba(245, 185, 66, 0.30) 0%, rgba(245, 185, 66, 0) 38%),
            radial-gradient(circle at 30% 95%, rgba(22, 163, 74, 0.22) 0%, rgba(22, 163, 74, 0) 36%),
            radial-gradient(circle at 80% 95%, rgba(109, 40, 217, 0.24) 0%, rgba(109, 40, 217, 0) 36%),
            linear-gradient(135deg, #F3EEFC 0%, {SURFACE} 40%, #FDF0EC 100%) !important;
        background-attachment: fixed !important;
    }}
    .main .block-container {{ padding-top: 1.6rem; }}

    h1, h2, h3, h4, .stApp h1, .stApp h2, .stApp h3 {{ color: {INK} !important; letter-spacing: -0.01em; }}
    .stApp p, .stApp span, .stApp label, .stApp li, .stMarkdown, [data-testid="stMarkdownContainer"] {{
        color: {INK};
    }}
    [data-testid="stCaptionContainer"] {{ color: {MUTED} !important; }}

    /* ---- Hero banner ---- */
    .tr-hero {{
        background: linear-gradient(120deg, {VIOLET_DEEP} 0%, {VIOLET} 45%, {CORAL} 100%);
        padding: 2.4rem 2.6rem; border-radius: 18px; margin-bottom: 1.8rem;
        box-shadow: 0 14px 34px rgba(76, 29, 149, 0.35);
        position: relative; overflow: hidden;
    }}
    .tr-hero::after {{
        content: ""; position: absolute; top: -60px; right: -60px;
        width: 220px; height: 220px; border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0) 70%);
    }}
    .tr-hero h1 {{ color: #FFFFFF !important; margin: 0; font-size: 2.3rem; font-weight: 800; }}
    .tr-hero p {{ color: #F3E8FF !important; margin-top: 0.5rem; font-size: 1.05rem; max-width: 660px; }}

    /* ---- Generic cards ---- */
    .tr-card {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px;
        padding: 1.3rem 1.5rem; margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(27, 20, 54, 0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .tr-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 24px rgba(27, 20, 54, 0.10); }}

    .tr-metric {{
        border-radius: 14px; padding: 1rem 1.1rem; color: #FFFFFF !important;
        text-align: center; box-shadow: 0 6px 18px rgba(0,0,0,0.14);
    }}
    .tr-metric .num {{ font-size: 1.7rem; font-weight: 800; color: #FFFFFF !important; }}
    .tr-metric .lbl {{ font-size: 0.8rem; opacity: 0.92; color: #FFFFFF !important; }}

    .tr-rank-badge {{
        display: inline-block; color: #FFFFFF !important; font-weight: 700;
        border-radius: 999px; padding: 0.2rem 0.75rem; font-size: 0.85rem;
        margin-right: 0.6rem;
    }}
    .tr-fit-badge {{
        display: inline-block; color: #FFFFFF !important; font-weight: 600;
        border-radius: 999px; padding: 0.2rem 0.75rem; font-size: 0.8rem;
    }}

    .tr-skill-pill {{
        display: inline-block; color: #FFFFFF !important; padding: 0.22rem 0.7rem;
        border-radius: 999px; font-size: 0.8rem; margin: 0.18rem;
        font-weight: 600; box-shadow: 0 2px 6px rgba(0,0,0,0.10);
    }}
    .tr-skill-pill-missing {{
        display: inline-block; background: #FFFFFF !important; color: {CORAL} !important;
        border: 1.5px dashed {CORAL}; padding: 0.18rem 0.65rem;
        border-radius: 999px; font-size: 0.8rem; margin: 0.18rem; font-weight: 600;
    }}

    .tr-question {{
        border-left: 5px solid {GOLD}; padding: 0.6rem 1rem; margin-bottom: 0.6rem;
        background: #FFFBEF; font-size: 0.95rem; border-radius: 0 10px 10px 0;
        color: {INK} !important; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .tr-question b {{ color: {INK} !important; }}
    .tr-question-gap {{ border-left-color: {CORAL}; background: #FFF3F0; }}
    .tr-question-behavioral {{ border-left-color: {VIOLET}; background: #F6F1FE; }}

    .tr-label {{ color: {MUTED} !important; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.04em; }}

    .tr-section-title {{
        display: flex; align-items: center; gap: 0.6rem; margin: 0.4rem 0 1rem 0;
    }}
    .tr-section-title .bar {{
        width: 6px; height: 26px; border-radius: 4px;
        background: linear-gradient(180deg, {VIOLET}, {CORAL});
    }}
    .tr-section-title span {{ font-size: 1.25rem; font-weight: 700; color: {INK} !important; }}

    /* ---- Candidate leaderboard cards (replaces plain dataframe) ---- */
    .tr-lead-card {{
        display: flex; align-items: center; gap: 1rem;
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px;
        padding: 0.9rem 1.2rem; margin-bottom: 0.7rem;
        box-shadow: 0 3px 12px rgba(27, 20, 54, 0.05);
        border-left: 6px solid var(--accent, {VIOLET});
    }}
    .tr-lead-rank {{
        font-size: 1.1rem; font-weight: 800; color: #FFFFFF !important;
        width: 34px; height: 34px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        background: var(--accent, {VIOLET}); flex-shrink: 0;
    }}
    .tr-lead-name {{ font-weight: 700; color: {INK} !important; font-size: 1rem; }}
    .tr-lead-email {{ color: {MUTED} !important; font-size: 0.82rem; }}
    .tr-lead-bar-track {{
        flex: 1; background: {BORDER}; border-radius: 999px; height: 10px; overflow: hidden; min-width: 100px;
    }}
    .tr-lead-bar-fill {{ height: 100%; border-radius: 999px; background: var(--accent, {VIOLET}); }}
    .tr-lead-score {{ font-weight: 800; color: {INK} !important; min-width: 46px; text-align: right; }}
    .tr-lead-missing {{ color: {MUTED} !important; font-size: 0.78rem; }}

    /* ---- Sidebar: deliberately dark, always readable ---- */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {SIDEBAR_BG_TOP} 0%, {SIDEBAR_BG_BOTTOM} 100%) !important;
    }}
    [data-testid="stSidebar"] * {{ color: #F1ECFB !important; }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: #FFFFFF !important; font-weight: 700 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ color: #B9AEDD !important; }}

    /* Text inputs / textareas: the visible box is the baseweb wrapper, not the
       bare <input>/<textarea> — style both so text is never white-on-white. */
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] [data-baseweb="textarea"],
    [data-testid="stSidebar"] [data-baseweb="base-input"] {{
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.20) !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea {{
        background: transparent !important; color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] input::placeholder, [data-testid="stSidebar"] textarea::placeholder {{
        color: rgba(255,255,255,0.45) !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: rgba(255,255,255,0.08) !important; color: #FFFFFF !important;
        border-color: rgba(255,255,255,0.20) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
        background: rgba(255,255,255,0.06) !important; border: 1.5px dashed rgba(255,255,255,0.28) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.14) !important; }}
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {{
        background-color: {CORAL} !important; box-shadow: 0 0 0 4px rgba(244, 102, 74, 0.25) !important;
    }}
    [data-testid="stSidebar"] .stSlider > div > div > div > div {{ background: {CORAL} !important; }}

    /* All sidebar buttons EXCEPT the primary CTA: give them a real
       contrasting background (they previously kept a default light
       background while we forced their text to white — invisible). */
    [data-testid="stSidebar"] button {{
        background: rgba(255,255,255,0.12) !important;
        color: #FFFFFF !important;
        border: 1.5px solid rgba(255,255,255,0.35) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}
    [data-testid="stSidebar"] button:hover {{
        background: rgba(255,255,255,0.22) !important;
        border-color: rgba(255,255,255,0.5) !important;
    }}
    [data-testid="stSidebar"] button[kind="primary"] {{
        background: linear-gradient(120deg, {CORAL}, #FF8A65) !important;
        border: none !important; font-weight: 700 !important;
        box-shadow: 0 6px 18px rgba(244, 102, 74, 0.35) !important;
        transition: transform 0.15s ease;
    }}
    [data-testid="stSidebar"] button[kind="primary"]:hover {{
        background: linear-gradient(120deg, {CORAL}, #FF8A65) !important;
        transform: translateY(-1px);
    }}
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {{
        color: rgba(255,255,255,0.55) !important;
    }}


    /* ---- Main-area buttons ---- */
    .stApp button {{ border-radius: 10px !important; }}
    .stApp button[kind="secondary"], .stDownloadButton button {{
        border: 1.5px solid {VIOLET} !important; color: {VIOLET} !important; font-weight: 600 !important;
        background: #FFFFFF !important;
    }}
    .stDownloadButton button:hover {{ background: #F6F1FE !important; }}

    /* File-uploader's "Browse files" button in the sidebar renders with
       kind="secondary", so the main-area secondary-button rule above
       (white background + violet text) was winning over the sidebar's
       generic button rule by CSS specificity — producing a white button
       with white icon/text that was invisible. Force it back to the
       sidebar's intended contrasting style. */
    [data-testid="stSidebar"] button[kind="secondary"] {{
        background: rgba(255,255,255,0.12) !important;
        color: #FFFFFF !important;
        border: 1.5px solid rgba(255,255,255,0.35) !important;
    }}
    [data-testid="stSidebar"] button[kind="secondary"]:hover {{
        background: rgba(255,255,255,0.22) !important;
        border-color: rgba(255,255,255,0.5) !important;
    }}

    /* ---- Expanders ---- */
    [data-testid="stExpander"] {{
        border-radius: 14px !important; border: 1px solid {BORDER} !important;
        background: {CARD} !important; margin-bottom: 0.8rem;
        box-shadow: 0 3px 12px rgba(27, 20, 54, 0.05);
    }}
    [data-testid="stExpander"] summary {{ color: {INK} !important; font-weight: 600 !important; }}
    [data-testid="stExpander"] summary p {{ color: {INK} !important; font-weight: 600 !important; }}
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{ background: {CARD} !important; }}

    /* ---- Dataframe (if used) & misc ---- */
    [data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; border: 1px solid {BORDER}; }}
    .stTabs [data-baseweb="tab"] {{ color: {INK} !important; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="tr-hero">
  <h1>🧭 Talent Radar</h1>
  <p>Upload a job description and a stack of resumes. Talent Radar screens each
  candidate, scores their fit, surfaces skill gaps, and drafts interview
  questions — so shortlisting takes minutes, not days.</p>
</div>
""", unsafe_allow_html=True)


def skill_pill_html(skill: str) -> str:
    category = SKILL_TO_CATEGORY.get(skill, "")
    color = CATEGORY_COLORS.get(category, DEFAULT_CATEGORY_COLOR)
    return f"<span class='tr-skill-pill' style='background:{color}'>{skill}</span>"


# ---------------------------------------------------------------------------
# Sidebar — inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("1. Job Description")
    jd_input_mode = st.radio("Provide the JD as", ["Paste text", "Upload file"], horizontal=True)
    jd_text = ""
    role_title_override = st.text_input("Role title (optional)", "")

    if jd_input_mode == "Paste text":
        jd_text = st.text_area("Paste the job description", height=220,
                                placeholder="e.g. We're looking for a Backend Engineer with 4+ years of experience in Python, Django, PostgreSQL...")
    else:
        jd_file = st.file_uploader("Upload JD (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if jd_file:
            jd_text = extract_text(jd_file)

    min_experience_override = st.number_input(
        "Min. years of experience (optional)",
        min_value=0.0, max_value=40.0, value=0.0, step=0.5,
        help="Talent Radar tries to auto-detect this from the JD text. If it "
             "can't find a clear phrasing (or you just want to set it "
             "yourself), enter it here — leave at 0 to keep auto-detection.",
    )

    st.divider()
    st.header("2. Resumes")
    resume_files = st.file_uploader(
        "Upload candidate resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    st.divider()
    st.header("3. Scoring Weights")
    st.caption("Adjust how much each factor contributes to the final score.")
    w_skills = st.slider("Skill match", 0, 100, 40)
    w_semantic = st.slider("Overall relevance", 0, 100, 30)
    w_experience = st.slider("Experience", 0, 100, 20)
    w_education = st.slider("Education", 0, 100, 10)
    total_w = max(w_skills + w_semantic + w_experience + w_education, 1)
    weights = {
        "skills": w_skills / total_w,
        "semantic": w_semantic / total_w,
        "experience": w_experience / total_w,
        "education": w_education / total_w,
    }

    st.divider()
    use_llm = st.toggle(
        "Use NVIDIA-hosted LLM for sharper interview questions",
        value=bool(os.environ.get("NVIDIA_API_KEY")),
        help="Requires an NVIDIA_API_KEY environment variable (integrate.api.nvidia.com). Falls back to built-in templates if unavailable.",
    )

    run_button = st.button("🚀 Screen Candidates", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------
if "results" not in st.session_state:
    st.session_state.results = None
    st.session_state.jd = None

if run_button:
    if not jd_text.strip():
        st.error("Please provide a job description first.")
    elif not resume_files:
        st.error("Please upload at least one resume.")
    else:
        with st.spinner("Reading resumes and scoring candidates..."):
            jd_text_clean = clean_text(jd_text)
            jd = parse_job_description(jd_text_clean, title_override=role_title_override)
            if min_experience_override > 0:
                jd.min_experience_years = min_experience_override

            evaluations = []
            for f in resume_files:
                text = extract_text(f)
                candidate = parse_resume(f.name, text)

                semantic_score = compute_semantic_similarity(candidate.raw_text, jd.raw_text)
                matched, missing, skill_pct = compute_skill_match(candidate.skills, jd.required_skills)
                experience_score = compute_experience_score(candidate.experience_years, jd.min_experience_years)
                education_score = compute_education_match(candidate.education, jd.required_education)

                overall = compute_overall_score(
                    semantic_score, skill_pct, experience_score, education_score, weights
                )

                evaluations.append({
                    "candidate": candidate,
                    "semantic_score": semantic_score,
                    "skill_score": skill_pct,
                    "experience_score": experience_score,
                    "education_score": education_score,
                    "overall_score": overall,
                    "matched_skills": matched,
                    "missing_skills": missing,
                })

            ranked = rank_candidates(evaluations)
            st.session_state.results = ranked
            st.session_state.jd = jd

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
results = st.session_state.results
jd = st.session_state.jd

if results:
    st.markdown(f"""
    <div class="tr-section-title"><div class="bar"></div><span>Results for: {jd.title}</span></div>
    """, unsafe_allow_html=True)

    metric_defs = [
        ("Candidates screened", len(results), VIOLET),
        ("Required skills detected", len(jd.required_skills), "#0EA5E9"),
        ("Min. experience", f"{jd.min_experience_years:g} yrs" if jd.min_experience_years else "Not specified", GOLD),
        ("Top score", f"{results[0]['overall_score']:.1f}", CORAL),
    ]
    meta_cols = st.columns(4)
    for col, (label, value, color) in zip(meta_cols, metric_defs):
        col.markdown(f"""
        <div class="tr-metric" style="background:{color}">
            <div class="num">{value}</div>
            <div class="lbl">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # --- Leaderboard chart, bars colored by fit tier ---
    names = [e["candidate"].name for e in results]
    scores = [e["overall_score"] for e in results]
    bar_colors = [suitability_color(s) for s in scores]
    fig = go.Figure(go.Bar(
        x=scores, y=names, orientation="h",
        marker_color=bar_colors,
        text=[f"{s:.1f}" for s in scores], textposition="outside",
    ))
    fig.update_layout(
        height=max(280, 42 * len(results)),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(range=[0, 108], title="Overall fit score", gridcolor=BORDER),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Helvetica Neue, sans-serif", color=INK),
    )
    st.plotly_chart(fig, use_container_width=True, key="tr_leaderboard_bar")

    # --- Colorful custom leaderboard cards (replaces the plain dataframe,
    #     which was rendering with invisible text under some themes) ---
    st.markdown("""
    <div class="tr-section-title" style="margin-top:0.4rem;"><div class="bar"></div><span>Candidate Ranking</span></div>
    """, unsafe_allow_html=True)

    for e in results:
        c = e["candidate"]
        accent = suitability_color(e["overall_score"])
        tier = suitability_label(e["overall_score"])
        missing_preview = ", ".join(sorted(e["missing_skills"])[:4]) if e["missing_skills"] else "None 🎉"
        if e["missing_skills"] and len(e["missing_skills"]) > 4:
            missing_preview += f" +{len(e['missing_skills']) - 4} more"
        st.markdown(f"""
        <div class="tr-lead-card" style="--accent:{accent}">
            <div class="tr-lead-rank" style="--accent:{accent}">{e['rank']}</div>
            <div style="min-width:190px;">
                <div class="tr-lead-name">{c.name}</div>
                <div class="tr-lead-email">{c.email or 'no email found'}</div>
            </div>
            <span class="tr-fit-badge" style="background:{accent}; min-width:96px; text-align:center;">{tier}</span>
            <div class="tr-lead-bar-track"><div class="tr-lead-bar-fill" style="width:{min(e['overall_score'],100)}%; --accent:{accent}"></div></div>
            <div class="tr-lead-score">{e['overall_score']:.1f}</div>
            <div style="min-width:150px; max-width:220px;">
                <div class="tr-label" style="margin-bottom:0.1rem;">Missing skills</div>
                <div class="tr-lead-missing">{missing_preview}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- CSV export (kept as a full data table, download only) ---
    df = pd.DataFrame([{
        "Rank": e["rank"],
        "Candidate": e["candidate"].name,
        "Email": e["candidate"].email,
        "Overall Score": e["overall_score"],
        "Fit": suitability_label(e["overall_score"]),
        "Skill Match %": e["skill_score"],
        "Relevance %": e["semantic_score"],
        "Experience (yrs)": e["candidate"].experience_years,
        "Missing Skills": ", ".join(sorted(e["missing_skills"])) if e["missing_skills"] else "—",
    } for e in results])

    st.write("")
    st.download_button(
        "⬇️ Download results as CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="candidate_ranking.csv",
        mime="text/csv",
    )

    st.divider()
    st.markdown("""
    <div class="tr-section-title"><div class="bar"></div><span>Candidate Detail & Interview Questions</span></div>
    """, unsafe_allow_html=True)

    for e in results:
        candidate = e["candidate"]
        tier = suitability_label(e["overall_score"])
        tier_color = suitability_color(e["overall_score"])
        rank_color = GOLD if e["rank"] == 1 else (VIOLET if e["rank"] <= 3 else MUTED)

        header = (
            f"<span class='tr-rank-badge' style='background:{rank_color}'>#{e['rank']}</span>"
            f"<b>{candidate.name}</b> &nbsp; "
            f"<span class='tr-fit-badge' style='background:{tier_color}'>{tier} · {e['overall_score']:.1f}</span>"
        )

        with st.expander(f"#{e['rank']} — {candidate.name}  ·  {tier}  ·  Score {e['overall_score']:.1f}"):
            st.markdown(header, unsafe_allow_html=True)
            st.write("")

            gauge_cols = st.columns(4)
            gauge_defs = [
                ("Skill match", e["skill_score"], "#0EA5E9"),
                ("Relevance", e["semantic_score"], VIOLET),
                ("Experience", e["experience_score"], "#16A34A"),
                ("Education", e["education_score"], GOLD),
            ]
            for col, (label, value, color) in zip(gauge_cols, gauge_defs):
                gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=value,
                    number={"suffix": "%", "font": {"size": 20, "color": INK}},
                    gauge={
                        "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": BORDER},
                        "bar": {"color": color},
                        "bgcolor": "white",
                        "borderwidth": 0,
                    },
                    title={"text": label, "font": {"size": 13, "color": MUTED}},
                ))
                gauge.update_layout(height=150, margin=dict(l=15, r=15, t=35, b=5))
                col.plotly_chart(
                    gauge,
                    use_container_width=True,
                    key=f"gauge_{e['rank']}_{candidate.name}_{label}",
                )

            contact_cols = st.columns(3)
            contact_cols[0].markdown(f"<span class='tr-label'>Email</span><br><b>{candidate.email or 'n/a'}</b>", unsafe_allow_html=True)
            contact_cols[1].markdown(f"<span class='tr-label'>Phone</span><br><b>{candidate.phone or 'n/a'}</b>", unsafe_allow_html=True)
            contact_cols[2].markdown(f"<span class='tr-label'>Education</span><br><b>{', '.join(candidate.education) or 'n/a'}</b>", unsafe_allow_html=True)

            st.write("")
            st.markdown("**✅ Matched skills**")
            if e["matched_skills"]:
                st.markdown(
                    "".join(skill_pill_html(s) for s in sorted(e["matched_skills"])),
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No overlapping skills detected.")

            st.markdown("**⚠️ Skill gaps**")
            if e["missing_skills"]:
                st.markdown(
                    "".join(f"<span class='tr-skill-pill-missing'>{s}</span>" for s in sorted(e["missing_skills"])),
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No gaps against the JD's required skills.")

            st.write("")
            st.markdown("**💬 Suggested interview questions**")
            questions = generate_questions(
                candidate.name, jd.title, e["matched_skills"], e["missing_skills"], use_llm=use_llm
            )
            type_class = {
                "Technical": "tr-question",
                "Skill Gap": "tr-question tr-question-gap",
                "Behavioral": "tr-question tr-question-behavioral",
            }
            for q in questions:
                css_class = type_class.get(q["type"], "tr-question")
                st.markdown(
                    f"<div class='{css_class}'><b>[{q['type']}]</b> {q['question']}</div>",
                    unsafe_allow_html=True,
                )

            with st.popover("📄 View extracted resume text"):
                st.text(candidate.raw_text[:4000])

else:
    st.info("Add a job description and resumes in the sidebar, then click **🚀 Screen Candidates** to get started.")

    feature_cols = st.columns(4)
    feature_defs = [
        ("🧠", "Smart Parsing", "Extracts skills, experience & education from PDF, DOCX or TXT resumes.", VIOLET),
        ("🎯", "Precision Matching", "TF-IDF relevance + explicit skill overlap against the job description.", "#0EA5E9"),
        ("🕳️", "Skill Gap Detection", "Flags exactly what's missing so interviewers know what to probe.", CORAL),
        ("💬", "Interview Prep", "Drafts technical, gap-probing & behavioral questions per candidate.", GOLD),
    ]
    for col, (icon, title, desc, color) in zip(feature_cols, feature_defs):
        col.markdown(f"""
        <div class="tr-card" style="border-top: 4px solid {color};">
            <div style="font-size:1.6rem;">{icon}</div>
            <div style="font-weight:700; color:{INK}; margin-top:0.3rem;">{title}</div>
            <div class="tr-label" style="margin-top:0.3rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
