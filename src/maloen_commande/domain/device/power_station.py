from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from maloen_commande.domain.device import Device


class GenericPowerStation(Device):
    __tablename__ = "equipement_mesure_centrale_elec_generique"
    __mapper_args__ = {
        "polymorphic_identity": 901,
    }
    id: Mapped[int] = mapped_column(
        ForeignKey("equipement_pilote_ou_mesure.id"), primary_key=True
    )
