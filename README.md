# Resume Screening Agent

An AI-powered resume screening system that analyzes a job description and multiple resumes, extracts structured candidate information using Google Gemini, calculates explainable relevance scores, ranks candidates, and saves the results in both JSON and CSV formats.

## Features

- Extracts structured information from job descriptions.
- Processes **10+ resumes in a single run**.
- Sends the job description and all resumes to Gemini in a **batch extraction request**.
- Extracts candidate name, skills, experience, education, and summary.
- Calculates semantic similarity between the candidate and job description.
- Calculates required-skill overlap.
- Produces an explainable final score.
- Ranks candidates from highest to lowest score.
- Generates deterministic reasoning for every candidate.
- Saves ranked results as JSON and CSV.
- Includes automated tests for scoring and ranking.
- Uses environment variables for the Gemini API key.

---

## Project Structure

```text
resume-screening-agent/
│
├── agent/
│   ├── __init__.py
│   ├── extractor.py
│   ├── parser.py
│   ├── ranker.py
│   └── scorer.py
│
├── data/
│   ├── jd.txt
│   └── resumes/
│       ├── Candidate_01_Aarav_Shah.pdf
│       ├── Candidate_02_Priya_Nair.pdf
│       ├── Candidate_03_Rohan_Mehta.pdf
│       ├── Candidate_04_Ananya_Rao.pdf
│       ├── Candidate_05_Vikram_Singh.pdf
│       └── ...
│
├── output/
│   ├── ranked_candidates.json
│   └── ranked_candidates.csv
│
├── tests/
│   ├── __init__.py
│   ├── test_ranker.py
│   └── test_scorer.py
│
├── main.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

> `.env` should contain the API key locally and should not be committed to GitHub.

---

## How the System Works

The application follows this pipeline:

```text
                 Job Description
                       │
                       ▼
                  PDF / TXT Input
                       │
                       ▼
                   Gemini API
                       │
                       ▼
               Structured JD Data
                       │
                       ▼
                Multiple Resumes
                       │
                       ▼
                  PDF Parser
                       │
                       ▼
             Gemini Batch Extraction
                       │
                       ▼
          ┌──────────────────────────┐
          │ Candidate Information    │
          │                          │
          │ • Name                   │
          │ • Skills                 │
          │ • Experience             │
          │ • Education              │
          │ • Summary                │
          └──────────────────────────┘
                       │
                       ▼
                Resume Scoring
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      Semantic Similarity    Skill Overlap
             70%                   30%
             │                   │
             └─────────┬─────────┘
                       ▼
                  Final Score
                       │
                       ▼
                Rank Candidates
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          JSON Output         CSV Output
```

### Batch Processing

All resumes are read from:

```text
data/resumes/
```

The application collects the text from every PDF and sends the JD together with the resumes to Gemini in a single batch extraction request.

For example, if the folder contains 10 resumes, the system processes all 10 candidates and returns 10 candidate objects.

The number of returned candidates is validated against the number of supplied resumes.

---

## Scoring

The final score uses two explainable signals:

### 1. Semantic Similarity — 70%

The system compares the resume summary with the job description summary using embedding vectors and cosine similarity.

```text
semantic_score = cosine_similarity(resume_embedding, jd_embedding)
```

The similarity is clipped to a minimum of `0`.

### 2. Skill Overlap — 30%

The system compares the candidate's extracted skills with the required skills from the job description.

```text
skill_overlap =
    matched_required_skills / total_required_skills
```

### Final Score

```text
final_score =
    (0.7 × semantic_similarity)
    + (0.3 × skill_overlap)
```

The result is converted to a `0–100` scale.

Example:

```text
Semantic similarity = 80%
Skill overlap        = 60%

Final score =
(0.7 × 80) + (0.3 × 60)

= 74%
```

The scoring logic is deterministic after extraction, so the ranking calculation itself does not make another LLM request.

---

## Experience Check

The system also compares:

```text
candidate years of experience
```

against:

```text
minimum required years of experience
```

The result is stored as:

```json
"meets_experience_requirement": true
```

or:

```json
"meets_experience_requirement": false
```

If the job description does not specify experience, the extracted minimum experience is `0`.

---

## Explainable Ranking

Candidates are sorted by their final score in descending order.

Each candidate receives:

- Rank
- Final score
- Semantic score
- Skill overlap score
- Matched skills
- Missing skills
- Years of experience
- Experience requirement status
- Deterministic reasoning

Example reasoning:

```text
Matches 6 required skill(s): javascript, react js, node js,
typescript, html5, css3. Missing: aws, mqtt.
Meets experience requirement (2 yrs).
Semantic fit 82%, skill overlap 60%.
```

---

## Input Files

### Job Description

Place the job description in:

```text
data/jd.txt
```

Example:

```text
Lead Full Stack Developer

We are seeking an experienced Full Stack Developer...

Required skills:
React, Angular, Node.js, TypeScript, JavaScript,
HTML5, CSS3, REST APIs, AWS...
```

### Resumes

Place PDF resumes in:

```text
data/resumes/
```

The application automatically discovers PDF files in this directory.

You do not need to manually list each resume in `main.py`.

---

## Requirements

Recommended Python version:

```text
Python 3.11+
```

The current development environment may use Python 3.10, but upgrading to Python 3.11+ is recommended for continued compatibility with Google's Python packages.

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Gemini API Configuration

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

The project loads the key using `python-dotenv`.

Do not commit the real API key.

The `.gitignore` should include:

```text
.env
venv/
__pycache__/
*.pyc
```

Use `.env.example` for documentation:

```text
GEMINI_API_KEY=your_api_key_here
```

---

## Running the Application

Activate the virtual environment.

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

Then run:

```powershell
python main.py
```

The application will:

1. Load the job description.
2. Find all PDF resumes.
3. Extract text from every resume.
4. Send the JD and resumes to Gemini for structured extraction.
5. Calculate candidate scores.
6. Rank candidates.
7. Generate explanations.
8. Save JSON results.
9. Save CSV results.
10. Print the ranked candidates to the terminal.

Example terminal output:

```text
Found 10 resume(s)

