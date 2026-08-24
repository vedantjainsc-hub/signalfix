from datetime import datetime
from typing import Literal

from pydantic import BaseModel

PlanStatus = Literal[
    "draft",
    "needs_evidence",
    "ready_for_review",
    "approved_pilot",
    "rejected",
    "cancelled",
    "in_progress",
    "measured",
    "closed",
]


class ApprovalPlan(BaseModel):
    plan_id: str
    remediation_id: str
    status: PlanStatus
    owner: str
    approver: str
    target_kpi: str
    baseline: float
    target: float
    stop_condition: str
    version: int


class AuditEvent(BaseModel):
    entity_id: str
    occurred_at: datetime
    actor: str
    action: str
    previous_status: PlanStatus
    new_status: PlanStatus
    reason: str
    previous_version: int
    new_version: int


_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"needs_evidence", "ready_for_review", "cancelled"},
    "needs_evidence": {"ready_for_review", "rejected", "cancelled"},
    "ready_for_review": {"needs_evidence", "approved_pilot", "rejected", "cancelled"},
    "approved_pilot": {"in_progress", "cancelled"},
    "in_progress": {"measured", "cancelled"},
    "measured": {"closed"},
    "rejected": set(),
    "cancelled": set(),
    "closed": set(),
}


def transition_plan(
    plan: ApprovalPlan,
    *,
    target_status: PlanStatus,
    actor: str,
    reason: str,
    occurred_at: datetime,
) -> tuple[ApprovalPlan, AuditEvent]:
    if target_status not in _ALLOWED_TRANSITIONS[plan.status]:
        raise ValueError(f"invalid plan transition: {plan.status} -> {target_status}")
    updated = plan.model_copy(update={"status": target_status, "version": plan.version + 1})
    event = AuditEvent(
        entity_id=plan.plan_id,
        occurred_at=occurred_at,
        actor=actor,
        action="plan_status_changed",
        previous_status=plan.status,
        new_status=target_status,
        reason=reason,
        previous_version=plan.version,
        new_version=updated.version,
    )
    return updated, event
