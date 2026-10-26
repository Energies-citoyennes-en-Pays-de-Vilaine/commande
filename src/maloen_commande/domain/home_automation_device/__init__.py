from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maloen_commande.domain.base import Base
from maloen_commande.domain.device import Device


class HomeAutomationDeviceUse(Enum):
    MEASURE_COMMUTE = 11
    COMMUTE = 12
    MEASURE = 21
    PRESS_POWER = 31
    PRESS_START = 32
    MEASURE_AMBIENT = 61
    UI = 71


class HomeAutomationDevice(Base):
    __tablename__ = "equipement_domotique"
    __mapper_args__ = {"polymorphic_on": "type"}

    id: Mapped[str] = mapped_column(primary_key=True)
    specific_id: Mapped[str] = mapped_column(name="equipement_domotique_specifique_id")
    user_id: Mapped[str] = mapped_column(
        ForeignKey("utilisateur.id"), name="utilisateur"
    )
    managed_device_id: Mapped[int] = mapped_column(
        ForeignKey("equipement_pilote_ou_mesure.id"),
        name="equipement_pilote_ou_mesure_id",
    )
    managed_device: Mapped[Device] = relationship()
    type: Mapped[int] = mapped_column(name="equipement_domotique_type_id")
    use: Mapped[int] = mapped_column(name="equipement_domotique_usage_id")
    hardware_id: Mapped[str] = mapped_column(name="id_materiel")
    brand: Mapped[str] = mapped_column(name="marque")
    assigned_to_user: Mapped[bool] = mapped_column(name="utilisateur_affecte")


class Cofybox(HomeAutomationDevice):
    __tablename__ = "equipement_domotique_cofybox_hems_v2"
    __mapper_args__ = {"polymorphic_identity": 911}

    id: Mapped[str] = mapped_column(
        ForeignKey("equipement_domotique.id"), primary_key=True
    )
    mqtt_bridge_topic: Mapped[str] = mapped_column(name="topic_mqtt_bridge")
