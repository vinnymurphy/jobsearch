from typing import Any

from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.views import generic
from django.template.loader import render_to_string
from django.http import HttpRequest, HttpResponse
from weasyprint import HTML
from django.urls import reverse_lazy


from .forms import IndustryForm, InterviewerForm, InterviewForm, JobForm
from .models import Interview, Job
from .utils import (
    InterviewCalendar,
    JobCalendar,
    get_date,
    next_month,
    prev_month,
)


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

class JobCreateView(generic.CreateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"
    success_url = reverse_lazy("job_calendar")

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        date_str = self.kwargs.get("date")
        if date_str:
            initial['applied_date'] = get_date(date_str)
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

        # Get current year and month
        req_month = self.request.GET.get("month", None)
        d = get_date(req_month)

        # Instantiate our calendar class
        cal = JobCalendar(d.year, d.month)

        # Call the formatmonth method, which returns our HTML as a string
        html_cal = cal.formatmonth(withyear=True)

        # mark_safe tells Django to render the HTML string as actual HTML
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)
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
