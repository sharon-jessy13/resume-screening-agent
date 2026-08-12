from agent.ranker import rank_candidates


def test_rank_candidates():
    results = [
        {
            "filename": "candidate1.pdf",
            "resume_fields": {
                "name": "Candidate One"
            },
            "score_info": {
                "final_score": 60.0,
                "semantic_score": 70.0,
                "skill_overlap_score": 50.0,
                "matched_skills": ["react"],
                "missing_skills": ["angular"],
                "years_experience": 2,
                "meets_experience_requirement": True
            }
        },
        {
            "filename": "candidate2.pdf",
            "resume_fields": {
                "name": "Candidate Two"
            },
            "score_info": {
                "final_score": 85.0,
                "semantic_score": 90.0,
                "skill_overlap_score": 80.0,
                "matched_skills": ["react", "node js"],
                "missing_skills": [],
                "years_experience": 3,
                "meets_experience_requirement": True
            }
        }
    ]

    ranked = rank_candidates(results)

    assert ranked[0]["filename"] == "candidate2.pdf"
    assert ranked[0]["rank"] == 1

    assert ranked[1]["filename"] == "candidate1.pdf"
    assert ranked[1]["rank"] == 2


def test_rank_order():
    results = [
        {
            "filename": "low.pdf",
            "resume_fields": {},
            "score_info": {
                "final_score": 20,
                "semantic_score": 20,
                "skill_overlap_score": 20,
                "matched_skills": [],
                "missing_skills": ["react"],
                "years_experience": 0,
                "meets_experience_requirement": False
            }
        },
        {
            "filename": "high.pdf",
            "resume_fields": {},
            "score_info": {
                "final_score": 90,
                "semantic_score": 90,
                "skill_overlap_score": 90,
                "matched_skills": ["react"],
                "missing_skills": [],
                "years_experience": 2,
                "meets_experience_requirement": True
            }
        }
    ]

    ranked = rank_candidates(results)

    # Highest score should come first
    assert ranked[0]["score_info"]["final_score"] == 90
    assert ranked[0]["filename"] == "high.pdf"
    assert ranked[0]["rank"] == 1

    # Lower score should come second
    assert ranked[1]["score_info"]["final_score"] == 20
    assert ranked[1]["filename"] == "low.pdf"
    assert ranked[1]["rank"] == 2