import pytest

from app.evidence.selector import EvidenceCandidate, select_evidence


def test_select_evidence_returns_central_diverse_and_counter_examples() -> None:
    candidates = [
        EvidenceCandidate(
            complaint_id="1",
            source_text="The dispute has been pending for six weeks.",
            evidence_span="pending for six weeks",
            similarity=0.95,
            contradicts_theme=False,
        ),
        EvidenceCandidate(
            complaint_id="2",
            source_text="I called repeatedly and still have no update.",
            evidence_span="still have no update",
            similarity=0.70,
            contradicts_theme=False,
        ),
        EvidenceCandidate(
            complaint_id="3",
            source_text="The dispute was resolved the next day.",
            evidence_span="resolved the next day",
            similarity=0.80,
            contradicts_theme=True,
        ),
    ]

    selection = select_evidence(candidates)

    assert selection.central.complaint_id == "1"
    assert selection.diverse.complaint_id == "2"
    assert selection.counter.complaint_id == "3"


def test_select_evidence_rejects_generated_or_paraphrased_span() -> None:
    candidates = [
        EvidenceCandidate(
            complaint_id="1",
            source_text="The dispute has been pending for six weeks.",
            evidence_span="pending for months",
            similarity=0.95,
            contradicts_theme=False,
        ),
        EvidenceCandidate(
            complaint_id="2",
            source_text="I still have no update.",
            evidence_span="still have no update",
            similarity=0.70,
            contradicts_theme=False,
        ),
        EvidenceCandidate(
            complaint_id="3",
            source_text="The dispute was resolved the next day.",
            evidence_span="resolved the next day",
            similarity=0.80,
            contradicts_theme=True,
        ),
    ]

    with pytest.raises(ValueError, match="not grounded in complaint 1"):
        select_evidence(candidates)
