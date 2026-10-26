from datetime import time

import pytest
from pydantic import BaseModel

from maloen_commande import domain
from maloen_commande.api import cohort_schedules


@pytest.mark.unit
def test_electricity():
    cohort_schedules.ElectricityRatePeriod.model_validate(
        {
            "from": time(0, 0, 0),
            "to": time(11, 59, 59),
            "rate": domain.ElectricityRate.OFF_PEAK,
        }
    )
