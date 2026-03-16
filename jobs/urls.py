from django.urls import path

from .views import (
    InterviewDetailView,
    InterviewView,
    JobCreateView,
    JobDetailView,
    JobView,
    dashboard_view,
    UnemploymentView,
    export_calendar_pdf,
)

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path(
        "interview/<int:pk>/",
        InterviewDetailView.as_view(),
        name="interview_detail",
    ),
    path("interviews/", InterviewView.as_view(), name="interview_calendar"),
    path("jobs/", JobView.as_view(), name="job_calendar"),
    path("job/<int:pk>/", JobDetailView.as_view(), name="job_detail"),
    path("job/add/", JobCreateView.as_view(), name="job_create"),
    path(
        "job/add/<str:date>/",
        JobCreateView.as_view(),
        name="job_create_with_date",
    ),
    path(
        "export/pdf/<int:year>/<int:month>/",
        export_calendar_pdf,
        name="export_pdf",
    ),
    path(
        "unemployment-report/",
        UnemploymentView.as_view(),
        name="unemployment_report",
    ),
]
