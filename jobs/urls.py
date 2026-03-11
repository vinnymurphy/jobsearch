from django.urls import path

from .views import InterviewView, JobCreateView, JobDetailView, JobView

urlpatterns = [
    path("interviews/", InterviewView.as_view(), name="interview_calendar"),
    path("jobs/", JobView.as_view(), name="job_calendar"),
    path("job/<int:pk>/", JobDetailView.as_view(), name="job_detail"),
    path("job/add/", JobCreateView.as_view(), name="job_create"),
    path(
        "job/add/<str:date>/",
        JobCreateView.as_view(),
        name="job_create_with_date",
    ),
]
