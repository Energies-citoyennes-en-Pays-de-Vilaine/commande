from contextlib import contextmanager
from datetime import time
from enum import Enum, unique
from functools import cached_property, total_ordering
from typing import Any, Generator

from sqlalchemy import URL, ForeignKey, create_engine
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)

engine = create_engine(
    URL.create(
        drivername="postgresql+psycopg2",
        host="localhost",
        database="commande",
        username="commande",
        password="commande",
    ),
    connect_args={"options": "-csearch_path=bdd_coordination_schema"},
)


@contextmanager
def transactional():
    with Session(engine) as session, session.begin():
        yield session


class Base(DeclarativeBase):
    pass


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

    @cached_property
    def key(self) -> int:
        return list(DayOfWeek).index(self)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, DayOfWeek):
            return NotImplemented

        return self.key < other.key


class ElectricityRate(Enum):
    PEAK = "peak"
    OFF_PEAK = "off_peak"


class HeaterMode(Enum):
    ECO = "eco"
    COMFORT = "comfort"


class DeviceTypology(Enum):
    DEUX_RELAIS = 110
    PRISE_COMMANDE = 120
    PRISE_ET_DOIGT = 130
    RELAI_ET_CAPTEUR_TEMPERATURE = 140
    PRISE_ET_DEUX_DOIGTS = 150
    PRISE_ET_DOIGT_DOUBLE_APPUI = 160
    PRISE_RALLUME_ET_DOIGT = 170
    RELAI_ET_COMPTEUR = 180
    RELAI_INVERSE = 190
    TIC = 200


class DeviceMode(Enum):
    NOT_MANAGED = 1
    INSTALLING = 10
    MANUAL = 20
    MANAGED = 30
    DEACTIVATED = 70
    DELETED = 80


class MonitorState(Enum):
    ON = 15
    OFF = 25
    COMMUNICATION_ERROR = 60
    UNKNOWN = 70


class CommandState(Enum):
    INITIAL = 1
    MANAGED_STAND_BY = 11
    MANUAL_OR_MANAGED_ON = 12
    MANUAL_ON = 13
    MANAGED_ACTIVATING = 21
    ERROR = 30
    NOT_MANAGED = 99


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
    devices: Mapped[list[Device]] = relationship()


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, id: str) -> User | None:
        return self.session.query(User).where(User.id == id).one_or_none()

    def find_all_by_cohort(self, cohort_id: str) -> list[User]:
        return self.session.query(User).where(User.cohort_id == cohort_id).all()

    def insert(self, user: User):
        self.session.add(user)


def user_repository() -> Generator[UserRepository]:
    with transactional() as session:
        yield UserRepository(session)


def enum_values(t):
    return [e.value for e in t]


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


class Device(Base):
    __tablename__ = "equipement_pilote_ou_mesure"
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": 1,
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[int] = mapped_column(name="equipement_pilote_ou_mesure_type_id")
    specific_id: Mapped[int] = mapped_column(name="equipement_pilote_specifique_id")
    user_id: Mapped[str] = mapped_column(
        ForeignKey("utilisateur.id"), name="utilisateur"
    )
    name: Mapped[str] = mapped_column(name="nom_humain")
    description: Mapped[str]
    typology: Mapped[int] = mapped_column(name="typologie_installation_domotique_id")
    mode: Mapped[int] = mapped_column(name="equipement_pilote_ou_mesure_mode_id")
    monitor_state: Mapped[int] = mapped_column(name="etat_controle_id")
    command_state: Mapped[int] = mapped_column(name="etat_commande_id")
    ems_recommends_activation: Mapped[bool] = mapped_column(name="ems_consigne_marche")
    last_activated_at: Mapped[int] = mapped_column(
        name="timestamp_derniere_mise_en_marche"
    )
    last_programmed_at: Mapped[int] = mapped_column(
        name="timestamp_derniere_programmation"
    )


