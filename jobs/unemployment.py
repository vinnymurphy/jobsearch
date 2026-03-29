from jobs.models import Interview, Job

from datetime import timedelta
from typing import Any

from django.utils import timezone
from django.views import generic


class UnemploymentView(generic.ListView):
    model = Job
    template_name = "jobs/unemployment_report.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        days_back = self.request.GET.get("days", 7)
        try:
            days_back = int(days_back)
            if days_back < 1:
                raise ValueError
        except (ValueError, TypeError):
            days_back = 7  # Default to 7 days if invalid input
        today = timezone.now()
        seven_days_ago = today - timedelta(days=days_back)
        context["recent_jobs"] = (
            Job.objects.filter(created_at__gte=seven_days_ago)
            .select_related("company")
            .order_by("-created_at")
        )
        context["recent_interviews"] = (
            Interview.objects.filter(scheduled_time__gte=seven_days_ago)
            .select_related("job__company")
            .order_by("-scheduled_time")
        )
        context["report_start_date"] = seven_days_ago
        context["report_end_date"] = today
        return context
