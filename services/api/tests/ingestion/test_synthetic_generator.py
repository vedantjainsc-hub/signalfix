from datetime import date

from app.ingestion.synthetic_generator import generate_northstar_cases


def test_generate_northstar_cases_is_reproducible_and_clearly_synthetic() -> None:
    first = generate_northstar_cases(
        count=20,
        seed=42,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
    )
    second = generate_northstar_cases(
        count=20,
        seed=42,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
    )

    assert first == second
    assert len(first) == 20
    assert len({case.case_id for case in first}) == 20
    assert all(case.source == "northstar_synthetic" for case in first)
    assert all(case.case_id.startswith("NS-42-") for case in first)
    assert all(date(2024, 1, 1) <= case.received_at.date() <= date(2024, 3, 31) for case in first)
    assert all("Northstar" not in case.narrative for case in first)


def test_generate_northstar_cases_can_model_an_emerging_internal_signal() -> None:
    surge_start = date(2024, 10, 1)
    cases = generate_northstar_cases(
        count=2_000,
        seed=7,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        surge_failure_mode="delayed_resolution",
        surge_start_date=surge_start,
    )

    before = [case for case in cases if case.received_at.date() < surge_start]
    after = [case for case in cases if case.received_at.date() >= surge_start]
    before_share = sum(case.failure_mode == "delayed_resolution" for case in before) / len(before)
    after_share = sum(case.failure_mode == "delayed_resolution" for case in after) / len(after)

    assert after_share > before_share + 0.25
