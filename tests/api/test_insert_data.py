import json

import pytest

from maloen_commande.domain import (
    CommandState,
    DayOfWeek,
    DeviceMode,
    DeviceTypology,
    ElectricityRate,
    ElectricityRatePeriod,
    Heater,
    HeaterMode,
    HeaterModePeriod,
    MonitorState,
    UserRepository,
    transactional,
)


@pytest.mark.insert
def test_insert_data():
    with transactional() as session:
        user_repository = UserRepository(session)

        user = user_repository.find_by_id("Dummy")
        if user is None:
            raise Exception("Couldn't find user Dummy")

        with open("/home/wbartlett/Downloads/cohort_schedules.json") as f:
            data = json.load(f)

        user.electricity_tariff_schedule.clear()
        user.electricity_tariff_schedule.extend(
            [
                ElectricityRatePeriod(
                    day=DayOfWeek(day),
                    from_=period["from"],
                    to=period["to"],
                    rate=ElectricityRate(period["price"]),
                )
                for day, periods in data["users"][0][
                    "electricityPricingSchedule"
                ].items()
                for period in periods
            ]
        )

        for heater in data["users"][0]["heaters"]:
            heater_id = int(heater["id"])
            user.devices.append(
                Heater(
                    id=heater_id,
                    specific_id=heater_id,
                    device_id=heater_id,
                    name=f"Heater {heater_id}",
                    description="",
                    typology=DeviceTypology.PRISE_COMMANDE.value,
                    mode=DeviceMode.MANAGED.value,
                    monitor_state=MonitorState.OFF.value,
                    command_state=CommandState.INITIAL.value,
                    ems_recommends_activation=False,
                    last_activated_at=0,
                    last_programmed_at=0,
                    schedule=[
                        HeaterModePeriod(
                            day=DayOfWeek(day),
                            from_=period["from"],
                            to=period["to"],
                            mode=HeaterMode(period["mode"]),
                        )
                        for day, periods in heater["schedule"].items()
                        for period in periods
                    ],
                )
            )

        user_repository.insert(user)
