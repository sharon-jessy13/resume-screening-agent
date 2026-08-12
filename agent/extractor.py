"""
extractor.py

Batch resume extraction using the Google GenAI SDK.

Features:
- Sends JD + ALL resumes in ONE Gemini request
- Uses structured JSON output
- Compatible with google-genai SDK
- Handles temporary 429 / 503 errors
- Does not use ["string", "null"] schema types
- Returns one candidate for every supplied resume
"""

import os
import json
import time

from dotenv import load_dotenv
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. "
        "Please check your .env file."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=API_KEY)


# ============================================================
# MODEL
# ============================================================

MODEL = "gemini-3.6-flash"


# ============================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================

# IMPORTANT:
#
# DO NOT use:
#
# "type": ["STRING", "NULL"]
#
# The current SDK rejects that format.
#
# Instead, name and education are STRING.
# If information is unavailable, Gemini returns "".

RESPONSE_SCHEMA = {
    "type": "OBJECT",

    "properties": {

        # ----------------------------------------------------
        # JOB
        # ----------------------------------------------------

        "job": {
            "type": "OBJECT",

            "properties": {

                "title": {
                    "type": "STRING"
                },

                "required_skills": {
                    "type": "ARRAY",
                    "items": {
                        "type": "STRING"
                    }
                },

                "min_years_experience": {
                    "type": "NUMBER"
                },

                "summary": {
                    "type": "STRING"
                }
            },

            "required": [
                "title",
                "required_skills",
                "min_years_experience",
                "summary"
            ]
        },

        # ----------------------------------------------------
        # CANDIDATES
        # ----------------------------------------------------

        "candidates": {
            "type": "ARRAY",

            "items": {

                "type": "OBJECT",

                "properties": {

                    "filename": {
                        "type": "STRING"
                    },

                    "name": {
                        "type": "STRING"
                    },

                    "skills": {
                        "type": "ARRAY",
                        "items": {
                            "type": "STRING"
                        }
                    },

                    "years_experience": {
                        "type": "NUMBER"
                    },

                    "education": {
                        "type": "STRING"
                    },

                    "summary": {
                        "type": "STRING"
                    }
                },

                "required": [
                    "filename",
                    "name",
                    "skills",
                    "years_experience",
                    "education",
                    "summary"
                ]
            }
        }
    },

    "required": [
        "job",
        "candidates"
    ]
}


# ============================================================
# JSON CLEANER
# ============================================================

def _clean_json(text: str) -> dict:
    """
    Convert Gemini response text into a Python dictionary.
    """

    if not text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    text = text.strip()

    # Remove markdown code fences if Gemini returns them.
    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Find JSON object if extra text exists.
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "Could not find JSON object in Gemini response."
        )

    text = text[start:end + 1]

    return json.loads(text)


# ============================================================
# RETRY FUNCTION
# ============================================================

def _call_gemini_with_retry(
    prompt: str,
    max_retries: int = 3
):
    """
    Calls Gemini and retries temporary server/rate-limit errors.

    429 -> quota/rate limit
    503 -> temporary server overload
    """

    for attempt in range(1, max_retries + 1):

        try:

            print(
                f"[Gemini attempt {attempt}/{max_retries}]"
            )

            response = client.models.generate_content(

                model=MODEL,

                contents=prompt,

                config={
                    "response_mime_type": "application/json",
                    "response_schema": RESPONSE_SCHEMA,
                }
            )

            return response

        except Exception as e:

            error_text = str(e)

            is_retryable = (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "503" in error_text
                or "UNAVAILABLE" in error_text
                or "temporarily" in error_text.lower()
                or "high demand" in error_text.lower()
                or "Server disconnected" in error_text
            )

            if not is_retryable:

                print(
                    "\n[ERROR] Non-retryable Gemini error:"
                )

                raise

            if attempt == max_retries:

                print(
                    "\n[ERROR] Gemini failed after "
                    f"{max_retries} attempts."
                )

                raise

            # Increasing wait time
            wait_time = 5 * attempt

            print(
                f"\n[Gemini temporary error]"
                f"\nWaiting {wait_time} seconds "
                f"before retry..."
            )

            time.sleep(wait_time)

    raise RuntimeError(
        "Gemini request failed."
    )


