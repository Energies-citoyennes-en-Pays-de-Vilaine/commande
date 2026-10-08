import logging
import click
from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy import URL, create_engine

from .haspscreen import HaspScreenMock

LOGGER = logging.getLogger(__name__)


@click.group
def main():
    logging.basicConfig(level=logging.INFO)


@main.group("screen")
def screen():
    pass


@screen.command("add")
@click.argument("id_equipement")
def ajouter_equipement(id_equipement: str):
    client = Client()
    client.connect("localhost")
    client.loop_start()

    engine = create_engine(URL.create(
        drivername="postgresql+psycopg2",
        host="localhost",
        username="commande",
        password="commande",
    ), connect_args={"options": "-csearch_path=bdd_coordination_schema"})

    ecran = HaspScreenMock(client, engine, id_equipement)
    ecran.ajouter_equipement()
    LOGGER.info("Écran %s ajouté", ecran.id)

    client.loop_stop()


@screen.command("charge")
@click.argument("id_equipement")
@click.argument("heure_fin", type=click.INT)
@click.argument("minute_fin", type=click.INT)
@click.argument("charge_restante", type=click.INT)
def demander_charge(id_equipement: str, heure_fin: int, minute_fin: int, charge_restante: int):
    client = Client()
    client.connect("localhost")
    client.loop_start()

    engine = create_engine(URL.create(
        drivername="postgresql+psycopg2",
        host="localhost",
        username="commande",
        password="commande",
    ), connect_args={"options": "-csearch_path=bdd_coordination_schema"})

    ecran = HaspScreenMock(client, engine, id_equipement)
    ecran.demander_charge(heure_fin, minute_fin, charge_restante)
    LOGGER.info("Charge voiture pour %02dh%02d demandée", heure_fin, minute_fin)

    client.loop_stop()


@main.command("listen")
def listen():
    client = Client()
    def on_message(client, data, message: MQTTMessage):
        LOGGER.info("[%s] %s", message.topic, message.payload)

    # client.on_message = on_message
    client.connect("localhost")
    client.message_callback_add("hasp/g001/command/jsonl", on_message)
    client.subscribe("hasp/#")
    client.loop_forever()


if __name__ == "__main__":
    main()
