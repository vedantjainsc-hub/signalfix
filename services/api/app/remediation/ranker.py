from pydantic import BaseModel, Field

DEFAULT_WEIGHTS: dict[str, float] = {
    "internal_signal": 0.20,
    "external_signal": 0.15,
    "harm_severity": 0.20,
    "cost_to_serve": 0.15,
    "evidence_confidence": 0.10,
    "strategic_fit": 0.10,
    "feasibility": 0.10,
}


class ScoreInputs(BaseModel):
    internal_signal: float = Field(ge=0, le=100)
    external_signal: float = Field(ge=0, le=100)
    harm_severity: float = Field(ge=0, le=100)
    cost_to_serve: float = Field(ge=0, le=100)
    evidence_confidence: float = Field(ge=0, le=100)
    strategic_fit: float = Field(ge=0, le=100)
    feasibility: float = Field(ge=0, le=100)


class PriorityAssessment(BaseModel):
    remediation_id: str
    score: float
    weights: dict[str, float]
    contributions: dict[str, float]


def score_remediation(remediation_id: str, inputs: ScoreInputs) -> PriorityAssessment:
    contributions = {
        name: round(getattr(inputs, name) * weight, 4)
        for name, weight in DEFAULT_WEIGHTS.items()
    }
    return PriorityAssessment(
        remediation_id=remediation_id,
        score=round(sum(contributions.values()), 4),
        weights=DEFAULT_WEIGHTS,
        contributions=contributions,
    )
