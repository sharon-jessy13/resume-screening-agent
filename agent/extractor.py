"""
extractor.py
Uses Gemini to pull structured fields (skills, experience, education) out of
free-form resume text and the job description.
"""

import json
import re
import google.generativeai as genai

EXTRACTION_MODEL = "gemini-2.5-flash"

RESUME_PROMPT = """You are an information extraction engine. Read the resume text
below and return ONLY a valid JSON object (no markdown, no commentary) with this
exact shape:

{{
  "name": "string or null",
  "skills": ["skill1", "skill2", ...],
  "years_experience": number,
  "education": "highest qualification, one line",
  "summary": "2-3 sentence factual summary of their background"
}}

Rules:
- "skills" should be normalized (e.g. "ReactJS" -> "React"), deduplicated, lowercase.
- "years_experience" is your best numeric estimate from dates/titles. Use 0 if unclear.
- If a field is missing from the resume, use null (or [] / 0 as appropriate).

RESUME TEXT:
\"\"\"
{resume_text}
\"\"\"
"""

JD_PROMPT = """You are an information extraction engine. Read the job description
below and return ONLY a valid JSON object (no markdown, no commentary) with this
exact shape:

{{
  "title": "string",
  "required_skills": ["skill1", "skill2", ...],
  "min_years_experience": number,
  "summary": "2-3 sentence factual summary of what this role needs"
}}

Rules:
- "required_skills" should be normalized (e.g. "ReactJS" -> "React"), deduplicated, lowercase.
- "min_years_experience" is your best numeric estimate. Use 0 if unclear.

JOB DESCRIPTION TEXT:
\"\"\"
{jd_text}
\"\"\"
"""


def _clean_json(raw: str) -> dict:
    """Strip markdown fences if present and parse JSON safely."""
    cleaned = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def extract_resume_fields(resume_text: str) -> dict:
    model = genai.GenerativeModel(EXTRACTION_MODEL)
    prompt = RESUME_PROMPT.format(resume_text=resume_text[:12000])
    response = model.generate_content(prompt)
    try:
        return _clean_json(response.text)
    except Exception as e:
        print(f"[warn] Could not parse resume extraction JSON: {e}")
        return {
            "name": None,
            "skills": [],
            "years_experience": 0,
            "education": None,
            "summary": "",
        }


def extract_jd_fields(jd_text: str) -> dict:
    model = genai.GenerativeModel(EXTRACTION_MODEL)
    prompt = JD_PROMPT.format(jd_text=jd_text[:12000])
    response = model.generate_content(prompt)
    try:
        return _clean_json(response.text)
    except Exception as e:
        print(f"[warn] Could not parse JD extraction JSON: {e}")
        return {
            "title": "Unknown Role",
            "required_skills": [],
            "min_years_experience": 0,
            "summary": "",
        }
