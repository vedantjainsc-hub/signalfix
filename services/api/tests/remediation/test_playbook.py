from app.remediation.playbook import find_remediations


def test_find_remediations_returns_controlled_options_for_delayed_resolution() -> None:
    options = find_remediations("purchase_disputes", "delayed_resolution")

    assert [option.id for option in options] == [
        "proactive-dispute-status",
        "specialist-dispute-queue",
    ]
    assert all(option.owner_role for option in options)
    assert all(option.target_kpis for option in options)
    assert all(option.guardrails for option in options)
    assert all(option.stop_conditions for option in options)