# ============================================================
# BATCH EXTRACTION
# ============================================================

def extract_all_resume_fields(
    jd_text: str,
    resumes: list
) -> tuple:
    """
    Send the JD and ALL resumes to Gemini in ONE request.

    Parameters
    ----------
    jd_text : str
        Job description text.

    resumes : list
        Example:

        [
            {
                "filename": "resume1.pdf",
                "text": "resume text..."
            },
            {
                "filename": "resume2.pdf",
                "text": "resume text..."
            }
        ]

    Returns
    -------
    tuple

        (
            jd_fields,
            candidate_fields
        )
    """

    if not resumes:

        raise ValueError(
            "No resumes were supplied."
        )


    # ========================================================
    # BUILD RESUME BLOCKS
    # ========================================================

    resume_blocks = []

    for index, resume in enumerate(
        resumes,
        start=1
    ):

        filename = resume.get(
            "filename",
            f"resume_{index}.pdf"
        )

        resume_text = resume.get(
            "text",
            ""
        )

        resume_blocks.append(
            f"""
================ RESUME {index} ================

FILENAME:
{filename}

RESUME TEXT:
{resume_text[:12000]}

==================================================
"""
        )


    all_resumes_text = "\n".join(
        resume_blocks
    )


    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are an AI resume screening and information extraction engine.

You are given:

1. ONE JOB DESCRIPTION
2. MULTIPLE RESUMES

Your task is to analyze the job description and EVERY resume.

IMPORTANT:
- Process every resume.
- Do not skip any resume.
- Do not merge candidates.
- Do not duplicate candidates.
- Keep the exact filename supplied for every resume.
- The number of candidate objects MUST equal the number of resumes.
- Return ONLY JSON.
- Do not return markdown.
- Do not return explanations outside JSON.

==================================================
JOB DESCRIPTION
==================================================

{jd_text[:15000]}

==================================================
RESUMES
==================================================

{all_resumes_text}

==================================================
EXTRACTION RULES
==================================================

JOB:

Extract:

1. Actual job title
2. Required technical and professional skills
3. Minimum required years of experience
4. Short factual summary

Normalize skills:

Examples:

ReactJS -> react js
React.js -> react js
NodeJS -> node js
Node.js -> node js
REST API -> rest apis

Skills must:
- be lowercase
- be deduplicated
- contain meaningful skills only

If the job description does not specify experience:

min_years_experience = 0


==================================================
CANDIDATES
==================================================

For EVERY resume extract:

1. filename
2. candidate name
3. skills
4. years of professional experience
5. highest education qualification
6. factual summary

IMPORTANT:

If candidate name is unavailable:

name = ""

If education is unavailable:

education = ""

Never return null.

If experience is unclear:

years_experience = 0

Do not invent information.

Skills must:
- be lowercase
- be deduplicated
- use normalized names


==================================================
OUTPUT
==================================================

Return exactly this JSON structure:

{{
    "job": {{
        "title": "string",
        "required_skills": [
            "skill1",
            "skill2"
        ],
        "min_years_experience": 0,
        "summary": "string"
    }},

    "candidates": [
        {{
            "filename": "resume.pdf",
            "name": "Candidate Name",
            "skills": [
                "java",
                "react",
                "sql"
            ],
            "years_experience": 0,
            "education": "Bachelor of Engineering",
            "summary": "Factual summary."
        }}
    ]
}}

FINAL REQUIREMENT:

There are exactly {len(resumes)} resumes.

Therefore:

"candidates" MUST contain exactly {len(resumes)} objects.

