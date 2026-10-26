from contextlib import contextmanager
from enum import Enum, unique
from functools import cached_property, total_ordering
from typing import Any, Self

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from maloen_commande.settings import settings

engine = create_engine(str(settings.db_url))


@contextmanager
def transactional():
    with Session(engine) as session, session.begin():
        yield session


def enum_values(t: type[Enum]):
    """Sequence of values of an enumeration.

    Useful for passing to `sqlalchemy.Enum(values_callable)` so that enum variants are persisted their value instead of their name.
    """
    return [e.value for e in t]


class Base(DeclarativeBase):
    metadata = MetaData(schema="bdd_coordination_schema")


@unique
@total_ordering
class DayOfWeek(Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @classmethod
    def weekdays(cls) -> list[Self]:
        return list(cls)[:5]

    @classmethod
    def weekend(cls) -> list[Self]:
        return list(cls)[5:]

    @cached_property
    def key(self) -> int:
        return list(DayOfWeek).index(self)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, DayOfWeek):
            return NotImplemented

        return self.key < other.key
