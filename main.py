"""
main.py

Resume Screening Agent

Pipeline:

1. Read JD
2. Read all PDF resumes
3. Send JD + ALL resumes to Gemini in ONE request
4. Extract candidate information
5. Score candidates deterministically
6. Rank candidates
7. Save JSON
8. Save CSV
"""


import os
import json
import csv
import argparse

from pypdf import PdfReader

from agent.extractor import (
    extract_all_resume_fields
)

from agent.scorer import (
    score_resume
)

from agent.ranker import (
    rank_candidates
)


# ============================================================
# DEFAULT PATHS
# ============================================================

DEFAULT_JD = "data/jd.txt"

DEFAULT_RESUMES = "data/resumes"

DEFAULT_OUTPUT = "output"


# ============================================================
# READ TEXT FILE
# ============================================================

def read_text_file(
    path: str
) -> str:

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ============================================================
# READ PDF
# ============================================================

def extract_pdf_text(
    pdf_path: str
) -> str:

    text_parts = []

    try:

        reader = PdfReader(
            pdf_path
        )

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text_parts.append(
                    page_text
                )

        return "\n".join(
            text_parts
        )

    except Exception as e:

        print(
            f"[ERROR] Could not read "
            f"{os.path.basename(pdf_path)}: {e}"
        )

        return ""


# ============================================================
# LOAD RESUMES
# ============================================================

