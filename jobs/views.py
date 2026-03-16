from datetime import date, timedelta
from typing import Any
from django.utils import timezone

from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views import generic
from weasyprint import HTML

from .forms import IndustryForm, InterviewerForm, InterviewForm, JobForm
from .models import Interview, Job
from .utils import (
    InterviewCalendar,
    JobCalendar,
    get_date,
    next_month,
    prev_month,
)


def dashboard_view(request):
    # Aggregate job counts by company
    performance_data = (
        Job.objects.values("company__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_velocity = Job.objects.filter(
        created_at__gte=seven_days_ago
    ).count()

    context = {
        "labels": [item["company__name"] for item in performance_data],
        "counts": [item["total"] for item in performance_data],
        "recent_velocity": recent_velocity,
    }
    return render(request, "jobs/dashboard.html", context)


def export_calendar_pdf(request, year, month):
    cal = JobCalendar(year, month)
    html_string = render_to_string(
        "jobs/calendar_pdf.html",
        {"calendar": cal, "year": year, "month": month},
    )
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    result = html.write_pdf()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f"attachment; filename=calendar_{year}_{month}.pdf"
    )
    response.write(result)
    return response


def create_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("job_list")
    else:
        form = JobForm()
    return render(request, "jobs/create_job.html", {"form": form})


class JobCreateView(SuccessMessageMixin, generic.CreateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"
    success_url = reverse_lazy("job_calendar")

    success_message = "Job for %(title)s at %(company)s created successfully!"

    def get_success_message(self, cleaned_data):
        # This allows you to use dynamic data in the message
        return self.success_message % dict(
            cleaned_data,
            company=self.object.company.name,
        )

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        date_str = self.kwargs.get("date")
        if date_str:
            initial["applied_date"] = get_date(date_str)
        return initial


def create_industry(request):
    if request.method == "POST":
        form = IndustryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("industry_list")
    else:
        form = IndustryForm()
    return render(request, "jobs/create_industry.html", {"form": form})


class InterviewView(generic.ListView):
    model = Interview
    template_name = "jobs/interview_calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        d = get_date(self.request.GET.get("month", None))
        cal = InterviewCalendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
        return context


class JobView(generic.ListView):
    model = Job
    template_name = "jobs/job_calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        try:
            year = int(self.request.GET.get("year", today.year))
            month = int(self.request.GET.get("month", today.month))
            if month < 1 or month > 12:
                raise ValueError
        except (ValueError, TypeError):
            year = today.year
            month = today.month
        first_day_of_month = date(year, month, 1)
        prev_month_date = first_day_of_month - timedelta(days=1)
        next_month_date = first_day_of_month + timedelta(days=32)
        jobs = Job.objects.filter(
            created_at__year=year, created_at__month=month
        )
        interviews = Interview.objects.filter(
            scheduled_time__year=year, scheduled_time__month=month
        )
        jobs_by_day = {}
        for job in jobs:
            d = job.created_at.day
            jobs_by_day.setdefault(d, []).append(job)

        interviews_by_day = {}
        for interview in interviews:
            d = interview.scheduled_time.day
            interviews_by_day.setdefault(d, []).append(interview)

        cal = JobCalendar(year, month)
        html_cal = cal.formatmonth(
            year,
            month,
            withyear=True,
            jobs=jobs_by_day,
            interviews=interviews_by_day,
        )
        context["calendar"] = mark_safe(html_cal)
        context["prev_year"] = prev_month_date.year
        context["prev_month"] = prev_month_date.month
        context["next_year"] = next_month_date.year
        context["next_month"] = next_month_date.month
        context["year"] = year
        context["month"] = month
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.job = self.object  # Automatically link to this job
            interview.save()
            return redirect("job_detail", pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form=form))


class InterviewDetailView(generic.DetailView):
    model = Interview
    template_name = "jobs/interview_detail.html"
    context_object_name = "interview"


class JobDetailView(generic.DetailView):
    model = Job
    template_name = "jobs/job_detail.html"
    context_object_name = "job"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["interviews"] = self.object.interviews.order_by(
            "-scheduled_time"
        )
        context["form"] = InterviewForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if "submit_interview" in request.POST:
            form = InterviewForm(request.POST)
            if form.is_valid():
                interview = form.save(commit=False)
                interview.job = self.object
                interview.save()
                return redirect("job_detail", pk=self.object.pk)
            # If invalid, return with the specific form errors
            return self.render_to_response(
                self.get_context_data(interview_form=form)
            )

        elif "submit_interviewer" in request.POST:
            form = InterviewerForm(request.POST)
            if form.is_valid():
                interviewer = form.save(commit=False)
                interviewer.company = self.object.company
                interviewer.save()
                return redirect("job_detail", pk=self.object.pk)
            # If invalid, return with the specific form errors
            return self.render_to_response(
                self.get_context_data(interviewer_form=form)
            )

        # Fallback: If somehow the POST reached here without a valid button name
        return self.render_to_response(self.get_context_data())


class UnemploymentView(generic.ListView):
    model = Job
    template_name = "jobs/unemployment_report.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        days_back = self.request.GET.get('days', 7)
        try:
            days_back = int(days_back)
            if days_back < 1:
                raise ValueError
        except (ValueError, TypeError):
            days_back = 7  # Default to 7 days if invalid input
        today = timezone.now()
        seven_days_ago = today - timedelta(days=days_back)
        context["recent_jobs"] = Job.objects.filter(
            created_at__gte=seven_days_ago
        ).order_by("-created_at")
        context["recent_interviews"] = Interview.objects.filter(
            scheduled_time__gte=seven_days_ago
        ).order_by("-scheduled_time")
        context["report_start_date"] = seven_days_ago
        context["report_end_date"] = today
        return context
