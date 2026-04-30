import calendar
from datetime import date, datetime, timedelta

from django.urls import reverse


def get_date(req_day):
    """Parses YYYY-MM or YYYY-MM-DD strings into a date object."""
    if not req_day:
        return date.today()
    try:
        return date.fromisoformat(req_day)
    except ValueError:
        # Handle YYYY-MM format by defaulting to the first of the month
        try:
            parts = req_day.split("-")
            if len(parts) == 2:
                return date(int(parts[0]), int(parts[1]), 1)
        except (ValueError, IndexError):
            pass
    return date.today()


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

        events_html = []
        
        # Map statuses to Bootstrap classes
        status_map = {
            "rejected": "bg-danger-subtle text-danger border-danger",
            "interviewing": "bg-success-subtle text-success border-success",
            "closed": "bg-dark-subtle text-dark border-dark",
        }

        for job in day_jobs:
            status_class = status_map.get(job.status, "bg-secondary")
            name = job.company.name if job.company else "Unknown Company"
            url = reverse("job_detail", args=[job.id])
            
            events_html.append(
                f'<div class="job-entry {status_class} p-1 mb-1 small rounded">'
                f'<li class="calendar-event"><a href="{url}" target="_blank">{name}</a>: {job.title}</li>'
                '</div>'
            )

        for interview in day_interviews:
            url = reverse("interview_detail", args=[interview.id])
            title = interview.job.title if interview.job else "Unknown"
            events_html.append(
                f'<li class="calendar-event bg-interview p-1 mb-1 small rounded">'
                f'<a href="{url}">{interview}</a> ({title})</li>'
            )

        content = "".join(events_html)
        return (
            f'<td><span class="date">{day}</span>'
            f'<ul class="list-unstyled">{content}</ul></td>'
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
