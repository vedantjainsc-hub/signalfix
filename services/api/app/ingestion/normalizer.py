from typing import Any

from app.schemas.complaint import ComplaintRecord

CFPB_COMPLAINT_URL = (
    "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1"
)


def normalize_cfpb_hit(hit: dict[str, Any], snapshot_id: str) -> ComplaintRecord:
    source = hit["_source"]
    if not source.get("complaint_id"):
        raise ValueError("complaint_id is required")
    complaint_id = str(source["complaint_id"])
    timely = source.get("timely")

    return ComplaintRecord(
        complaint_id=complaint_id,
        source="cfpb",
        received_at=source["date_received"],
        product=source["product"],
        sub_product=source.get("sub_product"),
        issue=source.get("issue"),
        sub_issue=source.get("sub_issue"),
        narrative=source.get("complaint_what_happened") or None,
        company_response=source.get("company_response"),
        timely_response={"Yes": True, "No": False}.get(timely),
        state=source.get("state"),
        source_url=f"{CFPB_COMPLAINT_URL}/{complaint_id}",
        snapshot_id=snapshot_id,
    )
