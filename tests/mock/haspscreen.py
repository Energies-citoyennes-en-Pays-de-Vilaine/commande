import json
import logging
from enum import Enum

from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from .domain import CohorteUtilisateurs, EquipementDomotique, EquipementDomotiqueOpenHasp, EquipementPilote, TypeEquipementDomotique, TypeEquipementPilote, Utilisateur

LOGGER = logging.getLogger(__name__)


class ScreenId(Enum):
    PAGE0 = 0
    STATS = 1
    PAGE2 = 2
    PAGE3 = 3
    PAGE4 = 4
    PAGE5 = 5
    CAR = 6
    PAGE7 = 7


class ButtonId(Enum):
    CAR_READY = 3
    CAR_END_HOUR = 5
    CAR_END_MINUTE = 6
    CAR_CHARGE_LEVEL = 8


class HaspScreenMock:
    def __init__(self, client: Client, engine: Engine, id: str, cofybox_id: str | None = None):
        self.client = client
        self.engine = engine
        self.id = id
        self.cofybox_id = cofybox_id

        self.messages: list[MQTTMessage] = []

        self.client.message_callback_add(f"{self.sujet_equipement}/command/jsonl", self.on_message)
        self.client.subscribe(f"{self.sujet_equipement}/#")

    @property
    def sujet_equipement(self):
        sujet = f"hasp/{self.id}"
        if self.cofybox_id:
            sujet = f"cofybox/{self.cofybox_id}/{sujet}"
        return sujet

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
                equipement_domotique_type_id=TypeEquipementDomotique.M5STACKCORE2_OPENHASP_V0.value,
                equipement_domotique_usage_id=71,
                id_materiel=self.id,
                marque="Dummy",
                utilisateur=utilisateur.id,
                utilisateur_affecte=True,
                equipement_domotique_specifique_id=self.id,
            )
            equipement_domotique_openhasp = EquipementDomotiqueOpenHasp(
                id=self.id,
                equipement_domotique_id=self.id,
                topic_mqtt_controle_json=f"hasp/{self.id.lower()}",
                topic_mqtt_commande_text=f"hasp/{self.id.lower()}/command/jsonl",
                topic_mqtt_lwt=f"hasp/{self.id.lower()}/LWT",
            )
            session.merge(cohorte)
            session.merge(utilisateur)
            session.merge(equipement_pilote)
            session.merge(equipement_domotique)
            session.merge(equipement_domotique_openhasp)
            session.commit()

    def demander_charge(self, heure_fin: int, minute_fin: int, charge_restante: int):
        self.publish_change(ScreenId.CAR, ButtonId.CAR_END_HOUR, heure_fin, f"{heure_fin}h")
        self.publish_change(ScreenId.CAR, ButtonId.CAR_END_MINUTE, minute_fin // 15, f"{minute_fin}")
        self.publish_change(ScreenId.CAR, ButtonId.CAR_CHARGE_LEVEL, charge_restante // 10, f"{charge_restante}%")
        self.publish_toggle(ScreenId.CAR, ButtonId.CAR_READY, True)

    def on_message(self, client: Client, data, message: MQTTMessage):
        self.messages.append(message)

    def publish_change(self, screen_id: ScreenId, button_id: ButtonId, value: int, text: str):
        topic = f"{self.sujet_equipement}/state/p{screen_id.value}b{button_id.value}"
        message = {
            "event": "changed",
            "val": 0,
            "text": text
        }

        self.client.publish(topic, json.dumps(message), qos=0).wait_for_publish()

    def publish_toggle(self, screen_id: ScreenId, button_id: ButtonId, value: bool):
        topic = f"{self.sujet_equipement}/state/p{screen_id.value}b{button_id.value}"
        message = {
            "event": "up",
            "val": int(value),
        }

        self.client.publish(topic, json.dumps(message), qos=0).wait_for_publish()
