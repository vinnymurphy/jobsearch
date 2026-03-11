import calendar
from datetime import date, datetime, timedelta

from django.urls import reverse

from .models import Interview, Job


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
        print(f"DEBUG: {year=} {month=}")

        super().__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events, interviews):
        # Filter the jobs that fall on this specific day
        events_per_day = events.filter(created_at__day=day)
        print(f"DEBUG: {events_per_day=}")
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
        print(f"{day=}")
        if day != 0:
            return("<td>"
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

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n"
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, events)}\n"
        cal += f"</table>"
        return cal


class JobCalendar(calendar.HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super().__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(created_at__day=day)
        d = ""
        STATUS_CLASSES = {
            "open": "bg-open",
            "closed": "bg-closed",
            "draft": "bg-draft",
            "applied": "bg-open",  # You can map multiple statuses to one color
            "rejected": "bg-closed",
        }
        for event in events_per_day:
            url = reverse("job_detail", args=[event.id])
            current_status = event.status.lower() if event.status else "draft"
            color_class = STATUS_CLASSES.get(current_status, "bg-draft")

            company_name = (
                event.company.name if event.company else "Unknown Company"
            )
            title = event.title
            # Add a link to the interview or just show the company name
            d += f"<li class='calendar-event'><a href='{url}' target='_blank'>{company_name}</a> ({title})</li>"
        if day != 0:
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
        events = Job.objects.filter(
            created_at__year=self.year, created_at__month=self.month
        )

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n"
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, events)}\n"
        cal += f"</table>"
        return cal