def load_resumes(
    resumes_dir: str
) -> list:

    if not os.path.exists(
        resumes_dir
    ):

        raise FileNotFoundError(
            f"Resume directory not found: "
            f"{resumes_dir}"
        )

    resumes = []

    files = sorted(
        os.listdir(
            resumes_dir
        )
    )

    for filename in files:

        if not filename.lower().endswith(
            ".pdf"
        ):
            continue

        pdf_path = os.path.join(
            resumes_dir,
            filename
        )

        print(
            f"Reading {filename} ..."
        )

        text = extract_pdf_text(
            pdf_path
        )

        if not text.strip():

            print(
                "  -> WARNING: No text extracted"
            )

            continue

        resumes.append({

            "filename": filename,

            "text": text

        })

        print(
            f"  -> Extracted "
            f"{len(text)} characters"
        )

    return resumes


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    results: list,
    output_path: str
):

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        "\nJSON saved:"
    )

    print(
        os.path.abspath(
            output_path
        )
    )


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(
    results: list,
    output_path: str
):

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(
            file
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        writer.writerow([

            "Rank",

            "Candidate",

            "Filename",

            "Final Score (%)",

            "Skill Score (%)",

            "Experience Score (%)",

            "Education Score (%)",

            "Years Experience",

            "Required Experience",

            "Meets Experience",

            "Matched Skills",

            "Missing Skills",

            "Reasoning"

        ])

        # ----------------------------------------------------
        # ROWS
        # ----------------------------------------------------

        for result in results:

            resume_fields = result.get(
                "resume_fields",
                {}
            )

            score_info = result.get(
                "score_info",
                {}
            )

            writer.writerow([

                result.get(
                    "rank",
                    ""
                ),

                resume_fields.get(
                    "name",
                    "Unknown"
                ),

                result.get(
                    "filename",
                    ""
                ),

                score_info.get(
                    "final_score",
                    0
                ),

                score_info.get(
                    "skill_score",
                    0
                ),

                score_info.get(
                    "experience_score",
                    0
                ),

                score_info.get(
                    "education_score",
                    0
                ),

                score_info.get(
                    "years_experience",
                    0
                ),

                score_info.get(
                    "required_experience",
                    0
                ),

                score_info.get(
                    "meets_experience_requirement",
                    False
                ),

                ", ".join(
                    score_info.get(
                        "matched_skills",
                        []
                    )
                ),

                ", ".join(
                    score_info.get(
                        "missing_skills",
                        []
                    )
                ),

                result.get(
                    "reasoning",
                    ""
                )

            ])


    print(
        "\nCSV saved:"
    )

    print(
        os.path.abspath(
            output_path
        )
    )


# ============================================================
# RUN SCREENING
# ============================================================

def run(
    jd_path: str = DEFAULT_JD,
    resumes_dir: str = DEFAULT_RESUMES,
    out_dir: str = DEFAULT_OUTPUT
):

    print()
    print(
        "=" * 70
    )

    print(
        "RESUME SCREENING AGENT"
    )

    print(
        "=" * 70
    )

    # ========================================================
    # STEP 1 — LOAD JD
    # ========================================================

    print(
        "\nLoading JD from "
        f"{jd_path} ..."
    )

    jd_text = read_text_file(
        jd_path
    )

    if not jd_text.strip():

        print(
            "[ERROR] Job description is empty."
        )

        return


    # ========================================================
    # STEP 2 — LOAD RESUMES
    # ========================================================

    print(
        "\nLoading resumes from "
        f"{resumes_dir} ..."
    )

    resumes = load_resumes(
        resumes_dir
    )

    print(
        f"\n-> Found "
        f"{len(resumes)} resume(s)"
    )

    if not resumes:

        print(
            "[ERROR] No PDF resumes found."
        )

        return


    # ========================================================
    # STEP 3 — ONE GEMINI REQUEST
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "GEMINI BATCH EXTRACTION"
    )

    print(
        "=" * 70
    )

    try:

        # IMPORTANT:
        #
        # extractor.py expects:
        #
        # extract_all_resume_fields(
        #     jd_text,
        #     resumes
        # )
        #
        # This sends JD + ALL resumes
        # in ONE Gemini request.

        jd_fields, resume_candidates = (
            extract_all_resume_fields(
                jd_text,
                resumes
            )
        )

    except Exception as e:

        print(
            "\n[ERROR] Resume batch extraction failed:"
        )

        print(e)

        return


    # ========================================================
    # CHECK GEMINI RESULT
    # ========================================================

    print(
        "\n-> Gemini extraction completed."
    )

    print(
        "-> Role: "
        f"{jd_fields.get('title', 'Unknown')}"
    )

    print(
        "-> Required skills: "
        f"{jd_fields.get('required_skills', [])}"
    )

    print(
        "-> Minimum experience: "
        f"{jd_fields.get('min_years_experience', 0)} years"
    )

    print(
        "-> Candidates extracted: "
        f"{len(resume_candidates)}"
    )


    # ========================================================
    # CREATE LOOKUP
    # ========================================================

    resume_fields_map = {}

    for candidate in resume_candidates:

        filename = candidate.get(
            "filename"
        )

        if filename:

            resume_fields_map[
                filename
            ] = candidate


    # ========================================================
    # STEP 4 — SCORE
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "SCORING CANDIDATES"
    )

    print(
        "=" * 70
    )

    results = []


    for resume in resumes:

        filename = resume[
            "filename"
        ]

        print(
            f"\nProcessing {filename} ..."
        )

        # ----------------------------------------------------
        # Find Gemini extraction
        # ----------------------------------------------------

        resume_fields = resume_fields_map.get(
            filename
        )

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        if not resume_fields:

            print(
                "  -> WARNING: Candidate was "
                "not returned by Gemini."
            )

            resume_fields = {

                "filename": filename,

                "name": None,

                "skills": [],

                "years_experience": 0,

                "education": None,

                "summary": ""
            }


        # ----------------------------------------------------
        # Deterministic scoring
        # ----------------------------------------------------

        try:

            score_info = score_resume(
                resume_fields,
                jd_fields
            )

        except Exception as e:

            print(
                f"  -> Scoring error: {e}"
            )

            score_info = {

                "final_score": 0,

                "skill_score": 0,

                "experience_score": 0,

                "education_score": 0,

                "skill_overlap_score": 0,

                "semantic_score": 0,

                "matched_skills": [],

                "missing_skills":
                    jd_fields.get(
                        "required_skills",
                        []
                    ),

                "years_experience": 0,

                "required_experience":
                    jd_fields.get(
                        "min_years_experience",
                        0
                    ),

                "meets_experience_requirement":
                    False
            }


        # ----------------------------------------------------
        # Print score
        # ----------------------------------------------------

        print(
            f"  -> Score: "
            f"{score_info['final_score']:.2f}%"
        )

        print(
            f"  -> Skills: "
            f"{score_info['skill_score']:.2f}%"
        )

        print(
            f"  -> Experience: "
            f"{score_info['experience_score']:.2f}%"
        )

        print(
            f"  -> Education: "
            f"{score_info['education_score']:.2f}%"
        )


        # ----------------------------------------------------
        # Store
        # ----------------------------------------------------

        results.append({

            "filename": filename,

            "resume_fields": resume_fields,

            "score_info": score_info

        })


    # ========================================================
    # STEP 5 — RANK
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "RANKING CANDIDATES"
    )

    print(
        "=" * 70
    )

    ranked_results = rank_candidates(
        results
    )


    # ========================================================
    # STEP 6 — OUTPUT DIRECTORY
    # ========================================================

    os.makedirs(
        out_dir,
        exist_ok=True
    )


    # ========================================================
    # STEP 7 — SAVE JSON
    # ========================================================

    json_path = os.path.join(
        out_dir,
        "ranked_candidates.json"
    )

    save_json(
        ranked_results,
        json_path
    )


    # ========================================================
    # STEP 8 — SAVE CSV
    # ========================================================

    csv_path = os.path.join(
        out_dir,
        "ranked_candidates.csv"
    )

    save_csv(
        ranked_results,
        csv_path
    )


    # ========================================================
    # STEP 9 — FINAL RESULTS
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL RANKING"
    )

    print(
        "=" * 70
    )


    for candidate in ranked_results:

        rank = candidate.get(
            "rank",
            0
        )

        filename = candidate.get(
            "filename",
            ""
        )

        resume_fields = candidate.get(
            "resume_fields",
            {}
        )

        score_info = candidate.get(
            "score_info",
            {}
        )

        name = resume_fields.get(
            "name"
        )

        if not name:

            name = "Unknown Candidate"


        print(
            f"\n#{rank} {name}"
        )

        print(
            f"   File: {filename}"
        )

        print(
            f"   Final Score: "
            f"{score_info.get('final_score', 0):.2f}%"
        )

        print(
            f"   Skills: "
            f"{score_info.get('skill_score', 0):.2f}%"
        )

        print(
            f"   Experience: "
            f"{score_info.get('experience_score', 0):.2f}%"
        )

        print(
            f"   Education: "
            f"{score_info.get('education_score', 0):.2f}%"
        )

        print(
            f"   Matched Skills: "
            f"{', '.join(score_info.get('matched_skills', []))}"
        )

        print(
            f"   Missing Skills: "
            f"{', '.join(score_info.get('missing_skills', []))}"
        )


    # ========================================================
    # DONE
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "SCREENING COMPLETED SUCCESSFULLY"
    )

    print(
        "=" * 70
    )

    print(
        "\nOutput files:"
    )

    print(
        f"JSON: {os.path.abspath(json_path)}"
    )

    print(
        f"CSV : {os.path.abspath(csv_path)}"
    )

    print(
        f"\nTotal resumes processed: "
        f"{len(resumes)}"
    )


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="AI Resume Screening Agent"
    )

    parser.add_argument(
        "--jd",
        default=DEFAULT_JD
    )

    parser.add_argument(
        "--resumes",
        default=DEFAULT_RESUMES
    )

    parser.add_argument(
        "--out",
        default=DEFAULT_OUTPUT
    )

    args = parser.parse_args()

    run(
        jd_path=args.jd,
        resumes_dir=args.resumes,
        out_dir=args.out
    )