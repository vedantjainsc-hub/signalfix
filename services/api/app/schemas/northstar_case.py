from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class NorthstarCase(BaseModel):
    case_id: str
    source: Literal["northstar_synthetic"] = "northstar_synthetic"
    received_at: datetime
    channel: Literal["web", "phone", "chat", "branch"]
    product: Literal["credit_card"] = "credit_card"
    process_stage: str
    failure_mode: str
    narrative: str
    handle_minutes: int = Field(gt=0)
    repeat_contact: bool
    escalated: bool
    sla_breach: bool
    estimated_cost_usd: float = Field(ge=0)
    owner_role: str
    generator_version: str = "0.1.0"
