from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from maloen_commande.domain.device import Device


class ElectricVehicle(Device):
    __tablename__ = "equipement_pilote_vehicule_electrique_generique"
    __mapper_args__ = {
        "polymorphic_identity": 221,
    }
    id: Mapped[int] = mapped_column(
        ForeignKey("equipement_pilote_ou_mesure.id"), primary_key=True
    )
    device_id: Mapped[int] = mapped_column(name="equipement_pilote_ou_mesure_id")
    remaining_charge_percentage: Mapped[int] = mapped_column(
        name="pourcentage_charge_restant"
    )
    minimum_desired_charge_percentage: Mapped[int] = mapped_column(
        name="pourcentage_charge_finale_minimale_souhaitee"
    )
    estimated_charging_time: Mapped[int] = mapped_column(name="duree_de_charge_estimee")
    deadline_timestamp: Mapped[int] = mapped_column(name="timestamp_dispo_souhaitee")
    charging_power: Mapped[int] = mapped_column(name="puissance_de_charge")
    battery_capacity: Mapped[int] = mapped_column(name="capacite_de_batterie")
    electric_power_measure_id: Mapped[int] = mapped_column(
        name="mesures_puissance_elec_id"
    )
