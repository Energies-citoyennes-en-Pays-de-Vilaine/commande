from dataclasses import dataclass
from datetime import time
from enum import Enum
from typing import Any, Generator

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from maloen_commande.domain.base import Base, DayOfWeek, enum_values, transactional
from maloen_commande.domain.device import Device
from maloen_commande.domain.home_automation_device import HomeAutomationDevice


class Cohort(Base):
    __tablename__ = "cohorte_utilisateurs"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(name="nom")
    description: Mapped[str]
    forecast_id: Mapped[str] = mapped_column(name="prevision_id")


class CohortRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, id: str) -> Cohort | None:
        return self.session.query(Cohort).where(Cohort.id == id).one_or_none()

    def insert(self, cohort: Cohort):
        self.session.add(cohort)


def cohort_repository() -> Generator[CohortRepository]:
    with transactional() as session:
        yield CohortRepository(session)


class User(Base):
    __tablename__ = "utilisateur"

    id: Mapped[str] = mapped_column(primary_key=True)
    cohort_id: Mapped[str] = mapped_column(name="cohorte")
    electricity_tariff_schedule: Mapped[list[ElectricityRatePeriod]] = relationship(
        cascade="all, delete-orphan"
    )
    devices: Mapped[list[Device]] = relationship(cascade="all, delete-orphan")
    home_automation_devices: Mapped[list[HomeAutomationDevice]] = relationship(
        cascade="all, delete-orphan"
    )

    def update_electricity_tariff_schedule(self, schedule: list[ElectricityRatePeriod]):
        self.electricity_tariff_schedule.clear()
        self.electricity_tariff_schedule.extend(schedule)


class ElectricityRate(Enum):
    PEAK = "peak"
    OFF_PEAK = "off_peak"


class ElectricityRatePeriod(Base):
    __tablename__ = "utilisateur_plage_tarifaire_electricite"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("utilisateur.id"), name="utilisateur_id", primary_key=True
    )
    day: Mapped[DayOfWeek] = mapped_column(
        SqlEnum(DayOfWeek, values_callable=enum_values),
        name="jour",
        primary_key=True,
    )
    from_: Mapped[time] = mapped_column(name="debut", primary_key=True)
    to: Mapped[time] = mapped_column(name="fin")
    rate: Mapped[ElectricityRate] = mapped_column(
        SqlEnum(ElectricityRate, values_callable=enum_values), name="prix"
    )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ElectricityRatePeriod):
            return NotImplemented
        return (self.day, self.from_, self.to, self.rate) == (
            other.day,
            other.from_,
            other.to,
            other.rate,
        )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(day={self.day.value}, from={self.from_}, to={self.to}, rate={self.rate.value})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(day={self.day}, from_={self.from_}, to={self.to}, rate={self.rate})"


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, id: str) -> User | None:
        return self.session.query(User).where(User.id == id).one_or_none()

    def find_all_by_cohort(self, cohort_id: str) -> list[User]:
        return self.session.query(User).where(User.cohort_id == cohort_id).all()

    def find_by_cofybox(self, cofybox_id: str) -> User | None:
        return (
            self.session.query(User)
            .where(
                User.home_automation_devices.any(HomeAutomationDevice.id == cofybox_id)
            )
            .one_or_none()
        )

    def find_by_home_automation_device(self, device_id: str) -> User | None:
        return (
            self.session.query(User)
            .where(
                User.home_automation_devices.any(HomeAutomationDevice.id == device_id)
            )
            .one_or_none()
        )

    def insert(self, user: User):
        self.session.add(user)


def user_repository() -> Generator[UserRepository]:
    with transactional() as session:
        yield UserRepository(session)
