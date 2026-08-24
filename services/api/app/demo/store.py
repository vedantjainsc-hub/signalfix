from datetime import UTC, datetime

from app.approvals.state_machine import ApprovalPlan, AuditEvent, transition_plan
from app.demo.service import build_demo_view


class DemoStore:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> dict:
        view = build_demo_view()
        self._base_view = {
            key: value for key, value in view.items() if key not in {"plan", "audit"}
        }
        self._plan = ApprovalPlan.model_validate(view["plan"])
        self._audit: list[AuditEvent] = []
        return self.view()

    def view(self) -> dict:
        return {
            **self._base_view,
            "plan": self._plan.model_dump(),
            "audit": [event.model_dump() for event in self._audit],
        }

    def approve(self, plan_id: str, actor: str, reason: str) -> tuple[ApprovalPlan, AuditEvent]:
        if plan_id != self._plan.plan_id:
            raise KeyError(plan_id)
        self._plan, event = transition_plan(
            self._plan,
            target_status="approved_pilot",
            actor=actor,
            reason=reason,
            occurred_at=datetime.now(UTC),
        )
        self._audit.append(event)
        return self._plan, event


demo_store = DemoStore()
