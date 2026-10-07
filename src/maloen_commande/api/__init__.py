import logging

from fastapi import FastAPI

from maloen_commande.api import cohort, cohort_schedules

logging.basicConfig(level=logging.INFO)

api = FastAPI()

api.include_router(cohort.router)
api.include_router(cohort_schedules.router)
