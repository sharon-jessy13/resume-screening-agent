"""
ranker.py
Combines extraction + scoring results into a ranked shortlist, with a
human-readable reasoning string generated deterministically (no extra LLM
call) so every score is fully auditable.
"""


def _build_reasoning(score_info: dict) -> str:
    matched = score_info["matched_skills"]
    missing = score_info["missing_skills"]

    parts = []

    if matched:
        shown = ", ".join(matched[:6])
        extra = f" (+{len(matched) - 6} more)" if len(matched) > 6 else ""
        parts.append(f"Matches {len(matched)} required skill(s): {shown}{extra}.")
    else:
        parts.append("No direct overlap with the required skill list.")

    if missing:
        shown = ", ".join(missing[:6])
        extra = f" (+{len(missing) - 6} more)" if len(missing) > 6 else ""
        parts.append(f"Missing: {shown}{extra}.")

    if score_info["meets_experience_requirement"]:
        parts.append(f"Meets experience requirement ({score_info['years_experience']} yrs).")
    else:
        parts.append(f"Below required experience (has {score_info['years_experience']} yrs).")

    parts.append(
        f"Semantic fit {score_info['semantic_score']}%, "
        f"skill overlap {score_info['skill_overlap_score']}%."
    )

    return " ".join(parts)


def rank_candidates(results: list) -> list:
    """
    results: list of dicts, each containing at least:
      { "filename": ..., "resume_fields": {...}, "score_info": {...} }

    Returns the same list, sorted descending by final_score, with a
    "reasoning" and "rank" field added.
    """
    for r in results:
        r["reasoning"] = _build_reasoning(r["score_info"])

    ranked = sorted(results, key=lambda r: r["score_info"]["final_score"], reverse=True)

    for i, r in enumerate(ranked, start=1):
        r["rank"] = i

    return ranked
