import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from maloen_commande.api import cohort, cohort_schedules
from maloen_commande.mqtt import fast_mqtt

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await fast_mqtt.mqtt_startup()
    yield
    await fast_mqtt.mqtt_shutdown()


api = FastAPI(lifespan=lifespan)

api.include_router(cohort.router)
api.include_router(cohort_schedules.router)
