import logging
from threading import Event

from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from .domain import CohorteUtilisateurs, EquipementDomotique, EquipementDomotiqueTasmota, EquipementPilote, TypeEquipementDomotique, TypeEquipementPilote, Utilisateur

LOGGER = logging.getLogger(__name__)


class PriseTasmotaMock:
    def __init__(self, client: Client, engine: Engine, id: str, cofybox_id: str | None = None):
        self.client = client
        self.engine = engine
        self.id = id
        self.cofybox_id = cofybox_id

        self.messages: list[MQTTMessage] = []
        self.message_received = Event()

        self.client.message_callback_add(f"{self.sujet_commande}", self.on_message)
        self.client.subscribe(f"{self.sujet_commande}")

    @property
    def prefixe_cofybox(self):
        if self.cofybox_id:
            return f"cofybox/{self.cofybox_id}/"
        else:
            return ""

    @property
    def sujet_commande(self) -> str:
        return f"{self.prefixe_cofybox}cmnd/{self.id}/POWER"

    @property
    def sujet_controle(self) -> str:
        return f"{self.prefixe_cofybox}stat/{self.id}/RESULT"

    @property
    def sujet_lwt(self) -> str:
        return f"{self.prefixe_cofybox}tele/{self.id}/LWT"

    def ajouter_equipement(self):
        with Session(self.engine) as session:
            cohorte = CohorteUtilisateurs(
                id="Dummy",
                nom="Dummy",
                description="Dummy",
                prevision_id="Dummy",
            )
            utilisateur = Utilisateur(
                id="Dummy",
                cohorte="Dummy",
            )
            equipement_pilote = EquipementPilote(
                id=1,
                equipement_pilote_specifique_id=1,
                typologie_installation_domotique_id=120,
                nom_humain="Dummy",
                description="Dummy",
                equipement_pilote_ou_mesure_type_id=TypeEquipementPilote.VOITURE_ELECTRIQUE.value,
                equipement_pilote_ou_mesure_mode_id=1,
                etat_controle_id=70,
                etat_commande_id=1,
                ems_consigne_marche=False,
                timestamp_derniere_mise_en_marche=0,
                timestamp_derniere_programmation=0,
                utilisateur=utilisateur.id,
            )
            equipement_domotique = EquipementDomotique(
                id=self.id,
                equipement_pilote_ou_mesure_id=1,
                equipement_domotique_type_id=TypeEquipementDomotique.NOUS_A1T_TASMOTA_V12.value,
                equipement_domotique_usage_id=11,
                id_materiel=self.id,
                marque="Dummy",
                utilisateur=utilisateur.id,
                utilisateur_affecte=True,
                equipement_domotique_specifique_id=self.id,
            )
            equipement_domotique_tasmota = EquipementDomotiqueTasmota(
                id=self.id,
                equipement_domotique_id=self.id,
                topic_mqtt_controle_json=self.sujet_controle,
                topic_mqtt_commande_text=self.sujet_commande,
                topic_mqtt_lwt=self.sujet_lwt,
            )
            session.merge(cohorte)
            session.merge(utilisateur)
            session.merge(equipement_pilote)
            session.merge(equipement_domotique)
            session.merge(equipement_domotique_tasmota)
            session.commit()

    def on_message(self, client: Client, data, message: MQTTMessage):
        self.messages.append(message)
        self.message_received.set()

    def wait_for_message(self, timeout=None):
        self.message_received.wait(timeout)