class Heater(Device):
    __tablename__ = "equipement_pilote_chauffage_non_asservi"
    __mapper_args__ = {
        "polymorphic_identity": 151,
    }
    id: Mapped[int] = mapped_column(
        ForeignKey("equipement_pilote_ou_mesure.id"), primary_key=True
    )
    device_id: Mapped[int] = mapped_column(name="equipement_pilote_ou_mesure_id")
    prog_semaine_periode_1_confort_actif: Mapped[bool] = mapped_column(
        name="prog_semaine_periode_1_confort_actif", default=False
    )
    prog_semaine_periode_1_confort_heure_debut: Mapped[int] = mapped_column(
        name="prog_semaine_periode_1_confort_heure_debut", default=1
    )
    prog_semaine_periode_1_confort_heure_fin: Mapped[int] = mapped_column(
        name="prog_semaine_periode_1_confort_heure_fin", default=1
    )
    prog_semaine_periode_2_confort_actif: Mapped[bool] = mapped_column(
        name="prog_semaine_periode_2_confort_actif", default=False
    )
    prog_semaine_periode_2_confort_heure_debut: Mapped[int] = mapped_column(
        name="prog_semaine_periode_2_confort_heure_debut", default=1
    )
    prog_semaine_periode_2_confort_heure_fin: Mapped[int] = mapped_column(
        name="prog_semaine_periode_2_confort_heure_fin", default=1
    )
    prog_weekend_periode_1_confort_actif: Mapped[bool] = mapped_column(
        name="prog_weekend_periode_1_confort_actif", default=False
    )
    prog_weekend_periode_1_confort_heure_debut: Mapped[int] = mapped_column(
        name="prog_weekend_periode_1_confort_heure_debut", default=1
    )
    prog_weekend_periode_1_confort_heure_fin: Mapped[int] = mapped_column(
        name="prog_weekend_periode_1_confort_heure_fin", default=1
    )
    prog_weekend_periode_2_confort_actif: Mapped[bool] = mapped_column(
        name="prog_weekend_periode_2_confort_actif", default=False
    )
    prog_weekend_periode_2_confort_heure_debut: Mapped[int] = mapped_column(
        name="prog_weekend_periode_2_confort_heure_debut", default=1
    )
    prog_weekend_periode_2_confort_heure_fin: Mapped[int] = mapped_column(
        name="prog_weekend_periode_2_confort_heure_fin", default=1
    )
    avg_eco_power: Mapped[int] = mapped_column(name="puissance_moyenne_eco", default=1)
    avg_comfort_power: Mapped[int] = mapped_column(
        name="puissance_moyenne_confort", default=1
    )
    forced_eco_pct: Mapped[int] = mapped_column(name="pourcentage_eco_force", default=1)
    mesures_id: Mapped[int] = mapped_column(name="mesures_puissance_elec_id", default=1)
    schedule: Mapped[list[HeaterModePeriod]] = relationship(
        cascade="all, delete-orphan"
    )


class HeaterModePeriod(Base):
    __tablename__ = "equipement_pilote_planning_chauffage"
    device_id: Mapped[int] = mapped_column(
        ForeignKey("equipement_pilote_ou_mesure.id"),
        name="equipement_pilote_ou_mesure_id",
        primary_key=True,
    )
    day: Mapped[DayOfWeek] = mapped_column(
        SqlEnum(DayOfWeek, values_callable=enum_values),
        name="jour",
        primary_key=True,
    )
    from_: Mapped[time] = mapped_column(name="debut", primary_key=True)
    to: Mapped[time] = mapped_column(name="fin")
    mode: Mapped[HeaterMode] = mapped_column(
        SqlEnum(HeaterMode, values_callable=enum_values)
    )


class ElectricVehicle(Device):
    __tablename__ = "equipement_pilote_vehicule_electrique_generique"
    __mapper_args__ = {
        "polymorphic_identity": 221,
    }
    id: Mapped[int] = mapped_column(
        ForeignKey("equipement_pilote_ou_mesure.id"), primary_key=True
    )
