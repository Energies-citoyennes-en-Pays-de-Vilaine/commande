import pytest
from sqlalchemy.orm import Session

from maloen_commande.domain import (
    Cofybox,
    Cohort,
    CommandState,
    DeviceMode,
    DeviceTypology,
    ElectricVehicle,
    HomeAutomationDeviceUse,
    MonitorState,
    User,
    UserRepository,
)
from maloen_commande.domain.base import engine


@pytest.mark.db
def test_find_by_cofybox():
    with Session(engine) as session:
        cohort = Cohort(id="Test", name="Test", description="Test", forecast_id="Test")
        user = User(id="Test", cohort_id=cohort.id)
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
        user.devices.append(ev)
        user.home_automation_devices.append(
            Cofybox(
                id="cb001",
                specific_id="cb001",
                managed_device=ev,
                use=HomeAutomationDeviceUse.MEASURE_COMMUTE.value,
                hardware_id="cb001",
                brand="",
                assigned_to_user=True,
                mqtt_bridge_topic="cofybox/cb001",
            )
        )

        session.add_all([cohort, user])

        user_repository = UserRepository(session)
        actual_user = user_repository.find_by_cofybox("cb001")

        assert actual_user is not None
        assert actual_user.id == "Test"
        session.rollback()
