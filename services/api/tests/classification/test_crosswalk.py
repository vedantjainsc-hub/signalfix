from app.classification.crosswalk import classify_with_crosswalk


def test_crosswalk_maps_unresolved_purchase_dispute_to_delayed_resolution() -> None:
    result = classify_with_crosswalk(
        issue="Problem with a purchase shown on your statement",
        sub_issue=(
            "Credit card company isn't resolving a dispute about a purchase on your statement"
        ),
    )

    assert result.process_stage == "purchase_disputes"
    assert result.failure_mode == "delayed_resolution"
    assert result.confidence == 0.9
    assert result.needs_review is False


def test_crosswalk_abstains_for_unknown_issue_pair() -> None:
    result = classify_with_crosswalk(issue="Unexpected issue", sub_issue=None)

    assert result.process_stage == "unknown"
    assert result.failure_mode == "unknown"
    assert result.confidence == 0.0
    assert result.needs_review is True
