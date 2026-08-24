from datetime import date

from app.trends.detector import WeeklyObservation, detect_trend_at


def test_detect_trend_uses_only_weeks_on_or_before_as_of_date() -> None:
    observations = [
        WeeklyObservation(week=date(2024, 1, 1), theme_count=10, total_count=100),
        WeeklyObservation(week=date(2024, 1, 8), theme_count=10, total_count=100),
        WeeklyObservation(week=date(2024, 1, 15), theme_count=10, total_count=100),
        WeeklyObservation(week=date(2024, 1, 22), theme_count=10, total_count=100),
        WeeklyObservation(week=date(2024, 1, 29), theme_count=30, total_count=100),
        WeeklyObservation(week=date(2024, 2, 5), theme_count=1, total_count=100),
    ]

    signal = detect_trend_at(
        observations,
        as_of=date(2024, 1, 29),
        baseline_weeks=4,
        minimum_count=5,
        emerging_ratio=1.5,
    )

    assert signal.status == "emerging"
    assert signal.current_share == 0.3
    assert signal.baseline_share == 0.1
    assert signal.change_ratio == 3.0
    assert signal.as_of == date(2024, 1, 29)


def test_detect_trend_reports_insufficient_baseline() -> None:
    observations = [
        WeeklyObservation(week=date(2024, 1, 1), theme_count=2, total_count=100),
        WeeklyObservation(week=date(2024, 1, 8), theme_count=8, total_count=100),
    ]

    signal = detect_trend_at(
        observations,
        as_of=date(2024, 1, 8),
        baseline_weeks=4,
        minimum_count=5,
        emerging_ratio=1.5,
    )

    assert signal.status == "insufficient_data"
    assert signal.baseline_share is None
    assert signal.change_ratio is None
    assert signal.baseline_weeks == 1
