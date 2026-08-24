from app.approvals.state_machine import ApprovalPlan
from app.remediation.playbook import find_remediations
from app.remediation.ranker import ScoreInputs, score_remediation

_LIMITATIONS = [
    "CFPB complaints are observed signals, not a statistical sample of all customers.",
    "Northstar Bank records and economics are synthetic demonstration data.",
    "This workflow recommends a bounded pilot, not an automated customer decision.",
]


def build_demo_view() -> dict:
    options = find_remediations("purchase_disputes", "delayed_resolution")
    option_inputs = {
        "proactive-dispute-status": ScoreInputs(
            internal_signal=82,
            external_signal=68,
            harm_severity=72,
            cost_to_serve=64,
            evidence_confidence=88,
            strategic_fit=76,
            feasibility=84,
        ),
        "specialist-dispute-queue": ScoreInputs(
            internal_signal=82,
            external_signal=68,
            harm_severity=78,
            cost_to_serve=70,
            evidence_confidence=88,
            strategic_fit=72,
            feasibility=52,
        ),
    }
    ranked = []
    for option in options:
        assessment = score_remediation(option.id, option_inputs[option.id])
        ranked.append({**option.model_dump(), **assessment.model_dump()})
    ranked.sort(key=lambda item: item["score"], reverse=True)

    plan = ApprovalPlan(
        plan_id="northstar-dispute-pilot",
        remediation_id=ranked[0]["id"],
        status="ready_for_review",
        owner="Disputes Operations",
        approver="Chief Operating Officer",
        target_kpi="repeat_contact_rate",
        baseline=24.0,
        target=18.0,
        stop_condition="Incorrect status notification rate exceeds 1%",
        version=1,
    )
    return {
        "signal": {
            "id": "signal-delayed-disputes",
            "title": "Delayed purchase-dispute resolution",
            "status": "emerging",
            "process_stage": "purchase_disputes",
            "failure_mode": "delayed_resolution",
            "external_source": "cfpb",
            "internal_source": "northstar_synthetic",
            "external_change_ratio": 1.8,
            "internal_change_ratio": 2.4,
            "confidence": 0.88,
            "plain_language": (
                "Observed dispute-delay complaints increased externally and are corroborated "
                "by a fictional rise in Northstar repeat contacts and SLA breaches."
            ),
        },
        "evidence": [
            {
                "role": "central",
                "source": "cfpb",
                "complaint_id": "8089105",
                "excerpt": "I have contacted Apple Card several times with no success.",
                "source_url": (
                    "https://www.consumerfinance.gov/data-research/consumer-complaints/"
                    "search/api/v1/8089105"
                ),
            },
            {
                "role": "diverse",
                "source": "cfpb",
                "complaint_id": "8088634",
                "excerpt": "We never received such a letter.",
                "source_url": (
                    "https://www.consumerfinance.gov/data-research/consumer-complaints/"
                    "search/api/v1/8088634"
                ),
            },
            {
                "role": "counter",
                "source": "northstar_synthetic",
                "complaint_id": "NS-DEMO-COUNTER-1",
                "excerpt": "The dispute was resolved the next day.",
                "source_url": None,
            },
        ],
        "remediations": ranked,
        "plan": plan.model_dump(),
        "audit": [],
        "limitations": _LIMITATIONS,
    }
