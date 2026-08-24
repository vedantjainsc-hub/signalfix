from app.privacy.scrubber import screen_narrative


def test_screen_narrative_masks_contact_information() -> None:
    result = screen_narrative(
        "Please contact me at person@example.com or 212-555-0199 about the dispute."
    )

    assert result.status == "masked"
    assert result.sanitized_text == (
        "Please contact me at [REDACTED_EMAIL] or [REDACTED_PHONE] about the dispute."
    )
    assert result.findings == ["email", "phone"]


def test_screen_narrative_quarantines_ssn_like_identifier() -> None:
    result = screen_narrative("My identifier is 123-45-6789 and the account is still blocked.")

    assert result.status == "quarantined"
    assert result.sanitized_text is None
    assert result.findings == ["ssn_like"]


def test_screen_narrative_quarantines_empty_text() -> None:
    result = screen_narrative("   ")

    assert result.status == "quarantined"
    assert result.sanitized_text is None
    assert result.findings == ["empty"]
