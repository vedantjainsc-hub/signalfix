import re
from typing import Literal

from pydantic import BaseModel


class PrivacyScreenResult(BaseModel):
    status: Literal["passed", "masked", "quarantined"]
    sanitized_text: str | None
    findings: list[str]


_MASK_PATTERNS = (
    (
        "email",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        "[REDACTED_EMAIL]",
    ),
    (
        "phone",
        re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
        "[REDACTED_PHONE]",
    ),
)


_SSN_LIKE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def screen_narrative(text: str) -> PrivacyScreenResult:
    if not text.strip():
        return PrivacyScreenResult(status="quarantined", sanitized_text=None, findings=["empty"])
    if _SSN_LIKE.search(text):
        return PrivacyScreenResult(
            status="quarantined", sanitized_text=None, findings=["ssn_like"]
        )

    sanitized = text
    findings: list[str] = []
    for name, pattern, replacement in _MASK_PATTERNS:
        sanitized, count = pattern.subn(replacement, sanitized)
        if count:
            findings.append(name)

    return PrivacyScreenResult(
        status="masked" if findings else "passed",
        sanitized_text=sanitized,
        findings=findings,
    )
