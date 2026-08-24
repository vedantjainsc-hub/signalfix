from datetime import date
from statistics import mean
from typing import Literal

from pydantic import BaseModel, Field


class WeeklyObservation(BaseModel):
    week: date
    theme_count: int = Field(ge=0)
    total_count: int = Field(gt=0)

    @property
    def share(self) -> float:
        return self.theme_count / self.total_count


class TrendSignal(BaseModel):
    as_of: date
    status: Literal["emerging", "stable", "insufficient_data"]
    current_share: float
    baseline_share: float | None
    change_ratio: float | None
    current_count: int
    baseline_weeks: int


def detect_trend_at(
    observations: list[WeeklyObservation],
    *,
    as_of: date,
    baseline_weeks: int,
    minimum_count: int,
    emerging_ratio: float,
) -> TrendSignal:
    available = sorted(
        (observation for observation in observations if observation.week <= as_of),
        key=lambda observation: observation.week,
    )
    current = next((item for item in reversed(available) if item.week == as_of), None)
    if current is None:
        raise ValueError("an observation is required for the as_of date")

    baseline = [item for item in available if item.week < as_of][-baseline_weeks:]
    if len(baseline) < baseline_weeks:
        return TrendSignal(
            as_of=as_of,
            status="insufficient_data",
            current_share=current.share,
            baseline_share=None,
            change_ratio=None,
            current_count=current.theme_count,
            baseline_weeks=len(baseline),
        )
    baseline_share = mean(item.share for item in baseline)
    change_ratio = current.share / baseline_share if baseline_share else None
    is_emerging = (
        current.theme_count >= minimum_count
        and change_ratio is not None
        and change_ratio >= emerging_ratio
    )
    return TrendSignal(
        as_of=as_of,
        status="emerging" if is_emerging else "stable",
        current_share=round(current.share, 6),
        baseline_share=round(baseline_share, 6),
        change_ratio=round(change_ratio, 6) if change_ratio is not None else None,
        current_count=current.theme_count,
        baseline_weeks=len(baseline),
    )
