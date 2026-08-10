from enum import Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_as_dataclass, Mapped, registry, mapped_column, relationship

REGISTRY = registry()

class TypeEquipementDomotique(Enum):
    NOUS_A1T_TASMOTA_V12 = 112
    M5STACKCORE2_OPENHASP_V0 = 711


class TypeEquipementPilote(Enum):
    MACHINE_GENERIQUE = 1
    LAVE_VAISSELLE = 111
    LAVE_LINGE = 112
    SECHE_LINGE = 113
    BALLON_ECS = 131
    CHAUFFAGE_NON_ASSERVI = 151
    CHAUFFAGE_ASSERVI = 155
    VOITURE_ELECTRIQUE = 221
    VELO_ASSISTANCE_ELECTRIQUE = 225
    COMPTEUR_ELECTRIQUE = 410
    CHARIOT_ELEVATEUR_ELECTRIQUE = 515
    CENTRALE_ELEC_GENERIQUE = 901
    CENTRALE_SOLAIRE_ELEC = 910
    CENTRALE_EOLIENNE_ELEC = 920


@mapped_as_dataclass(REGISTRY)
class EquipementDomotique:
    __tablename__ = "equipement_domotique"

    id: Mapped[str] = mapped_column(primary_key=True)
    equipement_pilote_ou_mesure_id: Mapped[int]
    equipement_domotique_type_id: Mapped[int]
    equipement_domotique_usage_id: Mapped[int]
    id_materiel: Mapped[str]
    marque: Mapped[str]
    utilisateur: Mapped[str]
    utilisateur_affecte: Mapped[bool]
    equipement_domotique_specifique_id: Mapped[str]
    cofybox_id: Mapped[str] = mapped_column(ForeignKey("cofybox.id"), init=False, default=None)


@mapped_as_dataclass(REGISTRY)
class EquipementDomotiqueOpenHasp:
    __tablename__ = "equipement_domotique_m5stackcore2_openhasp_v0"

    id: Mapped[str] = mapped_column(primary_key=True)
    equipement_domotique_id: Mapped[str]
    topic_mqtt_controle_json: Mapped[str]
    topic_mqtt_commande_text: Mapped[str]
    topic_mqtt_lwt: Mapped[str]


@mapped_as_dataclass(REGISTRY)
class EquipementDomotiqueTasmota:
    __tablename__ = "equipement_domotique_nous_a1t_tasmota_v12"

    id: Mapped[str] = mapped_column(primary_key=True)
    equipement_domotique_id: Mapped[str]
    topic_mqtt_controle_json: Mapped[str]
    topic_mqtt_commande_text: Mapped[str]
    topic_mqtt_lwt: Mapped[str]


@mapped_as_dataclass(REGISTRY)
class EquipementPilote:
    __tablename__ = "equipement_pilote_ou_mesure"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipement_pilote_specifique_id: Mapped[int]
    typologie_installation_domotique_id: Mapped[int]
    nom_humain: Mapped[str]
    description: Mapped[str]
    equipement_pilote_ou_mesure_type_id: Mapped[int]
    equipement_pilote_ou_mesure_mode_id: Mapped[int]
    etat_controle_id: Mapped[int]
    etat_commande_id: Mapped[int]
    ems_consigne_marche: Mapped[bool]
    timestamp_derniere_mise_en_marche: Mapped[int]
    timestamp_derniere_programmation: Mapped[int]
    utilisateur: Mapped[str]


@mapped_as_dataclass(REGISTRY)
class Utilisateur:
    __tablename__ = "utilisateur"

    id: Mapped[str] = mapped_column(primary_key=True)
    cohorte: Mapped[str]


@mapped_as_dataclass(REGISTRY)
class CohorteUtilisateurs:
    __tablename__ = "cohorte_utilisateurs"

    id: Mapped[str] = mapped_column(primary_key=True)
    nom: Mapped[str]
    description: Mapped[str]
    prevision_id: Mapped[str]


@mapped_as_dataclass(REGISTRY)
class Cofybox:
    __tablename__ = "cofybox"

    id: Mapped[str] = mapped_column(primary_key=True)
    equipements: Mapped[list[EquipementDomotique]] = relationship(init=False, default_factory=list)
