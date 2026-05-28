from .forms import IndustryForm, InterviewerForm, InterviewForm, JobForm
from .models import Interview, Job
from .utils import MasterCalendar, get_date, get_unemployment_week

from collections import OrderedDict
from datetime import date, timedelta
from typing import Any

from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views import generic
from openai import OpenAI
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from weasyprint import HTML

client = OpenAI(api_key=settings.OPENAI_API_KEY)


@api_view(["POST"])
def chat_view(request):
    user_input = request.data.get("message")

    if not user_input:
        return Response(
            {"error": "No message provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        response = client.responses.create(
            model="gpt-5.5-2026-04-23",
            input=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input},
            ],
        )
        output_text = (
            response.output[0].content[0].text if response.output else ""
        )
        return Response({"response": output_text})

    except Exception as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def dashboard_view(request):
    # Aggregate job counts by company
    performance_data = (
        Job.objects.values("company__name")
        .annotate(
            total=Count("id"), company_name_lower=Lower("company__name")
        )
        .order_by("-total")
    )
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_velocity = Job.objects.filter(
        applied_date__gte=seven_days_ago
    ).count()

    context = {
        "labels": [item["company__name"] for item in performance_data],
        "counts": [item["total"] for item in performance_data],
        "recent_velocity": recent_velocity,
    }
    return render(request, "jobs/dashboard.html", context)


def export_calendar_pdf(request, year, month):
    cal = MasterCalendar(year, month)
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
    success_url = reverse_lazy("calendar")

    success_message = "Job for %(title)s at %(company)s created successfully!"

    def get_success_message(self, cleaned_data):
        # This allows you to use dynamic data in the message
        return self.success_message % dict(
            cleaned_data,
            company=self.object.company.name,
        )

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        if date_str := self.kwargs.get("date"):
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


class JobView(generic.ListView):
    model = Job
    template_name = "jobs/calendar.html"

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
        today = timezone.now().date()

        # Calculate end of month for a cleaner range query
        last_day_of_month = next_month_date.replace(day=1) - timedelta(days=1)
        job_end_date = min(last_day_of_month, today)

        query = self.request.GET.get("q")

        jobs = Job.objects.filter(
            applied_date__range=(first_day_of_month, job_end_date)
        ).select_related("company")

        # Interviews range (handle datetime boundaries)
        start_dt = timezone.make_aware(timezone.datetime(year, month, 1))
        end_dt = timezone.make_aware(
            timezone.datetime(year, month, last_day_of_month.day, 23, 59, 59)
        )

        interviews = Interview.objects.filter(
            scheduled_time__range=(start_dt, end_dt)
        ).select_related("job__company", "interviewer")

        if query:
            jobs = jobs.filter(
                Q(title__icontains=query) | Q(company__name__icontains=query)
            )
            interviews = interviews.filter(
                Q(job__title__icontains=query)
                | Q(job__company__name__icontains=query)
            )

        jobs_by_day = {}
        for job in jobs:
            d = job.applied_date.day
            jobs_by_day.setdefault(d, []).append(job)
        interviews_by_day = {}
        for interview in interviews:
            d = interview.scheduled_time.day
            interviews_by_day.setdefault(d, []).append(interview)

        cal = MasterCalendar(
            year,
            month,
            search_query=query,
        )
        html_cal = cal.formatmonth(
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
        context["search_query"] = query
        return context


class InterviewDetailView(generic.DetailView):
    queryset = Interview.objects.select_related("job__company", "interviewer")
    template_name = "jobs/interview_detail.html"
    context_object_name = "interview"

    def post(self, request, *args, **kwargs):
        interview = self.get_object()
        interview.feedback = request.POST.get("feedback", "")
        interview.save()
        return redirect("interview_detail", pk=interview.pk)

class JobDetailView(generic.DetailView):
    queryset = Job.objects.select_related("company")
    template_name = "jobs/job_detail.html"
    context_object_name = "job"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["interviews"] = self.object.interviews.select_related(
            "interviewer"
        ).order_by("-scheduled_time")
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
                return redirect("job_detail", slug=self.object.slug)
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
                return redirect("job_detail", slug=self.object.slug)
            # If invalid, return with the specific form errors
            return self.render_to_response(
                self.get_context_data(interviewer_form=form)
            )

        # Fallback: If somehow the POST reached here without a valid
        # button name
        return self.render_to_response(self.get_context_data())


class UnemploymentReportView(generic.ListView):
    model = Job
    template_name = "jobs/unemployment_report.html"
    context_object_name = "jobs"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch all jobs, ordered by date
        all_jobs = (
            Job.objects.all()
            .order_by("-applied_date")
            .select_related("company")
        )

        weeks = OrderedDict()

        for job in all_jobs:
            start, end = get_unemployment_week(job.applied_date)
            week_label = (
                f"{start.strftime('%b %d')} — {end.strftime('%b %d, %Y')}"
            )

            if week_label not in weeks:
                weeks[week_label] = []
            weeks[week_label].append(job)

        context["weekly_log"] = weeks
        return context
