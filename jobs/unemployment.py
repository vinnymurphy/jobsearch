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
        n_days = self.request.GET.get("days", 7)
        try:
            n_days = int(n_days)
            if n_days < 1:
                raise ValueError
        except (ValueError, TypeError):
            n_days = 7  # Default to 7 days if invalid input
        today = timezone.now().date()
        days_back = today - timedelta(days=n_days)
        context["recent_jobs"] = (
            Job.objects.filter(applied_date__gte=days_back)
            .select_related("company")
            .order_by("-applied_date")
        )
        context["recent_interviews"] = (
            Interview.objects.filter(scheduled_time__gte=days_back)
            .select_related("job__company")
            .order_by("-scheduled_time")
        )
        context["report_start_date"] = days_back
        context["report_end_date"] = today
        return context
