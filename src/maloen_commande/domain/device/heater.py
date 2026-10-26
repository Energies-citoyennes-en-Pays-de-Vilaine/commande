from datetime import time
from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maloen_commande.domain.base import Base, DayOfWeek, enum_values
from maloen_commande.domain.device import Device


class HeaterMode(Enum):
    ECO = "eco"
    COMFORT = "comfort"


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
