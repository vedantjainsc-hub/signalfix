from datetime import UTC, datetime

import pytest

from app.approvals.state_machine import ApprovalPlan, transition_plan


def test_transition_plan_creates_audit_event_for_valid_approval() -> None:
    plan = ApprovalPlan(
        plan_id="plan-1",
        remediation_id="proactive-dispute-status",
        status="ready_for_review",
        owner="Disputes Operations",
        approver="COO",
        target_kpi="repeat_contact_rate",
        baseline=24.0,
        target=18.0,
        stop_condition="Incorrect status rate exceeds 1%",
        version=1,
    )

    updated, event = transition_plan(
        plan,
        target_status="approved_pilot",
        actor="demo-operations-director",
        reason="Evidence and guardrails reviewed",
        occurred_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC),
    )

    assert updated.status == "approved_pilot"
    assert updated.version == 2
    assert event.entity_id == "plan-1"
    assert event.previous_status == "ready_for_review"
    assert event.new_status == "approved_pilot"
    assert event.actor == "demo-operations-director"
    assert event.reason == "Evidence and guardrails reviewed"


def test_transition_plan_rejects_skipping_required_review() -> None:
    plan = ApprovalPlan(
        plan_id="plan-1",
        remediation_id="proactive-dispute-status",
        status="draft",
        owner="Disputes Operations",
        approver="COO",
        target_kpi="repeat_contact_rate",
        baseline=24.0,
        target=18.0,
        stop_condition="Incorrect status rate exceeds 1%",
        version=1,
    )

    with pytest.raises(ValueError, match="draft -> approved_pilot"):
        transition_plan(
            plan,
            target_status="approved_pilot",
            actor="demo-operations-director",
            reason="Skip review",
            occurred_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC),
        )
