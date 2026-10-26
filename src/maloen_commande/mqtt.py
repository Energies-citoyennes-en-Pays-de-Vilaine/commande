import logging
import re
from calendar import Day
from datetime import time

from fastapi_mqtt.config import MQTTConfig
from fastapi_mqtt.fastmqtt import FastMQTT
from pydantic import TypeAdapter, ValidationError

from maloen_commande.api.cohort_schedules import SchedulePeriod
from maloen_commande.domain import (
    DayOfWeek,
    ElectricityRate,
    ElectricityRatePeriod,
    HeaterMode,
    User,
    UserRepository,
    transactional,
)
from maloen_commande.domain.device.heater import HeaterModePeriod
from maloen_commande.hasp import HaspEvent, HaspPageId

fast_mqtt = FastMQTT(config=MQTTConfig())


logger = logging.getLogger(__name__)


@fast_mqtt.subscribe("cofybox/+/schedules/electricity-tariff")
def electricity_tariff(
    _client,
    topic: str,
    payload: bytes,
    _qos,
    _properties,
):
    logger.debug("%s: %s", topic, payload)
    cofybox_id = topic.split("/")[1]

    with transactional() as session:
        user_repository = UserRepository(session)

        user = user_repository.find_by_cofybox(cofybox_id)

        if not user:
            logger.warning("Unknown Cofybox %s", cofybox_id)
            return

        try:
            periods_by_day = TypeAdapter(
                dict[DayOfWeek, list[SchedulePeriod]]
            ).validate_json(payload)
        except ValidationError:
            logger.exception("Couldn't parse payload as a schedule.")
            return

        user.update_electricity_tariff_schedule(
            [
                period
                for day, periods in periods_by_day.items()
                for period in fill_electricity_day_schedule(day, periods)
            ]
        )


@fast_mqtt.subscribe("cofybox/+/hasp/+/state/+")
def cofybox_hasp_state(
    _client,
    topic: str,
    payload: bytes,
    _qos,
    _properties,
):
    (_, _cofybox_id, _, device_id, _, state_topic) = topic.split("/")

    m = re.fullmatch(state_topic, r"p(?P<page>\d)b(?P<control>\d)")
    if not m:
        return

    handle_hasp_page_button(
        device_id,
        HaspPageId(int(m.group("page"))),
        int(m.group("control")),
        HaspEvent.model_validate_json(payload),
    )


def handle_hasp_page_button(
    device_id: str, page_id: HaspPageId, control_id: int, event: HaspEvent
):
    with transactional() as session:
        user_repository = UserRepository(session)

        user = user_repository.find_by_home_automation_device(device_id)
        if user is None:
            logger.warning("Unknown home automation device: %s", device_id)

        match (page_id, control_id):
            case (HaspPageId.WEEKDAY_OFF_PEAK_ELEC, 5):
                pass
                # update_electricity_off_peak_from_hour(user, event.val)


def update_electricity_off_peak(
    periods: list[ElectricityRatePeriod],
    days: list[DayOfWeek],
    index: int,
    side: str,
    hour: int | None,
    minute: int | None,
):
    weekday_off_peak_periods = sorted(
        (
            period
            for period in periods
            if period.day == days[0] and period.rate == ElectricityRate.OFF_PEAK
        ),
        key=lambda period: period.from_,
    )

    return periods


def fill_electricity_day_schedule(
    day: DayOfWeek,
    off_peak_periods: list[SchedulePeriod],
) -> list[ElectricityRatePeriod]:
    off_peak_periods.sort()

    result = []
    current_time = time(0, 0)
    for off_peak_period in off_peak_periods:
        if off_peak_period.from_ > current_time:
            result.append(
                ElectricityRatePeriod(
                    from_=current_time,
                    to=off_peak_period.from_,
                    day=day,
                    rate=ElectricityRate.PEAK,
                )
            )

        result.append(
            ElectricityRatePeriod(
                from_=off_peak_period.from_,
                to=off_peak_period.to,
                day=day,
                rate=ElectricityRate.OFF_PEAK,
            )
        )
        current_time = off_peak_period.to

    if current_time < time(23, 59, 59):
        result.append(
            ElectricityRatePeriod(
                from_=current_time,
                to=time(23, 59, 59),
                day=day,
                rate=ElectricityRate.PEAK,
            )
        )

    return result


def fill_heater_day_schedule(
    day: DayOfWeek,
    comfort_periods: list[SchedulePeriod],
) -> list[HeaterModePeriod]:
    comfort_periods.sort()

    result = []
    current_time = time(0, 0)
    for period in comfort_periods:
        if period.from_ > current_time:
            result.append(
                HeaterModePeriod(
                    from_=current_time,
                    to=period.from_,
                    day=day,
                    rate=HeaterMode.ECO,
                )
            )

        result.append(
            HeaterModePeriod(
                from_=period.from_,
                to=period.to,
                day=day,
                rate=HeaterMode.COMFORT,
            )
        )
        current_time = period.to

    if current_time < time(23, 59, 59):
        result.append(
            HeaterModePeriod(
                from_=current_time,
                to=time(23, 59, 59),
                day=day,
                rate=HeaterMode.ECO,
            )
        )

    return result
