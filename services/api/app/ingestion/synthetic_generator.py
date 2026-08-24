import random
from datetime import UTC, date, datetime, timedelta

from app.schemas.northstar_case import NorthstarCase

_SCENARIOS = (
    (
        "purchase_disputes",
        "delayed_resolution",
        "Disputes Operations",
        (
            "I submitted the requested documents but the dispute status has not changed.",
            "The purchase dispute is still pending after several contacts with support.",
        ),
    ),
    (
        "billing",
        "incorrect_fee_or_charge",
        "Billing Operations",
        (
            "A fee appeared after I was told the account qualified for a waiver.",
            "The statement includes a charge that does not match the disclosed terms.",
        ),
    ),
    (
        "fraud_security",
        "handoff_failure",
        "Fraud Operations",
        (
            "I was transferred between support teams and had to repeat the fraud report.",
            "The fraud case was handed off but the next team could not see the prior notes.",
        ),
    ),
    (
        "payments",
        "system_or_process_error",
        "Payments Operations",
        (
            "The payment showed as accepted and later appeared as missing.",
            "The account balance did not update after the scheduled payment completed.",
        ),
    ),
)
_CHANNELS = ("web", "phone", "chat", "branch")


def generate_northstar_cases(
    *,
    count: int,
    seed: int,
    start_date: date,
    end_date: date,
    surge_failure_mode: str | None = None,
    surge_start_date: date | None = None,
) -> list[NorthstarCase]:
    if count < 0:
        raise ValueError("count must be non-negative")
    if end_date < start_date:
        raise ValueError("end_date must not precede start_date")

    rng = random.Random(seed)
    span_days = (end_date - start_date).days
    cases: list[NorthstarCase] = []

    for index in range(count):
        received_date = start_date + timedelta(days=rng.randint(0, span_days))
        weights = [1.0] * len(_SCENARIOS)
        if surge_failure_mode and surge_start_date and received_date >= surge_start_date:
            weights = [5.0 if scenario[1] == surge_failure_mode else 1.0 for scenario in _SCENARIOS]
        process_stage, failure_mode, owner_role, templates = rng.choices(
            _SCENARIOS, weights=weights, k=1
        )[0]
        handle_minutes = rng.randint(8, 75)
        repeat_contact = rng.random() < 0.28
        escalated = rng.random() < 0.14
        sla_breach = rng.random() < 0.18
        estimated_cost = round(
            handle_minutes * 0.85 + repeat_contact * 18 + escalated * 35 + sla_breach * 12,
            2,
        )
        cases.append(
            NorthstarCase(
                case_id=f"NS-{seed}-{index + 1:06d}",
                received_at=datetime.combine(received_date, datetime.min.time(), tzinfo=UTC),
                channel=rng.choice(_CHANNELS),
                process_stage=process_stage,
                failure_mode=failure_mode,
                narrative=rng.choice(templates),
                handle_minutes=handle_minutes,
                repeat_contact=repeat_contact,
                escalated=escalated,
                sla_breach=sla_breach,
                estimated_cost_usd=estimated_cost,
                owner_role=owner_role,
            )
        )

    return sorted(cases, key=lambda case: (case.received_at, case.case_id))
