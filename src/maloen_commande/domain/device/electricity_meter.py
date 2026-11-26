from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from maloen_commande.domain.device import Device


class ElectricityMeter(Device):
    __tablename__ = "equipement_mesure_compteur_electrique"
    __mapper_args__ = {
        "polymorphic_identity": 410,
    }
    id: Mapped[int] = mapped_column(
        ForeignKey("equipement_pilote_ou_mesure.id"), primary_key=True
    )
