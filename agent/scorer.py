"""
scorer.py

Deterministic resume scoring.

The score does NOT call Gemini.

This means the same resume + same JD
will produce the same percentage every run.

Scoring:

    Skill Match       = 60%
    Experience Match  = 25%
    Education Match   = 15%

Final score = weighted total
"""

import re


# ============================================================
# WEIGHTS
# ============================================================

SKILL_WEIGHT = 0.60
EXPERIENCE_WEIGHT = 0.25
EDUCATION_WEIGHT = 0.15


# ============================================================
# NORMALIZE TEXT
# ============================================================

def _normalize(text: str) -> str:

    if not text:
        return ""

    text = text.lower().strip()

    # Normalize common variations
    replacements = {
        "reactjs": "react",
        "react.js": "react",
        "node.js": "node js",
        "nodejs": "node js",
        "typescript.js": "typescript",
        "rest apis": "rest api",
        "restful apis": "rest api",
        "restful api": "rest api",
        "html5": "html",
        "css3": "css",
        "web sockets": "websockets",
        "ci cd": "ci/cd",
        "cicd": "ci/cd",
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new
        )

    # Remove punctuation except slash
    text = re.sub(
        r"[^a-z0-9+#./ -]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# NORMALIZE SKILL
# ============================================================

def _normalize_skill(
    skill: str
) -> str:

    return _normalize(skill)


# ============================================================
# SKILL OVERLAP
# ============================================================

def _skill_overlap(
    resume_skills: list,
    required_skills: list
):

    resume_set = {
        _normalize_skill(skill)
        for skill in resume_skills
        if skill
    }

    required_set = {
        _normalize_skill(skill)
        for skill in required_skills
        if skill
    }

    resume_set.discard("")
    required_set.discard("")

    if not required_set:

        return 0.0, [], []

    matched = sorted(
        resume_set.intersection(
            required_set
        )
    )

    missing = sorted(
        required_set.difference(
            resume_set
        )
    )

    ratio = (
        len(matched) /
        len(required_set)
    )

    return (
        ratio,
        matched,
        missing
    )


# ============================================================
# EXPERIENCE SCORE
# ============================================================

def _experience_score(
    candidate_years,
    required_years
):

    candidate_years = float(
        candidate_years or 0
    )

    required_years = float(
        required_years or 0
    )

    # If JD does not specify experience,
    # don't penalize candidates.
    if required_years <= 0:

        return 1.0

    if candidate_years >= required_years:

        return 1.0

    # Partial credit
    score = (
        candidate_years /
        required_years
    )

    return max(
        0.0,
        min(
            score,
            1.0
        )
    )


# ============================================================
# EDUCATION SCORE
# ============================================================

def _education_score(
    education: str
):

    if not education:

        return 0.0

    education = _normalize(
        education
    )

    # Basic education hierarchy
    if any(
        word in education
        for word in [
            "phd",
            "doctorate"
        ]
    ):

        return 1.0

    if any(
        word in education
        for word in [
            "master",
            "m.tech",
            "mtech",
            "mca",
            "mba",
            "msc",
            "m.sc"
        ]
    ):

        return 1.0

    if any(
        word in education
        for word in [
            "bachelor",
            "b.e",
            "be ",
            "btech",
            "b.tech",
            "bca",
            "bsc",
            "b.sc"
        ]
    ):

        return 0.90

    if any(
        word in education
        for word in [
            "diploma"
        ]
    ):

        return 0.70

    return 0.50


# ============================================================
# SCORE RESUME
# ============================================================

def score_resume(
    resume_fields: dict,
    jd_fields: dict
) -> dict:

    resume_skills = resume_fields.get(
        "skills",
        []
    ) or []

    required_skills = jd_fields.get(
        "required_skills",
        []
    ) or []

    # --------------------------------------------------------
    # Skill score
    # --------------------------------------------------------

    skill_ratio, matched, missing = _skill_overlap(
        resume_skills,
        required_skills
    )

    skill_score = skill_ratio * 100

    # --------------------------------------------------------
    # Experience score
    # --------------------------------------------------------

    candidate_years = resume_fields.get(
        "years_experience",
        0
    ) or 0

    required_years = jd_fields.get(
        "min_years_experience",
        0
    ) or 0

    experience_ratio = _experience_score(
        candidate_years,
        required_years
    )

    experience_score = (
        experience_ratio * 100
    )

    # --------------------------------------------------------
    # Education score
    # --------------------------------------------------------

    education_ratio = _education_score(
        resume_fields.get(
            "education"
        )
    )

    education_score = (
        education_ratio * 100
    )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    final_score = (
        SKILL_WEIGHT *
        skill_ratio
        +
        EXPERIENCE_WEIGHT *
        experience_ratio
        +
        EDUCATION_WEIGHT *
        education_ratio
    ) * 100

    meets_experience = (
        candidate_years >=
        required_years
    )

    return {

        "final_score": round(
            final_score,
            2
        ),

        "skill_score": round(
            skill_score,
            2
        ),

        "experience_score": round(
            experience_score,
            2
        ),

        "education_score": round(
            education_score,
            2
        ),

        "skill_overlap_score": round(
            skill_score,
            2
        ),

        "semantic_score": 0,

        "matched_skills": matched,

        "missing_skills": missing,

        "years_experience": candidate_years,

        "required_experience": required_years,

        "meets_experience_requirement":
            meets_experience
    }