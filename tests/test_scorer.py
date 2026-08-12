from agent.scorer import _skill_overlap


def test_skill_overlap():
    resume_skills = [
        "react",
        "javascript",
        "node js",
        "html5"
    ]

    required_skills = [
        "react",
        "javascript",
        "node js",
        "typescript"
    ]

    ratio, matched, missing = _skill_overlap(
        resume_skills,
        required_skills
    )

    assert ratio == 0.75

    assert "react" in matched
    assert "javascript" in matched
    assert "node js" in matched

    assert "typescript" in missing


def test_empty_required_skills():
    ratio, matched, missing = _skill_overlap(
        ["react", "javascript"],
        []
    )

    assert ratio == 0.0
    assert matched == []
    assert missing == []