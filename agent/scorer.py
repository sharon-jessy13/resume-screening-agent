"""
scorer.py
Computes a relevance score between a resume and a JD using two real,
explainable signals:

1. Semantic similarity  - cosine similarity between Gemini embeddings
                           of the resume summary and the JD summary
2. Skill overlap         - fraction of JD-required skills present in
                           the candidate's extracted skill list

final_score = 0.7 * semantic + 0.3 * overlap   (0-100 scale)

Weights are configurable via SEMANTIC_WEIGHT / OVERLAP_WEIGHT below.
"""

import numpy as np
import google.generativeai as genai

EMBEDDING_MODEL = "models/gemini-embedding-2"
SEMANTIC_WEIGHT = 0.7
OVERLAP_WEIGHT = 0.3


def _embed(text: str) -> np.ndarray:
    result = genai.embed_content(model=EMBEDDING_MODEL, content=text)
    return np.array(result["embedding"])


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _skill_overlap(resume_skills: list, required_skills: list) -> tuple:
    """Returns (overlap_ratio, matched_skills, missing_skills)."""
    resume_set = set(s.lower().strip() for s in resume_skills)
    required_set = set(s.lower().strip() for s in required_skills)

    if not required_set:
        return 0.0, [], []

    matched = sorted(resume_set & required_set)
    missing = sorted(required_set - resume_set)
    ratio = len(matched) / len(required_set)
    return ratio, matched, missing


def score_resume(resume_fields: dict, jd_fields: dict) -> dict:
    resume_summary = resume_fields.get("summary") or ""
    jd_summary = jd_fields.get("summary") or ""

    # Fall back to skill list text if summary is empty, so embedding still works
    if not resume_summary.strip():
        resume_summary = ", ".join(resume_fields.get("skills", []))
    if not jd_summary.strip():
        jd_summary = ", ".join(jd_fields.get("required_skills", []))

    resume_vec = _embed(resume_summary)
    jd_vec = _embed(jd_summary)
    semantic_score = max(0.0, _cosine_similarity(resume_vec, jd_vec))  # clip negatives

    overlap_ratio, matched, missing = _skill_overlap(
        resume_fields.get("skills", []),
        jd_fields.get("required_skills", []),
    )

    final = (SEMANTIC_WEIGHT * semantic_score + OVERLAP_WEIGHT * overlap_ratio) * 100

    exp_candidate = resume_fields.get("years_experience", 0) or 0
    exp_required = jd_fields.get("min_years_experience", 0) or 0
    meets_experience = exp_candidate >= exp_required

    return {
        "final_score": round(final, 2),
        "semantic_score": round(semantic_score * 100, 2),
        "skill_overlap_score": round(overlap_ratio * 100, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "years_experience": exp_candidate,
        "meets_experience_requirement": meets_experience,
    }
