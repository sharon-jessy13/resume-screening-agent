# Resume Screening Agent

An AI-powered Resume Screening Agent built for the **Rooman AI Challenge – Junior AI Research Associate Selection Round**.

The agent takes a **Job Description (JD)** and a folder of candidate resumes, extracts structured information, evaluates each resume against the JD, ranks the candidates, and produces **CSV and JSON** results with scores, matched skills, missing skills, and reasoning.

## Challenge

This project was selected as the **Resume Screening Agent** from the challenge's list of 12 agents.

The challenge expects the agent to:

- Parse resumes and extract skills, experience, and education.
- Compute relevance against a Job Description using NLP similarity.
- Rank candidates and provide reasoning.
- Handle 10+ resumes in a single run.
- Provide a JD, sample resumes, ranked CSV/JSON output, and an explanation of the scoring method.

Source: Rooman AI Challenge brief.

## Features

- PDF/text resume processing through the project's parser.
- Job Description extraction.
- Resume information extraction.
- Semantic similarity scoring using Gemini embeddings.
- Skill overlap analysis.
- Experience requirement comparison.
- Candidate ranking.
- Reasoning for candidate ranking.
- JSON output for structured results.
- CSV output for easy review in Excel/Google Sheets.
- Command-line execution.
- Environment-variable based Gemini API configuration.

## Project Structure

```text
resume-screening-agent/
│
├── agent/
│   ├── extractor.py       # Extracts structured JD/resume fields
│   ├── parser.py          # Reads JD and resume files
│   ├── ranker.py          # Ranks candidates
│   └── scorer.py          # Calculates candidate scores
│
├── data/
│   ├── jd.txt             # Job Description
│   └── resumes/           # Candidate resumes
│
├── output/                # Generated results
│   ├── ranked_results.json
│   └── ranked_results.csv
│
├── main.py                # CLI entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── .env                   # Local API key - DO NOT COMMIT
└── README.md
```

## How the Agent Works

```text
Job Description
       │
       ▼
   Parse JD
       │
       ▼
Extract JD Fields
       │
       │
       ├──────────────────────────────┐
       │                              │
       ▼                              ▼
Candidate Resumes              JD Requirements
       │
       ▼
Parse Resume
       │
       ▼
Extract Resume Fields
       │
       ▼
Compare Resume ↔ JD
       │
       ├── Semantic Similarity
       ├── Skill Overlap
       └── Experience Match
       │
       ▼
Calculate Score
       │
       ▼
Rank Candidates
       │
       ├──────────────► ranked_results.json
       │
       └──────────────► ranked_results.csv
```

## Tech Stack

- **Python**
- **Google Gemini API**
- **Gemini Embeddings** for semantic similarity
- **Pandas** for CSV generation
- **python-dotenv** for environment variables
- **PyPDF / document parsing dependencies** as configured in `requirements.txt`

## Requirements

- Python 3.11+ recommended
- Google Gemini API key
- pip
- Windows, macOS, or Linux

> Python 3.10 may work with the currently installed dependencies, but upgrading to Python 3.11+ is recommended for continued compatibility with the Google Python packages.

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd resume-screening-agent
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `python-dotenv` is missing:

```bash
pip install python-dotenv
```

## Gemini API Key Setup

Create a Gemini API key using Google AI Studio.

Then create a `.env` file in the project root:

```text
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

Example:

```text
GEMINI_API_KEY=your_actual_key
```

Never commit the `.env` file to GitHub.

Add this to `.gitignore`:

```text
.env
venv/
__pycache__/
output/
```

## Input Data

### Job Description

Place the job description at:

```text
data/jd.txt
```

Example:

```text
We are looking for a Full Stack Developer.

Required skills:
React
JavaScript
TypeScript
Node.js
HTML5
CSS3
REST API
AWS
Git

Experience:
2+ years
```

### Resumes

Place candidate resumes inside:

```text
data/resumes/
```

For example:

```text
data/resumes/
├── candidate_01.pdf
├── candidate_02.pdf
├── candidate_03.pdf
└── candidate_04.pdf
```

For the challenge submission, include **10 or more sample resumes** so the agent demonstrates the required batch-screening capability.

## Running the Agent

The default command is:

```bash
python main.py
```

This uses:

```text
JD:       data/jd.txt
Resumes:  data/resumes
Output:   output
```

You can also specify custom paths:

```bash
python main.py --jd data/jd.txt --resumes data/resumes --out output
```

### Command-line arguments

| Argument | Description | Default |
|---|---|---|
| `--jd` | Path to the Job Description | `data/jd.txt` |
| `--resumes` | Folder containing resumes | `data/resumes` |
| `--out` | Output folder | `output` |

## Output

After a successful run, the agent generates:

```text
output/
├── ranked_results.json
└── ranked_results.csv
```

### JSON Output

The JSON contains:

- Job description fields
- Candidate name
- Resume fields
- Final score
- Semantic score
- Skill overlap score
- Experience information
- Matched skills
- Missing skills
- Ranking/reasoning information

Example:

```json
{
  "job_description": {
    "title": "Full Stack Developer",
    "required_skills": [
      "react",
      "javascript",
      "node.js",
      "sql"
    ]
  },
  "candidates": [
    {
      "rank": 1,
      "filename": "candidate_01.pdf",
      "candidate_name": "Candidate One",
      "score_info": {
        "final_score": 86.5,
        "semantic_score": 89.2,
        "skill_overlap_score": 90.0,
        "years_experience": 2,
        "meets_experience_requirement": true,
        "matched_skills": [
          "react",
          "javascript",
          "node.js"
        ],
        "missing_skills": [
          "aws"
        ]
      }
    }
  ]
}
```

The exact values depend on the input JD and resumes.

### CSV Output

The CSV contains columns such as:

```text
rank
filename
candidate_name
final_score
semantic_score
skill_overlap_score
years_experience
meets_experience_requirement
matched_skills
missing_skills
reasoning
```

The CSV can be opened directly in Excel or Google Sheets.

## Scoring Approach

The agent evaluates candidates using multiple signals instead of relying only on keyword matching.

### 1. Semantic Similarity

The resume and Job Description are converted into embeddings.

This allows the system to compare the meaning and relevance of the resume content to the JD, even when the wording is not exactly identical.

### 2. Skill Overlap

The agent compares skills extracted from:

```text
Job Description
        ↓
