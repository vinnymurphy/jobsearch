import calendar
from datetime import date, datetime, timedelta

from django.urls import reverse


def get_date(req_day):
    if req_day:
        year, month = map(int, req_day.split("-"))
        return date(year, month, day=1)
    return datetime.now()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    return f"month={prev_month.strftime('%Y-%m')}"


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    return f"month={next_month.strftime('%Y-%m')}"


class MasterCalendar(calendar.HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super().__init__(firstweekday=calendar.SUNDAY)

    def formatday(self, day, weekday, jobs, interviews):
        if day == 0:
            return "<td class='noday'>&nbsp;</td>"

        day_jobs = jobs.get(day, [])
        day_interviews = interviews.get(day, [])

        d = ""
        for job in day_jobs:
            status_class = "bg-secondary"
            if job.status == "rejected":
                status_class = "bg-danger-subtle text-danger border-danger"
            elif job.status == "interviewing": 
                status_class = "bg-success-subtle text-success border-success"
            elif job.status == "closed":
                status_class = "bg-dark-subtle text-dark border-dark"
            name = job.company.name if job.company else "Unknown Company"
            url = reverse("job_detail", args=[job.id])
            title = job.title
            d += f'<div class="job-entry {status_class} p-1 mb-1 small rounded">'
            d += f"<li class='calendar-event'><a href='{url}' "
            d += f"target='_blank'>{name}</a>{title}</li>"
            d += "</div>"

        for interview in day_interviews:
            url = reverse("interview_detail", args=[interview.id])
            title = interview.job.title if interview.job else "Unknown"
            d += f"<li class='calendar-event bg-interview'><a href='{url}'>"
            d += f"{interview}</a> ({title})</li>"
        return (
            f'<td><span class="date">{day}</span>'
            f'<ul class="list-unstyled">{d}</ul></td>'
        )

    def formatweek(self, theweek, jobs, interviews):
        s = "".join(
            self.formatday(d, wd, jobs, interviews) for (d, wd) in theweek
        )
        return f"<tr>{s}</tr>"

    def formatmonth(
        self, withyear=True, jobs=None, interviews=None, **kwargs
    ):
        jobs = jobs or {}
        interviews = interviews or {}
        month_name = self.formatmonthname(
            self.year, self.month, withyear=withyear
        )
        cal = '<table class="table table-bordered calendar">\n'
        cal += f"{month_name}\n"
        cal += f"{self.formatweekheader()}\n"
        cal += "<tbody>"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, jobs, interviews)}\n"
        cal += "</tbody></table>"
        return cal

def get_unemployment_week(d):
    # Adjust to the previous Sunday
    start = d - timedelta(days=(d.weekday() + 1) % 7)
    end = start + timedelta(days=6)
    return start, end
