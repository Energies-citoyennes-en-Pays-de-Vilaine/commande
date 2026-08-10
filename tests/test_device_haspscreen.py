from dataclasses import dataclass
import json
import logging
from typing import Any
import pytest

from config import config
from device_haspscreen import DeviceHaspScreen
from devicecallback import DeviceCallback
import ems_broker


class TestDeviceHaspScreen:
    @pytest.fixture
    def configuration(self):
        config.set_current_config({
            "mqtt": { "host": "127.0.0.1", "port": "", "user": "", "pass": "" },
            "pgsql": { "host": "127.0.0.1", "port": "5432", "user": "commande", "pass": "commande", "database": "commande" },
            "coordination": {
                "database": "commande",
                "equipement_domotique_table": "bdd_coordination_schema.equipement_domotique",
                "equipement_domotique_table_root": "bdd_coordination_schema.equipement_domotique_",
                "equipement_domotique_type_table": "bdd_coordination_schema.equipement_domotique_type",
                "equipement_pilote_ou_mesure_table": "bdd_coordination_schema.equipement_pilote_ou_mesure",
                "equipement_pilote_typologie_installation_domotique": "bdd_coordination_schema.equipement_pilote_typologie_installation_domotique",
                "equipement_pilote_vehicule_electrique_generique": "bdd_coordination_schema.equipement_pilote_vehicule_electrique_generique",
                "screen_usage_assoc": {
                    "6": [221],
                },
                "screen_indicator_topic": "INDICATEURS/refresh",
                "screen_connexion_page": 9,
                "screen_connexion_label_id": 8,
                "screen_connexion_label": "ecran connecté",
                "screen_connexion_label_color": "#208020",
                "screen_status_page": 8,
                "screen_led_id": 10,
                "screen_status_led":{
                    "6": 16,
                },
            },
        })
        return config.get_current_config()

    @pytest.fixture
    def screen(self, configuration) -> DeviceHaspScreen:
        return DeviceHaspScreen("test")

    @pytest.fixture
    def mqtt(self):
        mqtt = MqttSpy()
        ems_broker.handler = mqtt
        return mqtt

    @pytest.mark.skip
    def test_offline_then_online(self, caplog, mqtt: MqttSpy, screen: DeviceHaspScreen):
        screen.incomingMessage(mqtt=mqtt, devicetype=None, device=None, topic="hasp/g001/LWT", payload="offline")

        assert len(screen.offline_device) == 1
        screen.incomingMessage(mqtt=mqtt, devicetype=None, device=None, topic="hasp/g001/LWT", payload="online")

        assert mqtt.published_messages
        assert mqtt.published_messages[0].topic == "INDICATEURS/refresh"
        assert not screen.offline_device

    @pytest.mark.skip
    def test_charge_car(self, caplog, mqtt: MqttSpy, screen: DeviceHaspScreen):
        payload = json.dumps({
            "event": "up",
            "val": 1,
        })
        screen.incomingMessage(mqtt=mqtt, devicetype=None, device=None, topic="hasp/g001/state/p6b3", payload=payload)

        assert mqtt.published_messages
        assert mqtt.published_messages[0].topic == "cmnd/a001/POWER"
        assert mqtt.published_messages[0].payload == "OFF"

class MqttSpy:
    @dataclass
    class Message:
        topic: str
        payload: Any
        qos: int

    def __init__(self):
        self.published_messages: list[MqttSpy.Message] = []
        self.topic_callbacks: dict[str, DeviceCallback] = {}

    def publish(self, topic: str, payload: Any, qos: int = 0):
        self.published_messages.append(self.Message(topic, payload, qos))

    def SendMessage(self, topic: str, payload: Any):
        self.publish(topic, payload)

        if (callback := self.topic_callbacks.get("tele/a001")) is not None:
            callback.exec("tele/a001/STATE", json.dumps("success").encode("utf-8"))

    def RegisterCallback(self, topic: str, callback: DeviceCallback):
        self.topic_callbacks[topic] = callback

    def UnRegisterCallback(self, topic: str):
        del self.topic_callbacks[topic]