Required skills
        ↓
Candidate resume skills
```

It identifies:

- Matched skills
- Missing skills

### 3. Experience Match

The candidate's extracted experience is compared with the experience requirement from the Job Description.

### 4. Final Score

The scorer combines the available signals into a final candidate score.

The implementation is contained in:

```text
agent/scorer.py
```

Keeping the scoring logic in a separate module makes it easier to adjust the weighting or add additional signals later.

## Ranking

After scoring all candidates, the ranking module:

1. Sorts candidates by their final score.
2. Assigns a rank.
3. Preserves the scoring details.
4. Provides reasoning for the ranking.

The implementation is in:

```text
agent/ranker.py
```

## Example Run

```text
Loading JD from data/jd.txt ...
  -> Role: Full Stack Developer
  -> Required skills: ['react', 'node.js', 'javascript', 'sql']

Loading resumes from data/resumes ...
  -> Found 10 resume(s)

Processing candidate_01.pdf ...
  -> Score: 86.5

Processing candidate_02.pdf ...
  -> Score: 78.4

...

Ranking candidates ...

Done. Wrote:
  output/ranked_results.json
  output/ranked_results.csv

=== SHORTLIST ===
1. Candidate One — 86.5/100
2. Candidate Two — 78.4/100
3. Candidate Three — 74.1/100
```

## Design Decisions

### Why Python?

Python provides a simple ecosystem for:

- Document parsing
- NLP
- Embeddings
- AI APIs
- Data processing

It also keeps the agent easy for reviewers to install and run.

### Why semantic similarity?

Keyword matching alone can miss relevant candidates when a resume uses different wording.

Semantic embeddings allow the agent to compare the meaning of resume content with the requirements of the Job Description.

### Why CSV and JSON?

JSON provides structured machine-readable output, while CSV makes the ranked shortlist easy to inspect manually.

### Why a CLI?

The challenge states that a UI is optional. A CLI keeps the implementation small, reproducible, and focused on the end-to-end agent workflow.

## Tradeoffs

### Advantages

- Simple architecture.
- Easy to run from the command line.
- Combines semantic and structured signals.
- Produces both human-friendly and machine-readable output.
- Easy to extend with additional scoring criteria.

### Limitations

- Resume parsing quality depends on the document format and parser.
- Extracted skills depend on the extraction logic.
- Embedding-based similarity does not guarantee that a candidate actually possesses a skill.
- Experience extraction can be imperfect when resumes use unusual wording.
- AI/API availability and model limits can affect execution.
- The system should be treated as a screening aid, not an automatic hiring decision-maker.

## Future Improvements

With more development time, the agent could be extended with:

- A Streamlit or React web interface.
- DOCX and image/OCR support.
- More robust structured extraction.
- Configurable scoring weights.
- Skill synonym mapping.
- Education and certification scoring.
- Duplicate resume detection.
- Batch processing progress indicators.
- Detailed candidate comparison reports.
- Human-review flags for uncertain candidates.
- Unit and integration tests.
- Persistent storage of screening runs.

## Testing Checklist

Before submission, verify:

- [ ] The project installs using `requirements.txt`.
- [ ] `.env` configuration is documented.
- [ ] API keys are not committed.
- [ ] The JD can be loaded.
- [ ] At least 10 resumes can be processed in one run.
- [ ] Resume fields are extracted.
- [ ] Scores are generated.
- [ ] Candidates are ranked.
- [ ] JSON output is generated.
- [ ] CSV output is generated.
- [ ] Sample input/output is included.
- [ ] README instructions work from a clean environment.

## Challenge Deliverables

This repository provides the core deliverables requested for the Resume Screening Agent:

- **Job Description:** `data/jd.txt`
- **Sample resumes:** `data/resumes/`
- **Ranked output:** `output/ranked_results.json` and `output/ranked_results.csv`
- **Scoring explanation:** This README
- **Runnable agent:** `main.py`

## Security

Never commit:

```text
.env
```

Never expose your Gemini API key in:

- GitHub
- README files
- Screenshots
- Source code
- Public messages

If an API key is accidentally exposed, revoke it and create a new key.

## Author

**Sharon Jessy T S**

Resume Screening Agent developed for the Rooman AI Challenge.

## License

This project was created as part of the Rooman AI Challenge and is intended for evaluation and demonstration purposes.
