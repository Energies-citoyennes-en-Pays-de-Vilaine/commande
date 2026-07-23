from paho.mqtt.client import Client
import pytest
from sqlalchemy import URL, Engine, create_engine

from tests.mock.haspscreen import HaspScreenMock


class TestChargeCar:
    @pytest.fixture
    def broker(self):
        broker = Client()
        broker.connect("localhost")
        broker.loop_start()
        yield broker
        broker.loop_stop()

    @pytest.fixture
    def engine(self) -> Engine:
        engine = create_engine(URL.create(
            drivername="postgresql+psycopg2",
            host="localhost",
            username="commande",
            password="commande",
        ), connect_args={"options": "-csearch_path=bdd_coordination_schema"})
        return engine

    @pytest.fixture
    def screen(self, broker: Client, engine: Engine) -> HaspScreenMock:
        screen = HaspScreenMock(broker, engine, "g001")
        screen.ajouter_equipement()
        return screen

    def test_charge_car(self, screen: HaspScreenMock):
        screen.demander_charge(heure_fin=22, minute_fin=0, charge_restante=0)