Sending JD + all resumes to Gemini in ONE request...
Gemini extraction completed.

Gemini returned 10 candidate(s).

Results saved to:
output/ranked_candidates.json

CSV results saved to:
output/ranked_candidates.csv

1. Vikram Singh -> 67.71%
2. Aarav Shah -> 49.69%
3. Priya Nair -> 48.72%
...
```

---

## Output

The application creates:

```text
output/
├── ranked_candidates.json
└── ranked_candidates.csv
```

### JSON Output

The JSON file contains detailed structured information for each candidate, including scoring and reasoning.

Example:

```json
{
  "rank": 1,
  "filename": "candidate.pdf",
  "resume_fields": {
    "name": "Candidate Name",
    "skills": ["react js", "node js"],
    "years_experience": 2,
    "education": "B.E.",
    "summary": "..."
  },
  "score_info": {
    "final_score": 78.5,
    "semantic_score": 80.0,
    "skill_overlap_score": 75.0,
    "matched_skills": ["react js", "node js"],
    "missing_skills": ["aws"],
    "years_experience": 2,
    "meets_experience_requirement": true
  },
  "reasoning": "..."
}
```

### CSV Output

The CSV is designed for easy review in Excel or Google Sheets.

Typical columns include:

```text
rank
filename
name
final_score
semantic_score
skill_overlap_score
years_experience
meets_experience_requirement
matched_skills
missing_skills
reasoning
```

---

## Running Tests

The project includes tests for the scoring and ranking components.

Run:

```powershell
pytest
```

Expected result:

```text
4 passed
```

The tests verify:

- Skill overlap calculation.
- Matching and missing skills.
- Candidate ranking order.
- Ranking and reasoning behavior.

---

## Main Components

### `main.py`

Application entry point.

Responsibilities:

- Load the JD.
- Discover resume PDFs.
- Parse resume text.
- Call batch extraction.
- Score candidates.
- Rank candidates.
- Save JSON.
- Save CSV.
- Print results.

### `agent/parser.py`

Handles PDF text extraction.

### `agent/extractor.py`

Uses the Google GenAI SDK to extract structured information from the JD and multiple resumes.

The current implementation is designed for batch processing.

### `agent/scorer.py`

Calculates:

- Semantic similarity.
- Skill overlap.
- Final score.
- Experience requirement status.

### `agent/ranker.py`

Sorts candidates by final score and generates deterministic reasoning.

### `tests/`

Contains automated tests for the ranking and scoring logic.

---

## Technologies Used

- Python
- Google Gemini API
- Google GenAI Python SDK
- NumPy
- PyPDF2 / PDF parsing
- python-dotenv
- pytest
- JSON
- CSV

---

## Design Decisions

### Why batch extraction?

Sending multiple resumes together reduces the number of Gemini generation requests compared with making one generation request per resume.

For example:

```text
10 resumes

Individual approach:
10+ Gemini generation requests

Batch approach:
1 Gemini generation request
```

This is especially useful when working with API request quotas.

### Why deterministic scoring?

The final ranking is calculated in Python rather than asking Gemini to assign the final score.

This makes the scoring formula:

```text
70% semantic similarity
30% skill overlap
```

explicit, reproducible, and easier to audit.

### Why JSON and CSV?

JSON preserves the detailed structured output.

CSV makes the ranked candidates easy to inspect, filter, sort, and share.

---

## Error Handling

The application handles common issues such as:

- Missing Gemini API key.
- Empty Gemini responses.
- Invalid JSON responses.
- PDF extraction failures.
- Missing input files.
- API errors.
- Batch extraction failures.

The application reports errors in the terminal so they can be diagnosed without silently producing invalid results.

---

## Limitations

- Gemini API availability and quotas can affect batch extraction.
- Very large collections of resumes may exceed model input limits and should be processed in smaller batches.
- Years of experience are estimated from resume text.
- Skill extraction depends on the quality of the source resume and model extraction.
- Semantic similarity is only one signal and should not replace human review.
- The system is intended as a screening aid, not an autonomous hiring decision maker.

---

## Security

Never commit secrets to GitHub.

Keep:

```text
.env
```

out of version control.

If an API key is accidentally committed, revoke it and generate a new key.

---

## Quick Start

```powershell
# 1. Clone the repository
git clone <repository-url>

# 2. Enter the project
cd resume-screening-agent

# 3. Create/activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure Gemini API key
# Create .env and add:
# GEMINI_API_KEY=your_api_key_here

# 6. Add the job description
# data/jd.txt

# 7. Add PDF resumes
# data/resumes/

# 8. Run the application
python main.py

# 9. Run tests
pytest
```

---

## Project Goal

The goal of this project is to demonstrate an explainable AI-assisted resume screening workflow that can:

- Process multiple resumes efficiently.
- Extract structured candidate information.
- Compare candidates against a job description.
- Produce transparent relevance scores.
- Rank candidates automatically.
- Provide human-readable explanations.
- Export results in both machine-readable JSON and spreadsheet-friendly CSV formats.


---

## Author

**Sharon Jessy T S**

Information Science Engineering  
B.E. (2022–2026)

GitHub: **sharon-jessy13**