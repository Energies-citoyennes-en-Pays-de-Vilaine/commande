import logging
from datetime import time
from functools import total_ordering
from itertools import groupby
from typing import Annotated, Any, Self

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from maloen_commande import domain
from maloen_commande.domain import (
    DayOfWeek,
    ElectricityRate,
    Heater,
    HeaterMode,
    UserRepository,
    user_repository,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cohorts/{cohort_id}/schedules")


@total_ordering
class SchedulePeriod(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: Annotated[time, Field(alias="from")]
    to: time

    @model_validator(mode="after")
    def check_from_before_to(self) -> Self:
        if self.from_ > self.to:
            raise ValueError(
                "The start of a period (from) should be before the end (to)"
            )
        return self

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, SchedulePeriod):
            return NotImplemented
        return (self.from_, self.to) < (other.from_, other.to)


class ElectricityRatePeriod(SchedulePeriod):
    rate: ElectricityRate


class HeaterModePeriod(SchedulePeriod):
    mode: HeaterMode


type WeeklySchedule[T] = dict[DayOfWeek, list[T]]


class HeaterSchedule(BaseModel):
    id: int
    schedule: WeeklySchedule[HeaterModePeriod]


class UserSchedule(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    electricity_tariff_schedule: WeeklySchedule[ElectricityRatePeriod]
    heaters: list[HeaterSchedule]


class CohortSchedules(BaseModel):
    id: str
    users: list[UserSchedule]


type UserRepositoryDep = Annotated[UserRepository, Depends(user_repository)]


@router.get("")
def get_all_cohort_schedules(
    cohort_id: str, user_repository: UserRepositoryDep
) -> CohortSchedules:
    users = user_repository.find_all_by_cohort(cohort_id)

    return CohortSchedules(
        id=cohort_id,
        users=[
            UserSchedule(
                id=user.id,
                electricity_tariff_schedule={
                    day: [
                        ElectricityRatePeriod(
                            from_=p.from_,
                            to=p.to,
                            rate=p.rate,
                        )
                        for p in g
                    ]
                    for day, g in groupby(
                        sorted(user.electricity_tariff_schedule, key=lambda p: p.day),
                        key=lambda p: p.day,
                    )
                },
                heaters=[
                    HeaterSchedule(
                        id=heater.id,
                        schedule={
                            day: [
                                HeaterModePeriod(from_=p.from_, to=p.to, mode=p.mode)
                                for p in g
                            ]
                            for day, g in groupby(
                                sorted(heater.schedule, key=lambda p: p.day),
                                key=lambda p: p.day,
                            )
                        },
                    )
                    for heater in user.devices
                    if isinstance(heater, Heater)
                ],
            )
            for user in users
        ],
    )
