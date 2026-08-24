from typing import Literal

from pydantic import BaseModel


class RemediationOption(BaseModel):
    id: str
    title: str
    mechanism: str
    owner_role: str
    effort_band: Literal["low", "medium", "high"]
    lead_time_weeks: tuple[int, int]
    target_kpis: list[str]
    guardrails: list[str]
    stop_conditions: list[str]


_PLAYBOOK = {
    ("purchase_disputes", "delayed_resolution"): [
        RemediationOption(
            id="proactive-dispute-status",
            title="Proactive dispute-status notifications",
            mechanism=(
                "Send milestone updates when evidence is received, review begins, and a decision "
                "is delayed."
            ),
            owner_role="Disputes Operations",
            effort_band="medium",
            lead_time_weeks=(4, 6),
            target_kpis=["repeat_contact_rate", "status_inquiry_volume", "resolution_time"],
            guardrails=["Do not promise a resolution date", "Preserve required disclosures"],
            stop_conditions=["Incorrect status rate exceeds 1%"],
        ),
        RemediationOption(
            id="specialist-dispute-queue",
            title="Specialist queue for aged disputes",
            mechanism="Route disputes beyond a defined age to a specialist review queue.",
            owner_role="Disputes Operations",
            effort_band="high",
            lead_time_weeks=(6, 10),
            target_kpis=["aged_case_volume", "resolution_time", "reopen_rate"],
            guardrails=["Apply queue rules consistently", "Monitor downstream backlog"],
            stop_conditions=["Standard queue service level falls below target"],
        ),
    ]
}


def find_remediations(process_stage: str, failure_mode: str) -> list[RemediationOption]:
    return list(_PLAYBOOK.get((process_stage, failure_mode), []))
