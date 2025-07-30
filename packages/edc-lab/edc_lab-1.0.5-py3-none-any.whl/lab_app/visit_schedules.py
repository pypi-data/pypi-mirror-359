from dateutil.relativedelta import relativedelta
from edc_visit_schedule.schedule import Schedule
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.tests.dummy_panel import DummyPanel
from edc_visit_schedule.visit import Crf, CrfCollection, RequisitionCollection, Visit
from edc_visit_schedule.visit.requisition import Requisition
from edc_visit_schedule.visit_schedule import VisitSchedule

from .consents import consent_v1


class MockPanel(DummyPanel):
    """`requisition_model` is normally set when the lab profile
    is set up.
    """

    def __init__(self, name):
        super().__init__(requisition_model="lab_app.subjectrequisition", name=name)


crfs = CrfCollection(Crf(show_order=1, model="lab_app.crfone", required=True))

requisitions = RequisitionCollection(
    Requisition(show_order=10, panel=MockPanel("panel"), required=True, additional=False)
)


visit = Visit(
    code="1000",
    timepoint=0,
    rbase=relativedelta(days=0),
    rlower=relativedelta(days=0),
    rupper=relativedelta(days=6),
    requisitions=requisitions,
    crfs=crfs,
    requisitions_unscheduled=None,
    crfs_unscheduled=None,
    allow_unscheduled=False,
    facility_name="5-day-clinic",
)


schedule = Schedule(
    name="schedule",
    onschedule_model="lab_app.onschedule",
    offschedule_model="lab_app.offschedule",
    appointment_model="edc_appointment.appointment",
    consent_definitions=[consent_v1],
)

visit_schedule = VisitSchedule(
    name="visit_schedule",
    offstudy_model="edc_offstudy.subjectoffstudy",
    death_report_model="edc_appointment.deathreport",
    locator_model="edc_locator.subjectlocator",
)

schedule.add_visit(visit)

visit_schedule.add_schedule(schedule)
site_visit_schedules.register(visit_schedule)
