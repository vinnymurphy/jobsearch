from .unemployment import JobSearchReportView
from .views import (
    InterviewDetailView,
    JobCreateView,
    JobDetailView,
    JobView,
    chat_view,
    dashboard_view,
    export_calendar_pdf,
)

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path(
        "interview/<int:pk>/",
        InterviewDetailView.as_view(),
        name="interview_detail",
    ),
    path("jobs/", JobView.as_view(), name="calendar"),
    path("job/add/", JobCreateView.as_view(), name="job_create"),
    path(
        "job/add/<str:date>/",
        JobCreateView.as_view(),
        name="job_create_with_date",
    ),
    path("job/<slug:slug>/", JobDetailView.as_view(), name="job_detail"),
    path(
        "export/pdf/<int:year>/<int:month>/",
        export_calendar_pdf,
        name="export_pdf",
    ),
    path(
        "unemployment-report/",
        JobSearchReportView.as_view(),
        name="unemployment_report",
    ),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.svg")),
        name="favicon",
    ),
    path("api/chat/", chat_view, name="chat"),
]
