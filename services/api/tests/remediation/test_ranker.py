from app.remediation.ranker import DEFAULT_WEIGHTS, ScoreInputs, score_remediation


def test_score_remediation_exposes_every_weighted_contribution() -> None:
    inputs = ScoreInputs(
        internal_signal=80,
        external_signal=60,
        harm_severity=70,
        cost_to_serve=50,
        evidence_confidence=90,
        strategic_fit=40,
        feasibility=100,
    )

    assessment = score_remediation("proactive-status", inputs)

    assert assessment.remediation_id == "proactive-status"
    assert assessment.score == 69.5
    assert assessment.weights == DEFAULT_WEIGHTS
    assert assessment.contributions == {
        "internal_signal": 16.0,
        "external_signal": 9.0,
        "harm_severity": 14.0,
        "cost_to_serve": 7.5,
        "evidence_confidence": 9.0,
        "strategic_fit": 4.0,
        "feasibility": 10.0,
    }
    assert sum(assessment.contributions.values()) == assessment.score
