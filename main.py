"""
main.py
Resume Screening Agent - CLI entry point.

Usage:
    python main.py --jd data/jd.txt --resumes data/resumes --out output

See README.md for full setup instructions.
"""

import os
import json
import argparse
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

from agent.parser import extract_text, load_resumes
from agent.extractor import extract_resume_fields, extract_jd_fields
from agent.scorer import score_resume
from agent.ranker import rank_candidates


def configure_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Copy .env.example to .env and add your key."
        )
    genai.configure(api_key=api_key)


def run(jd_path: str, resumes_dir: str, out_dir: str):
    configure_gemini()
    os.makedirs(out_dir, exist_ok=True)

    print(f"Loading JD from {jd_path} ...")
    jd_text = extract_text(jd_path)
    jd_fields = extract_jd_fields(jd_text)
    print(f"  -> Role: {jd_fields.get('title')}")
    print(f"  -> Required skills: {jd_fields.get('required_skills')}")

    print(f"\nLoading resumes from {resumes_dir} ...")
    resumes = load_resumes(resumes_dir)
    print(f"  -> Found {len(resumes)} resume(s)")

    results = []
    for fname, text in resumes.items():
        print(f"\nProcessing {fname} ...")
        resume_fields = extract_resume_fields(text)
        score_info = score_resume(resume_fields, jd_fields)
        results.append({
            "filename": fname,
            "candidate_name": resume_fields.get("name") or fname,
            "resume_fields": resume_fields,
            "score_info": score_info,
        })
        print(f"  -> Score: {score_info['final_score']}")

    ranked = rank_candidates(results)

    # --- Write JSON output ---
    json_path = os.path.join(out_dir, "ranked_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"job_description": jd_fields, "candidates": ranked}, f, indent=2)

    # --- Write CSV output ---
    csv_rows = []
    for r in ranked:
        csv_rows.append({
            "rank": r["rank"],
            "filename": r["filename"],
            "candidate_name": r["candidate_name"],
            "final_score": r["score_info"]["final_score"],
            "semantic_score": r["score_info"]["semantic_score"],
            "skill_overlap_score": r["score_info"]["skill_overlap_score"],
            "years_experience": r["score_info"]["years_experience"],
            "meets_experience_requirement": r["score_info"]["meets_experience_requirement"],
            "matched_skills": ", ".join(r["score_info"]["matched_skills"]),
            "missing_skills": ", ".join(r["score_info"]["missing_skills"]),
            "reasoning": r["reasoning"],
        })
    csv_path = os.path.join(out_dir, "ranked_results.csv")
    pd.DataFrame(csv_rows).to_csv(csv_path, index=False)

    print(f"\nDone. Wrote:\n  {json_path}\n  {csv_path}")
    print("\n=== SHORTLIST ===")
    for r in ranked:
        print(f"{r['rank']}. {r['candidate_name']} — {r['score_info']['final_score']}/100")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume Screening Agent")
    parser.add_argument("--jd", default="data/jd.txt", help="Path to job description file")
    parser.add_argument("--resumes", default="data/resumes", help="Folder of resumes")
    parser.add_argument("--out", default="output", help="Output folder")
    args = parser.parse_args()

    run(args.jd, args.resumes, args.out)
