"""
ranker.py

Ranks candidates using the deterministic final score.

No Gemini calls are made here.
"""


def _build_reasoning(
    score_info: dict
) -> str:

    matched = score_info.get(
        "matched_skills",
        []
    )

    missing = score_info.get(
        "missing_skills",
        []
    )

    parts = []

    # --------------------------------------------------------
    # Matched skills
    # --------------------------------------------------------

    if matched:

        shown = ", ".join(
            matched[:6]
        )

        extra = ""

        if len(matched) > 6:

            extra = (
                f" (+{len(matched) - 6} more)"
            )

        parts.append(
            f"Matches {len(matched)} "
            f"required skill(s): "
            f"{shown}{extra}."
        )

    else:

        parts.append(
            "No direct overlap with "
            "the required skill list."
        )

    # --------------------------------------------------------
    # Missing skills
    # --------------------------------------------------------

    if missing:

        shown = ", ".join(
            missing[:6]
        )

        extra = ""

        if len(missing) > 6:

            extra = (
                f" (+{len(missing) - 6} more)"
            )

        parts.append(
            f"Missing: "
            f"{shown}{extra}."
        )

    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    years = score_info.get(
        "years_experience",
        0
    )

    required = score_info.get(
        "required_experience",
        0
    )

    if score_info.get(
        "meets_experience_requirement",
        False
    ):

        if required > 0:

            parts.append(
                f"Meets experience requirement "
                f"({years} yrs vs {required} yrs required)."
            )

        else:

            parts.append(
                f"Experience: {years} yrs."
            )

    else:

        parts.append(
            f"Below required experience "
            f"({years} yrs vs {required} yrs required)."
        )

    # --------------------------------------------------------
    # Score breakdown
    # --------------------------------------------------------

    parts.append(
        f"Skill score "
        f"{score_info.get('skill_score', 0)}%, "
        f"experience score "
        f"{score_info.get('experience_score', 0)}%, "
        f"education score "
        f"{score_info.get('education_score', 0)}%."
    )

    return " ".join(parts)


def rank_candidates(
    results: list
) -> list:

    for result in results:

        result["reasoning"] = _build_reasoning(
            result["score_info"]
        )

    # Highest score first
    ranked = sorted(
        results,
        key=lambda result:
            result["score_info"].get(
                "final_score",
                0
            ),
        reverse=True
    )

    # Add rank
    for index, result in enumerate(
        ranked,
        start=1
    ):

        result["rank"] = index

    return ranked