Do not omit any resume.
Do not merge resumes.
Do not invent resumes.
"""


    # ========================================================
    # SEND ONE REQUEST
    # ========================================================

    print(
        "\nSending JD + all resumes to Gemini in ONE request..."
    )

    print(
        f"Calling Gemini model: {MODEL}"
    )


    try:

        response = _call_gemini_with_retry(
            prompt
        )

        if not response.text:

            raise ValueError(
                "Gemini returned an empty response."
            )


        result = _clean_json(
            response.text
        )


        # ====================================================
        # VALIDATE RESULT
        # ====================================================

        job_fields = result.get(
            "job",
            {}
        )

        candidates = result.get(
            "candidates",
            []
        )


        print(
            "\nGemini extraction completed."
        )

        print(
            f"Gemini returned "
            f"{len(candidates)} candidate(s)."
        )


        # ====================================================
        # CHECK CANDIDATE COUNT
        # ====================================================

        if len(candidates) != len(resumes):

            print(
                "\n[WARNING]"
            )

            print(
                f"Expected {len(resumes)} candidates "
                f"but Gemini returned "
                f"{len(candidates)}."
            )


            # ------------------------------------------------
            # Try to restore missing candidates using filename
            # ------------------------------------------------

            existing_files = {
                candidate.get("filename", "")
                for candidate in candidates
            }


            for resume in resumes:

                filename = resume.get(
                    "filename",
                    ""
                )

                if filename not in existing_files:

                    print(
                        f"Adding missing candidate: "
                        f"{filename}"
                    )

                    candidates.append(
                        {
                            "filename": filename,
                            "name": "",
                            "skills": [],
                            "years_experience": 0,
                            "education": "",
                            "summary": ""
                        }
                    )


        # ====================================================
        # FORCE EXACT COUNT
        # ====================================================

        # Match candidates back to supplied filenames.

        candidate_map = {
            candidate.get("filename", ""): candidate
            for candidate in candidates
        }


        final_candidates = []


        for resume in resumes:

            filename = resume.get(
                "filename",
                ""
            )


            candidate = candidate_map.get(
                filename
            )


            if candidate is None:

                candidate = {
                    "filename": filename,
                    "name": "",
                    "skills": [],
                    "years_experience": 0,
                    "education": "",
                    "summary": ""
                }


            # ------------------------------------------------
            # Normalize missing fields
            # ------------------------------------------------

            candidate["filename"] = filename

            if candidate.get("name") is None:
                candidate["name"] = ""

            if candidate.get("education") is None:
                candidate["education"] = ""

            if not isinstance(
                candidate.get("skills"),
                list
            ):
                candidate["skills"] = []


            if candidate.get(
                "years_experience"
            ) is None:

                candidate[
                    "years_experience"
                ] = 0


            if candidate.get(
                "summary"
            ) is None:

                candidate["summary"] = ""


            final_candidates.append(
                candidate
            )


        print(
            f"Final candidate count: "
            f"{len(final_candidates)}"
        )


        return (
            job_fields,
            final_candidates
        )


    except Exception as e:

        print(
            "\n[ERROR] Gemini extraction failed:"
        )

        print(e)

        raise


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def extract_resume_fields(
    resume_text: str
) -> dict:
    """
    Compatibility function for older code.

    This sends one resume to Gemini.
    For the main application use
    extract_all_resume_fields().
    """

    _, candidates = extract_all_resume_fields(
        "",
        [
            {
                "filename": "resume.pdf",
                "text": resume_text
            }
        ]
    )


    if candidates:

        return candidates[0]


    return {
        "filename": "resume.pdf",
        "name": "",
        "skills": [],
        "years_experience": 0,
        "education": "",
        "summary": ""
    }


# ============================================================
# COMPATIBILITY FUNCTION
# ============================================================

def extract_jd_fields(
    jd_text: str
) -> dict:
    """
    Compatibility function for older code.

    NOTE:
    The main application should extract the JD together
    with all resumes using extract_all_resume_fields().
    """

    # We can extract only the JD by sending an empty
    # placeholder resume. This function exists only for
    # compatibility with older code.

    job, _ = extract_all_resume_fields(
        jd_text,
        [
            {
                "filename": "__placeholder__.pdf",
                "text": ""
            }
        ]
    )


    return job