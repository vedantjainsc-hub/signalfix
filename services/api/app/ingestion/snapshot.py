import hashlib
import json
from typing import Any

from pydantic import BaseModel


class SnapshotManifest(BaseModel):
    snapshot_id: str
    query: dict[str, Any]
    complaint_ids: list[str]
    record_count: int
    last_updated: str | None


def build_snapshot_manifest(
    query: dict[str, Any], hits: list[dict[str, Any]], last_updated: str | None
) -> SnapshotManifest:
    complaint_ids = sorted(str(hit["_source"]["complaint_id"]) for hit in hits)
    canonical = json.dumps(
        {
            "query": query,
            "complaint_ids": complaint_ids,
            "last_updated": last_updated,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    snapshot_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return SnapshotManifest(
        snapshot_id=snapshot_id,
        query=query,
        complaint_ids=complaint_ids,
        record_count=len(complaint_ids),
        last_updated=last_updated,
    )
