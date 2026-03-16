import calendar
from datetime import date, datetime, timedelta

from django.urls import reverse

from .models import Interview


def get_date(req_day):
    if req_day:
        year, month = map(int, req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    return f"month={prev_month.strftime('%Y-%m')}"


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    return f"month={next_month.strftime('%Y-%m')}"


class InterviewCalendar(calendar.HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super().__init__(firstweekday=calendar.SUNDAY)

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events, interviews):
        # Filter the jobs that fall on this specific day
        events_per_day = events.filter(created_at__day=day)
        d = ""

        for event in events_per_day:
            url = reverse("job_detail", args=[event.id])

            # 1. Determine the status color class
            # We use .get() or a default to avoid crashes if status is empty
            status = event.status.lower() if event.status else "draft"

            if status == "closed":
                color_class = "bg-closed"
            elif status == "draft":
                color_class = "bg-draft"
            else:
                color_class = "bg-open"

            company_name = (
                event.company.name if event.company else "Unknown Company"
            )
            title = event.title

            # 2. Inject the color_class into the <li>
            d += f"<li class='calendar-event {color_class}'><a href='{url}'>{company_name}</a> ({title})</li>"
        if day != 0:
            return (
                "<td>"
                f"<a href='{url}' class='date-link' title='Add job for this day'>{day}</a>"
                f"<ul> {d} </ul>"
                "</td>"
            )
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return "<td></td>"

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ""
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f"<tr> {week} </tr>"

    # formats a month as a table
    def formatmonth(self, withyear=True):
        # Gather all interviews for the given month and year
        events = Interview.objects.filter(
            scheduled_time__year=self.year, scheduled_time__month=self.month
        )

        cal = '<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n"
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, events)}\n"
        cal += "</table>"
        return cal


class JobCalendar(calendar.HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super().__init__(firstweekday=calendar.SUNDAY)

    # formats a day as a td
    # filter events by day
    def formatday(self, day, weekday, jobs, interviews):
        if day == 0:
            return "<td></td>"
        day_jobs = jobs.get(day, [])
        d = ""

        for job in day_jobs:
            url = reverse("job_detail", args=[job.id])
            company_name = (
                job.company.name if job.company else "Unknown Company"
            )
            title = job.title
            # Add a link to the interview or just show the company name
            d += f"<li class='calendar-event'><a href='{url}' target='_blank'>{company_name}</a> ({title})</li>"

        interview_days = interviews.get(day, [])
        for interview in interview_days:
            url = reverse("interview_detail", args=[interview.id])
            title = interview.job.title if interview.job else "Unknown"
            d += f"<li class='calendar-event bg-interview'><a href='{url}'>{interview}</a> ({title})</li>"
        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return "<td></td>"

    def formatmonth(
        self, theyear, themonth, withyear=True, jobs=None, interviews=None
    ):
        jobs = jobs or {}
        interviews = interviews or {}

        cal = '<table class="calendar">\n'
        cal += (
            f"{self.formatmonthname(theyear, themonth, withyear=withyear)}\n"
        )
        cal += f"{self.formatweekheader()}\n"

        # This is where we pass the data to each week
        for week in self.monthdays2calendar(theyear, themonth):
            cal += f"{self.formatweek(week, jobs, interviews)}\n"
        cal += "</table>"
        return cal

    def formatweek(self, theweek, jobs, interviews):
        week = ""
        for d, weekday in theweek:
            # And pass it to each day
            week += self.formatday(d, weekday, jobs, interviews)
        return f"<tr> {week} </tr>"
