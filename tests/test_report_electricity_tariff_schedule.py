from datetime import time
from typing import Generator

import pytest
from pydantic import TypeAdapter

from maloen_commande.api.cohort_schedules import SchedulePeriod
from maloen_commande.domain import (
    Cofybox,
    Cohort,
    CommandState,
    DayOfWeek,
    DeviceMode,
    DeviceTypology,
    ElectricityRate,
    ElectricityRatePeriod,
    ElectricVehicle,
    HomeAutomationDeviceUse,
    MonitorState,
    User,
    transactional,
)
from maloen_commande.mqtt import (
    electricity_tariff,
    fill_electricity_day_schedule,
    update_electricity_off_peak,
)


@pytest.fixture
def schedule_payload() -> bytes:
    return b"""{"monday": [{"from":"01:00:00","to":"05:00:00"}],"tuesday": [{"from":"01:00:00","to":"05:00:00"}],"wednesday": [{"from":"01:00:00","to":"05:00:00"}],"thursday": [{"from":"01:00:00","to":"05:00:00"}],"friday": [{"from":"01:00:00","to":"05:00:00"}],"saturday": [{"from":"00:00:00","to":"23:59:59.999999"}],"sunday": [{"from":"00:00:00","to":"23:59:59.999999"}]}"""


@pytest.mark.int
class TestGivenUser:
    @pytest.fixture
    def user(self) -> Generator[User]:
        with transactional() as session:
            user = session.query(User).where(User.id == "Test").one_or_none()
            if user is not None:
                session.delete(user)

            cohort = session.query(Cohort).where(Cohort.id == "Test").one_or_none()
            if cohort is not None:
                session.delete(cohort)

        cohort = Cohort(id="Test", name="Test", description="Test", forecast_id="Test")

        ev = ElectricVehicle(
            id=999,
            specific_id=999,
            device_id=999,
            name="EV",
            description="",
            typology=DeviceTypology.PRISE_COMMANDE.value,
            mode=DeviceMode.MANUAL.value,
            monitor_state=MonitorState.OFF.value,
            command_state=CommandState.MANAGED_STAND_BY.value,
            ems_recommends_activation=False,
            last_activated_at=1,
            last_programmed_at=1,
            remaining_charge_percentage=0,
            minimum_desired_charge_percentage=100,
            estimated_charging_time=21600,
            deadline_timestamp=1,
            charging_power=3680,
            battery_capacity=25000,
            electric_power_measure_id=1,
        )

        user = User(id="Test", cohort_id=cohort.id)
        user.devices.append(ev)
        user.home_automation_devices.append(
            Cofybox(
                id="cb",
                specific_id="cb999",
                managed_device=ev,
                use=HomeAutomationDeviceUse.MEASURE_COMMUTE.value,
                hardware_id="cb999",
                brand="",
                assigned_to_user=True,
                mqtt_bridge_topic="cofybox/cb999",
            )
        )
        with transactional() as session:
            session.add_all([cohort, user])

        yield user

    @pytest.mark.db
    def test_update_schedule(self, user: User, schedule_payload: bytes):
        topic = "cofybox/cb001/schedules/electricity-tariff"

        electricity_tariff(None, topic, schedule_payload, 0, {})

        with transactional() as session:
            user = session.query(User).where(User.id == "Test").one()
            assert user.electricity_tariff_schedule[0].day == DayOfWeek.MONDAY


@pytest.mark.unit
def test_parse_schedule(schedule_payload: bytes):
    view = TypeAdapter(dict[DayOfWeek, list[SchedulePeriod]]).validate_json(
        schedule_payload
    )

    assert view[DayOfWeek.SUNDAY][0].from_ == time(0, 0)
    assert view[DayOfWeek.SUNDAY][0].to == time(23, 59, 59, 999999)


@pytest.mark.unit
def test_fill_electricity_schedule_day():
    off_peak_hours = [SchedulePeriod(from_=time(1, 0), to=time(5, 0))]

    day_schedule = fill_electricity_day_schedule(DayOfWeek.MONDAY, off_peak_hours)
    assert day_schedule == [
        ElectricityRatePeriod(
            from_=time(0, 0),
            to=time(1, 0),
            rate=ElectricityRate.PEAK,
            day=DayOfWeek.MONDAY,
        ),
        ElectricityRatePeriod(
            from_=time(1, 0),
            to=time(5, 0),
            rate=ElectricityRate.OFF_PEAK,
            day=DayOfWeek.MONDAY,
        ),
        ElectricityRatePeriod(
            from_=time(5, 0),
            to=time(23, 59, 59),
            rate=ElectricityRate.PEAK,
            day=DayOfWeek.MONDAY,
        ),
    ]


def case(
    weekday: list[tuple[time, time]], weekend: list[tuple[time, time]]
) -> list[ElectricityRatePeriod]:
    return [
        period
        for day in DayOfWeek.weekdays()
        for period in fill_electricity_day_schedule(
            day, [SchedulePeriod(from_=from_, to=to) for from_, to in weekday]
        )
    ] + [
        period
        for day in DayOfWeek.weekend()
        for period in fill_electricity_day_schedule(
            day, [SchedulePeriod(from_=from_, to=to) for from_, to in weekend]
        )
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    "periods, days, index, side, hour, expected",
    [
        (
            case(
                weekday=[(time(1, 0), time(5, 0))],
                weekend=[(time(0, 0), time(23, 59))],
            ),
            DayOfWeek.weekdays(),
            1,
            "from_",
            2,
            case(
                weekday=[(time(1, 0), time(5, 0))],
                weekend=[(time(0, 0), time(23, 59))],
            ),
        ),
    ],
)
def test_update_electricity_off_peak_hour(
    periods: list[ElectricityRatePeriod],
    days: list[DayOfWeek],
    index: int,
    side: str,
    hour: int,
    expected: list[ElectricityRatePeriod],
):
    actual = update_electricity_off_peak(periods, days, index, side, hour, None)

    assert actual == expected
