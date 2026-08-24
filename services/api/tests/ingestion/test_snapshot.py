from app.ingestion.snapshot import build_snapshot_manifest


def test_snapshot_id_is_stable_across_hit_order() -> None:
    query = {
        "product": "Credit card",
        "date_received_min": "2024-01-01",
        "date_received_max": "2025-01-01",
    }
    hits_a = [
        {"_source": {"complaint_id": "2"}},
        {"_source": {"complaint_id": "1"}},
    ]
    hits_b = list(reversed(hits_a))

    manifest_a = build_snapshot_manifest(query, hits_a, last_updated="2025-01-02T00:00:00Z")
    manifest_b = build_snapshot_manifest(query, hits_b, last_updated="2025-01-02T00:00:00Z")

    assert manifest_a.snapshot_id == manifest_b.snapshot_id
    assert manifest_a.record_count == 2
    assert manifest_a.complaint_ids == ["1", "2"]
    assert len(manifest_a.snapshot_id) == 64
