from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from maloen_commande.domain.base import Base


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


class Device(Base):
    __tablename__ = "equipement_pilote_ou_mesure"
    __mapper_args__ = {"polymorphic_on": "type"}

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
