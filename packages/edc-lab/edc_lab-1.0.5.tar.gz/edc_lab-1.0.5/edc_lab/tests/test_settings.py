#!/usr/bin/env python
import sys
from pathlib import Path

from edc_test_settings.default_test_settings import DefaultTestSettings

app_name = "edc_lab"
base_dir = Path(__file__).absolute().parent.parent.parent

project_settings = DefaultTestSettings(
    calling_file=__file__,
    BASE_DIR=base_dir,
    APP_NAME=app_name,
    ETC_DIR=str(base_dir / app_name / "tests" / "etc"),
    SILENCED_SYSTEM_CHECKS=[
        "sites.E101",
        "edc_navbar.E002",
        "edc_navbar.E003",
        "edc_consent.E001",
    ],
    SUBJECT_SCREENING_MODEL="lab_app.subjectscreening",
    SUBJECT_CONSENT_MODEL="lab_app.subjectconsent",
    SUBJECT_VISIT_MODEL="edc_visit_tracking.subjectvisit",
    SUBJECT_VISIT_MISSED_MODEL="edc_visit_tracking.subjectvisitmissed",
    SUBJECT_REQUISITION_MODEL="lab_app.subjectrequisition",
    SUBJECT_APP_LABEL="lab_app",
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sites",
        "django_crypto_fields.apps.AppConfig",
        "django_revision.apps.AppConfig",
        "multisite",
        "edc_auth.apps.AppConfig",
        "edc_action_item.apps.AppConfig",
        "edc_appointment.apps.AppConfig",
        "edc_adverse_event.apps.AppConfig",
        "adverse_event_app.apps.AppConfig",
        "edc_consent.apps.AppConfig",
        "edc_crf.apps.AppConfig",
        "edc_list_data.apps.AppConfig",
        "edc_protocol.apps.AppConfig",
        "edc_metadata.apps.AppConfig",
        "edc_dashboard.apps.AppConfig",
        "edc_subject_dashboard.apps.AppConfig",
        "edc_review_dashboard.apps.AppConfig",
        "edc_device.apps.AppConfig",
        "edc_identifier.apps.AppConfig",
        "edc_facility.apps.AppConfig",
        "edc_label.apps.AppConfig",
        "edc_model.apps.AppConfig",
        "edc_notification.apps.AppConfig",
        "edc_data_manager.apps.AppConfig",
        "edc_form_runners.apps.AppConfig",
        "edc_registration.apps.AppConfig",
        "edc_search.apps.AppConfig",
        "edc_sites.apps.AppConfig",
        "edc_timepoint.apps.AppConfig",
        "edc_visit_schedule.apps.AppConfig",
        "edc_visit_tracking.apps.AppConfig",
        "edc_offstudy.apps.AppConfig",
        "edc_lab.apps.AppConfig",
        "lab_app.apps.AppConfig",
        "edc_appconfig.apps.AppConfig",
    ],
    add_dashboard_middleware=True,
    use_test_urls=True,
).settings


for k, v in project_settings.items():
    setattr(sys.modules[__name__], k, v)
