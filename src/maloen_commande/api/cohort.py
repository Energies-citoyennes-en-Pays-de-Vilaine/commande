import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from maloen_commande.domain import CohortRepository, cohort_repository

router = APIRouter(prefix="/cohorts")

logger = logging.getLogger(__name__)


class Cohort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    forecast_id: str


type CohortRepositoryDep = Annotated[CohortRepository, Depends(cohort_repository)]


@router.get("/{cohort_id}")
def get_cohort(cohort_id: str, cohort_repository: CohortRepositoryDep) -> Cohort:
    cohort = cohort_repository.find_by_id(cohort_id)
    if cohort is None:
        raise HTTPException(status_code=404)

    return Cohort.model_validate(cohort)
