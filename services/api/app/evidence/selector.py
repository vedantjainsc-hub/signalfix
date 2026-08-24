from pydantic import BaseModel, Field


class EvidenceCandidate(BaseModel):
    complaint_id: str
    source_text: str
    evidence_span: str
    similarity: float = Field(ge=0, le=1)
    contradicts_theme: bool


class EvidenceSelection(BaseModel):
    central: EvidenceCandidate
    diverse: EvidenceCandidate
    counter: EvidenceCandidate


def select_evidence(candidates: list[EvidenceCandidate]) -> EvidenceSelection:
    for candidate in candidates:
        if candidate.evidence_span not in candidate.source_text:
            raise ValueError(
                f"evidence span is not grounded in complaint {candidate.complaint_id}"
            )

    supporting = [candidate for candidate in candidates if not candidate.contradicts_theme]
    counter = [candidate for candidate in candidates if candidate.contradicts_theme]
    if len(supporting) < 2 or not counter:
        raise ValueError("at least two supporting and one counter candidate are required")

    return EvidenceSelection(
        central=max(supporting, key=lambda candidate: candidate.similarity),
        diverse=min(supporting, key=lambda candidate: candidate.similarity),
        counter=max(counter, key=lambda candidate: candidate.similarity),
    )
