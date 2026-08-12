# Resume Screening Agent

An AI-powered Resume Screening Agent that analyzes a Job Description (JD), extracts structured information from multiple resumes, calculates candidate relevance scores, ranks candidates, and generates machine-readable output.

The system uses Google's Gemini API to process the Job Description and multiple resumes in a single extraction request.

---

## Features

- Extracts structured information from a Job Description
- Processes 10+ resumes in a single run
- Sends the JD and all resumes to Gemini in one request
- Extracts:
  - Candidate name
  - Skills
  - Years of experience
  - Education
  - Resume summary
- Extracts:
  - Job title
  - Required skills
  - Minimum experience
  - Job summary
- Normalizes and deduplicates skills
- Calculates candidate relevance scores
- Calculates skill overlap
- Calculates semantic similarity
- Checks experience requirements
- Ranks candidates automatically
- Generates deterministic and explainable ranking reasons
- Saves results as JSON
- Supports CSV output
- Includes automated tests using pytest
- Designed to avoid making one Gemini request per resume

---

## Project Structure

```text
resume-screening-agent/
│
├── agent/
│   ├── __init__.py
│   ├── extractor.py
│   ├── scorer.py
│   └── ranker.py
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

---

## **How the System Works**

1. How the System Works

The application follows this pipeline:

                 Job Description
                       │
                       ▼
                 Gemini API
                       │
                       ▼
              JD Structured Data
                       │
                       │
                       ▼
        ┌──────────────────────────┐
        │      Multiple Resumes    │
        │                          │
        │ Resume 1                 │
        │ Resume 2                 │
        │ Resume 3                 │
        │ ...                      │
        │ Resume 10                │
        └──────────────────────────┘
                       │
                       ▼
                 Gemini API
             ONE extraction request
                       │
                       ▼
              Resume Structured Data
                       │
                       ▼
                   Scoring
                       │
                       ▼
                   Ranking
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        ranked JSON          ranked CSV
2. Gemini Batch Processing

The application is designed to process multiple resumes in a single Gemini request.

For example, if there are 10 resumes:

JD + Resume 1 + Resume 2 + ... + Resume 10

are sent to Gemini together.

Gemini returns structured information for all candidates.

This avoids making:

1 Gemini request for Resume 1
1 Gemini request for Resume 2
1 Gemini request for Resume 3
...
10 Gemini requests

Instead, the application uses:

1 Gemini extraction request

for the complete batch.

This significantly reduces the number of Gemini API requests.

3. Scoring

The candidate score is calculated using two main signals:

Semantic Similarity
+
Skill Overlap

The scoring formula is:

Final Score =
    0.7 × Semantic Similarity
  + 0.3 × Skill Overlap

The result is converted to a percentage from 0 to 100.

Semantic Similarity

Semantic similarity compares the candidate's resume information with the Job Description.

It measures how closely the candidate's background matches the requirements of the role.

Skill Overlap

Skill overlap measures how many required JD skills are present in the candidate's extracted skill list.

Example:

Required skills:
React
Angular
Node.js
TypeScript
AWS

Candidate skills:
React
Node.js
JavaScript
MongoDB

Matched skills:

React
Node.js

Therefore:

Skill Overlap = 2 / 5
               = 40%
4. Experience Check

The system also compares:

Candidate years of experience

with:

Required years of experience

For example:

Required experience: 3 years
Candidate experience: 4 years

Result:

Meets requirement: True

If:

Required experience: 3 years
Candidate experience: 1 year

Result:

Meets requirement: False
5. Explainable Ranking

The ranking system generates deterministic explanations.

Example:

Matches 8 required skill(s): react, node.js, javascript, typescript.
Missing: aws, mqtt.
Meets experience requirement (3 yrs).
Semantic fit 82.45%, skill overlap 66.67%.

The reasoning is generated without another Gemini request.

This makes the ranking easier to audit.

6. Requirements

The project requires:

Python 3.10+
Google Gemini API key
pytest

Recommended Python version:

Python 3.11

Python 3.10 may work, but newer versions are recommended for compatibility with current Google packages.

7. Installation

Clone the project or open the project directory.

Create a virtual environment:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt
8. Gemini API Key

Create a Gemini API key from Google's Gemini developer platform.

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here

Example:

GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXX

Do not commit the actual API key to GitHub.

The .env file should be included in .gitignore.

Example:

.env
venv/
__pycache__/
*.pyc
output/
9. Environment File

A safe .env.example file can contain:

GEMINI_API_KEY=your_gemini_api_key_here

Copy .env.example to .env and replace the placeholder with your actual API key.

10. Input Files
Job Description

Place the Job Description here:

data/jd.txt

Example:

Lead Full Stack Developer

We are seeking an experienced Lead Full Stack Developer...

Required skills:
React
Angular
Node.js
TypeScript
HTML5
CSS3
REST APIs
AWS
...
Resumes

Place resume PDF files inside:

data/resumes/

Example:

data/resumes/
├── Candidate_01_Aarav_Shah.pdf
├── Candidate_02_Priya_Nair.pdf
├── Candidate_03_Rohan_Mehta.pdf
├── Candidate_04_Ananya_Rao.pdf
├── Candidate_05_Vikram_Singh.pdf
├── SharonJessyTS_Resume.pdf
├── resume_114.pdf
└── updated_resume.pdf

The application automatically detects the PDF files in this directory.

11. Running the Application

Make sure the virtual environment is active:

venv\Scripts\activate

Then run:

python main.py

The application will:

Load the Job Description
Find all resumes
Extract text from the resumes
Send the JD and resumes to Gemini
Extract structured candidate information
Calculate candidate scores
Rank candidates
Save JSON output
Save CSV output
12. Example Console Output
RESUME SCREENING AGENT

Loading JD from data/jd.txt ...

Loading resumes from data/resumes ...

-> Found 10 resume(s)

Reading Candidate_01_Aarav_Shah.pdf ...
Reading Candidate_02_Priya_Nair.pdf ...
Reading Candidate_03_Rohan_Mehta.pdf ...
...

Sending 10 resumes in ONE Gemini request...

Gemini extraction completed.

Gemini returned 10 candidate(s).

Results saved to:
output/ranked_candidates.json

CSV results saved to:
output/ranked_candidates.csv

1. Vikram Singh -> 67.71%
2. Aarav Shah -> 49.69%
3. Priya Nair -> 48.72%
4. Ananya Rao -> 42.74%
5. Rohan Mehta -> 39.37%
...
13. JSON Output

The application generates:

output/ranked_candidates.json

The JSON contains information such as:

{
    "rank": 1,
    "filename": "Candidate_05_Vikram_Singh.pdf",
    "resume_fields": {
        "name": "Vikram Singh",
        "skills": [
            "react",
            "node.js",
            "javascript"
        ],
        "years_experience": 3,
        "education": "Bachelor of Engineering",
        "summary": "..."
    },
    "score_info": {
        "final_score": 67.71,
        "semantic_score": 72.45,
        "skill_overlap_score": 56.67,
        "matched_skills": [
            "react",
            "javascript"
        ],
        "missing_skills": [
            "aws"
        ],
        "years_experience": 3,
        "meets_experience_requirement": true
    },
    "reasoning": "..."
}
14. CSV Output

The application also generates:

output/ranked_candidates.csv

The CSV can be opened in:

Microsoft Excel
Google Sheets
LibreOffice Calc
Python/pandas
Other spreadsheet applications

Typical columns include:

Rank
Name
Filename
Final Score
Semantic Score
Skill Overlap Score
Years Experience
Meets Experience Requirement
Matched Skills
Missing Skills
Education
Summary
Reasoning
15. Running Tests

The project includes unit tests using pytest.

Run:

pytest

Expected result:

================================
4 passed
================================

The tests cover:

Skill overlap calculation
Matching skills
Missing skills
Candidate ranking order
Ranking behavior

The tests do not require a Gemini API call.

This makes them fast and suitable for local development.

16. Testing Structure

The project contains:

tests/
├── __init__.py
├── test_ranker.py
└── test_scorer.py

Example:

test_scorer.py

tests the skill overlap logic.

Example:

test_ranker.py

tests whether candidates are sorted correctly according to their final score.

17. Important Gemini API Considerations

Gemini API usage is subject to project/model quotas and rate limits.

A free-tier project may have a limited number of requests.

The application therefore avoids sending one request for every resume.

Instead:

10 resumes
      ↓
1 Gemini extraction request

is used.

However, the request itself can become large when many resumes contain a lot of text.

For very large batches, the application may need to:

Split resumes into smaller batches
Reduce resume text length
Use an appropriate Gemini model
Increase available API quota
Use a paid API project if required
18. Large Resume Collections

For 10 resumes, a single request can work when the combined input fits within the model's context limits.

For larger collections such as:

50 resumes
100 resumes
500 resumes

it is better to process them in batches.

Example:

Batch 1 → Resumes 1-10
Batch 2 → Resumes 11-20
Batch 3 → Resumes 21-30
...

This prevents excessively large prompts and reduces the possibility of server-side failures.

19. Error Handling

The application handles common issues such as:

Missing API key
GEMINI_API_KEY not found

Check:

.env

and make sure the API key is present.

Gemini quota exceeded

Example:

429 RESOURCE_EXHAUSTED

This means the Gemini API project has reached its available quota.

Changing the Python code alone does not increase the quota.

Possible solutions:

Use another project with available quota
Wait for the quota to reset
Use a model/project with available quota
Enable billing where appropriate
Server unavailable

Example:

503 UNAVAILABLE

This can happen when the model is temporarily experiencing high demand.

Retrying later or using an available model/project can resolve the issue.

20. Deterministic Scoring

The ranking calculation itself is deterministic once the extracted candidate data is available.

The scoring system does not ask Gemini to decide:

Candidate A = 72%
Candidate B = 61%

Instead, the application calculates the score using defined formulas.

This improves transparency and reproducibility.

The Gemini extraction stage can still produce slightly different structured outputs between runs because it is an AI model.

Therefore, if the extracted skills or summaries change, the final score may also change.

21. Technologies Used
Programming Language
Python
AI
Google Gemini API
Google SDK
google-genai
Data Processing
NumPy
Environment Configuration
python-dotenv
Testing
pytest
Resume Processing
PDF text extraction
22. Main Components
main.py

Responsible for the application workflow.

It:

Loads the JD
Finds resumes
Extracts resume text
Calls batch extraction
Scores candidates
Ranks candidates
Saves JSON
Saves CSV
Displays results
agent/extractor.py

Responsible for Gemini-based information extraction.

It extracts:

JD
title
required_skills
min_years_experience
summary
Resume
filename
name
skills
years_experience
education
summary

The extractor sends all resumes together in one Gemini request.

agent/scorer.py

Responsible for calculating candidate relevance.

It calculates:

Semantic Score
Skill Overlap Score
Final Score

It also determines:

Matched Skills
Missing Skills
Experience Requirement
agent/ranker.py

Responsible for:

Sorting candidates
Assigning ranks
Generating deterministic reasoning

Candidates are sorted by:

final_score

in descending order.

23. Example Ranking

Example:

Rank  Candidate              Score
------------------------------------------------
1     Vikram Singh           67.71%
2     Aarav Shah             49.69%
3     Priya Nair             48.72%
4     Ananya Rao             42.74%
5     Rohan Mehta             39.37%

The candidate with the highest final score receives rank 1.

24. Advantages

This project provides:

Automated resume screening
Batch resume processing
Structured candidate information
Explainable scoring
Skill-based comparison
Semantic matching
Experience checking
Candidate ranking
JSON export
CSV export
Automated tests

It reduces the manual effort required to compare multiple resumes against a Job Description.

25. Limitations

The system relies on AI-generated extraction, so extracted information may not always be perfect.

Potential limitations include:

Ambiguous resume dates
Unclear experience periods
Different names for similar technologies
Missing information in resumes
Large resume batches exceeding model context limits
Gemini API quota limitations
Temporary Gemini API availability issues

The results should therefore be treated as a screening aid rather than a replacement for human recruitment decisions.

26. Security

Never commit your Gemini API key.

Do NOT put this in Git:

GEMINI_API_KEY=actual_secret_key

Use:

.env

and add it to:

.gitignore

Use .env.example as a template:

GEMINI_API_KEY=your_gemini_api_key_here
27. Recommended .gitignore
# Virtual environment
venv/
.venv/

# Environment variables
.env

# Python cache
__pycache__/
*.py[cod]

# Pytest
.pytest_cache/

# Generated output
output/

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db
28. Quick Start

For a quick setup:

git clone <repository-url>

cd resume-screening-agent

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

Create:

.env

with:

GEMINI_API_KEY=your_api_key_here

Add the Job Description:

data/jd.txt

Add resume PDFs:

data/resumes/

Run:

python main.py

Run tests:

pytest

Check results:

output/ranked_candidates.json
output/ranked_candidates.csv
29. Expected Final Output

After successful execution:

resume-screening-agent/
│
├── output/
│   ├── ranked_candidates.json
│   └── ranked_candidates.csv
│
└── ...

The JSON contains the complete structured screening results.

The CSV provides a convenient table for reviewing and comparing candidates.

30. Project Goal

The goal of this project is to build an AI-assisted resume screening system that can efficiently process multiple resumes against a Job Description and provide:

Extraction
     ↓
Scoring
     ↓
Ranking
     ↓
Explanation
     ↓
JSON + CSV

The system is designed to make resume screening faster, more structured, and easier to audit while keeping the final recruitment decision with a human reviewer.
