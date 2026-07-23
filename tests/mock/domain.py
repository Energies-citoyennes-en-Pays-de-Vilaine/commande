from sqlalchemy.orm import mapped_as_dataclass, Mapped, registry, mapped_column

REGISTRY = registry()

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


@mapped_as_dataclass(REGISTRY)
class EquipementDomotiqueOpenHasp:
    __tablename__ = "equipement_domotique_m5stackcore2_openhasp_v0"

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
