from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class HaspPageId(Enum):
    WEEKDAY_HEATING_SCHEDULE = 2
    WEEKEND_HEATING_SCHEDULE = 3
    WEEKDAY_OFF_PEAK_ELEC = 4
    WEEKEND_OFF_PEAK_ELEC = 5
    ELECTRIC_VEHICLE = 6


class HaspEventType(Enum):
    CHANGED = "changed"
    UP = "up"
    DOWN = "down"


class HaspEvent(BaseModel):
    type: Annotated[HaspEventType, Field(alias="event")]
    val: int
    text: str | None = None
