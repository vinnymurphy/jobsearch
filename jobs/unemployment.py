from jobs.models import Interview, Job

from datetime import timedelta
from typing import Any

from django.utils import timezone
from django.views import generic


class JobSearchReportView(generic.TemplateView):
    """Generates a lookback activity log of job applications and
    interviews, typically used for compiling weekly unemployment
    work-search compliance logs.
    """

    template_name = "jobs/unemployment_report.html"
    DEFAULT_LOOKBACK_DAYS = 7

    def _get_lookback_days(self) -> int:
        """Parses, validates, and bounds the lookback window from the
        URL query strings.
        """
        raw_days = self.request.GET.get("days")
        try:
            days = int(raw_days)  # type: ignore
            return days if days >= 1 else self.DEFAULT_LOOKBACK_DAYS
        except (ValueError, TypeError):
            return self.DEFAULT_LOOKBACK_DAYS

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Establish window boundaries
        today = timezone.now().date()
        lookback_days = self._get_lookback_days()
        start_date = today - timedelta(days=lookback_days)

        # Gather compliance evidence querysets
        context["recent_jobs"] = (
            Job.objects.filter(applied_date__gte=start_date)
            .select_related("company")
            .order_by("-applied_date")
        )
        context["recent_interviews"] = (
            Interview.objects.filter(scheduled_time__date__gte=start_date)
            .select_related("job__company")
            .order_by("-scheduled_time")
        )

        # Meta parameters for report headers/labels
        context["report_start_date"] = start_date
        context["report_end_date"] = today
        context["lookback_days"] = lookback_days

        return context
