from datetime import UTC, datetime

import pytest

from app.ingestion.normalizer import normalize_cfpb_hit


def test_normalize_cfpb_hit_preserves_source_lineage() -> None:
    hit = {
        "_source": {
            "complaint_id": "8085685",
            "date_received": "2024-01-01T00:04:58.000Z",
            "product": "Credit card",
            "sub_product": "General-purpose credit card or charge card",
            "issue": "Advertising and marketing, including promotional offers",
            "sub_issue": "Didn't receive advertised or promotional terms",
            "complaint_what_happened": "The advertised terms were not applied.",
            "company_response": "Closed with explanation",
            "timely": "Yes",
            "state": "NY",
        }
    }

    complaint = normalize_cfpb_hit(hit, snapshot_id="snapshot-2024")

    assert complaint.complaint_id == "8085685"
    assert complaint.source == "cfpb"
    assert complaint.received_at == datetime(2024, 1, 1, 0, 4, 58, tzinfo=UTC)
    assert complaint.narrative == "The advertised terms were not applied."
    assert complaint.timely_response is True
    assert complaint.snapshot_id == "snapshot-2024"
    assert complaint.source_url.endswith("8085685")


def test_normalize_cfpb_hit_rejects_record_without_complaint_id() -> None:
    hit = {
        "_source": {
            "date_received": "2024-01-01T00:04:58.000Z",
            "product": "Credit card",
        }
    }

    with pytest.raises(ValueError, match="complaint_id is required"):
        normalize_cfpb_hit(hit, snapshot_id="snapshot-2024")
