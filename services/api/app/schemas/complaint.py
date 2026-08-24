from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ComplaintRecord(BaseModel):
    complaint_id: str
    source: Literal["cfpb", "northstar_synthetic"]
    received_at: datetime
    product: str
    sub_product: str | None = None
    issue: str | None = None
    sub_issue: str | None = None
    narrative: str | None = None
    company_response: str | None = None
    timely_response: bool | None = None
    state: str | None = None
    source_url: str | None = None
    privacy_status: Literal["passed", "masked", "quarantined"] = "passed"
    snapshot_id: str
