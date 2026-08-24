from pydantic import BaseModel, Field


class TaxonomyClassification(BaseModel):
    process_stage: str
    failure_mode: str
    confidence: float = Field(ge=0, le=1)
    needs_review: bool
    source: str = "cfpb_crosswalk_v0.1"


_RULES = {
    (
        "Problem with a purchase shown on your statement",
        "Credit card company isn't resolving a dispute about a purchase on your statement",
    ): ("purchase_disputes", "delayed_resolution"),
}


def classify_with_crosswalk(issue: str | None, sub_issue: str | None) -> TaxonomyClassification:
    match = _RULES.get((issue or "", sub_issue or ""))
    if match is None:
        return TaxonomyClassification(
            process_stage="unknown",
            failure_mode="unknown",
            confidence=0.0,
            needs_review=True,
        )
    process_stage, failure_mode = match
    return TaxonomyClassification(
        process_stage=process_stage,
        failure_mode=failure_mode,
        confidence=0.9,
        needs_review=False,
    )
