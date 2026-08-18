from .models import Company, Industry, Interview, Job
from .utils import get_unemployment_week

from datetime import date, datetime
from io import StringIO
from unittest.mock import patch

import factory
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone


# Simple Factory to generate test data
class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    title = factory.Faker("job")
    company = factory.LazyAttribute(
        lambda o: Company.objects.create(name="Test Corp")
    )


class PDFExportTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a few jobs so the calendar has events to render
        JobFactory.create_batch(3)

    def test_pdf_export_status_and_type(self):
        """Verify the PDF view returns 200 and correct Content-Type."""
        url = reverse("export_pdf", kwargs={"year": 2026, "month": 3})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_pdf_filename_header(self):
        """Ensure the filename is formatted correctly."""
        url = reverse("export_pdf", kwargs={"year": 2026, "month": 3})
        response = self.client.get(url)
        self.assertIn(
            "filename=calendar_2026_3.pdf", response["Content-Disposition"]
        )


class JobPerformanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.industry = Industry.objects.create(name="Tech")
        self.company = Company.objects.create(
            name="Cisco", industry=self.industry
        )

        # Create 20 jobs for March 2026
        for i in range(20):
            Job.objects.create(
                title=f"Engineer {i}", company=self.company, status="open"
            )

    def test_calendar_query_efficiency(self):
        """
        Verify that 20 jobs don't cause 20+ queries.
        With select_related, it should be a constant low number.
        """
        url = reverse("calendar") + "?year=2026&month=3"

        # We expect ~5-7 queries: Session, User, Jobs (1 JOIN),
        # Interviews, etc.  Without select_related, this would be 25+.
        with self.assertNumQueries(4):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_calendar_uses_event_pill_markup(self):
        job = Job.objects.create(
            title="Global Solutions Architect",
            company=self.company,
            applied_date=date(2026, 3, 9),
            status=Job.Status.OPEN,
        )
        url = reverse("calendar") + "?year=2026&month=3"

        response = self.client.get(url)

        self.assertContains(response, '<ul class="calendar-events">')
        self.assertContains(
            response,
            (
                '<li class="calendar-event job-entry status-open">'
                f'<a href="{job.get_absolute_url()}" '
                'class="calendar-event-link">'
            ),
        )
        self.assertNotContains(response, '<ul class="list-unstyled">')
        self.assertNotContains(response, '<div class="job-entry')


class JobDetailStatusTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.industry = Industry.objects.create(name="Software")
        self.company = Company.objects.create(
            name="Test Corp",
            industry=self.industry,
            website="https://example.com",
        )
        self.job = Job.objects.create(
            title="Software Engineer",
            company=self.company,
            status=Job.Status.OPEN,
            applied_date=date(2026, 3, 25),
            application_link="https://example.com/jobs/software-engineer",
        )

    def test_detail_shows_company_industry(self):
        url = reverse("job_detail", kwargs={"slug": self.job.slug})

        response = self.client.get(url)

        self.assertContains(response, "Software")

    def test_detail_shows_company_and_job_links(self):
        url = reverse("job_detail", kwargs={"slug": self.job.slug})

        response = self.client.get(url)

        self.assertContains(response, 'href="https://example.com"')
        self.assertContains(
            response, 'href="https://example.com/jobs/software-engineer"'
        )

    def test_detail_shows_reporting_period(self):
        url = reverse("job_detail", kwargs={"slug": self.job.slug})

        response = self.client.get(url)

        self.assertContains(response, "Reporting Period:")
        self.assertContains(response, "March 22, 2026")
        self.assertContains(response, "March 28, 2026")

    def test_can_change_job_status_from_detail(self):
        url = reverse("job_detail", kwargs={"slug": self.job.slug})

        response = self.client.post(
            url, {"transition_status": Job.Status.INTERVIEWING}
        )

        self.job.refresh_from_db()
        self.assertRedirects(response, url)
        self.assertEqual(self.job.status, Job.Status.INTERVIEWING)

    def test_invalid_status_does_not_change_job(self):
        url = reverse("job_detail", kwargs={"slug": self.job.slug})

        response = self.client.post(url, {"transition_status": "bogus"})

        self.job.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.job.status, Job.Status.OPEN)

    def test_interview_feedback_renders_markdown(self):
        Interview.objects.create(
            job=self.job,
            scheduled_time=timezone.now(),
            feedback="**Great fit**\n\n- Follow up",
        )
        url = reverse("job_detail", kwargs={"slug": self.job.slug})

        response = self.client.get(url)

        self.assertContains(response, "<strong>Great fit</strong>", html=True)
        self.assertContains(response, "<li>Follow up</li>", html=True)

    def test_interviews_render_earliest_to_latest(self):
        later = timezone.now() + timezone.timedelta(days=2)
        earlier = timezone.now() + timezone.timedelta(days=1)
        Interview.objects.create(
            job=self.job,
            scheduled_time=later,
            feedback="Second interview",
        )
        Interview.objects.create(
            job=self.job,
            scheduled_time=earlier,
            feedback="First interview",
        )
        url = reverse("job_detail", kwargs={"slug": self.job.slug})

        response = self.client.get(url)

        self.assertContains(response, "First interview")
        self.assertContains(response, "Second interview")
        self.assertLess(
            response.content.index(b"First interview"),
            response.content.index(b"Second interview"),
        )


class InterviewDetailStatusTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(name="Test Corp")
        self.job = Job.objects.create(
            title="Software Engineer",
            company=self.company,
            status=Job.Status.OPEN,
        )
        self.interview = Interview.objects.create(
            job=self.job,
            scheduled_time=timezone.now(),
            feedback="Existing notes",
        )

    def test_detail_shows_job_status_choices(self):
        url = reverse("interview_detail", kwargs={"pk": self.interview.pk})

        response = self.client.get(url)

        self.assertContains(response, "Job Status:")
        self.assertContains(response, "Interviewing")
        self.assertContains(response, "Rejected")

    def test_can_change_job_status_from_interview_detail(self):
        url = reverse("interview_detail", kwargs={"pk": self.interview.pk})

        response = self.client.post(
            url, {"transition_status": Job.Status.NEGOTIATING}
        )

        self.job.refresh_from_db()
        self.interview.refresh_from_db()
        self.assertRedirects(response, url)
        self.assertEqual(self.job.status, Job.Status.NEGOTIATING)
        self.assertEqual(self.interview.feedback, "Existing notes")


class UnemploymentReportingTests(TestCase):
    """Test suite for the Sunday-to-Saturday logical windowing system.
    Ensures compliance with state-mandated reporting periods.
    """

    def test_sunday_stays_on_sunday(self):
        """An application on a Sunday (2026-03-22) should mark that
        specific Sunday as the start of the reporting week.
        """
        self.sunday_to_saturday_span(22)

    def test_monday_rolls_back_to_sunday(self):
        """An application on a Monday (2026-03-23) should roll back to
        the previous Sunday (2026-03-22) for the week start.
        """
        self.sunday_to_saturday_span(23)

    def test_saturday_is_end_of_week(self):
        """An application on a Saturday (2026-03-28) should roll back
        to the previous Sunday (2026-03-22).
        """
        self.sunday_to_saturday_span(28)

    def test_mid_week_calculation(self):
        """A Wednesday application should correctly identify the
        surrounding Sunday-to-Saturday window.
        """
        self.sunday_to_saturday_span(25)

    def test_report_template_shows_reporting_period(self):
        company = Company.objects.create(name="Test Corp")
        Job.objects.create(
            title="Software Engineer",
            company=company,
            applied_date=date(2026, 3, 25),
        )
        url = reverse("unemployment_report")
        now = timezone.make_aware(datetime(2026, 3, 29, 9, 0))

        with patch("jobs.unemployment.timezone.now", return_value=now):
            response = self.client.get(url)

        self.assertContains(response, "Reporting Period:")
        self.assertContains(response, "March 22, 2026")
        self.assertContains(response, "March 29, 2026")

    def test_report_links_applications_to_job_detail(self):
        company = Company.objects.create(name="Test Corp")
        job = Job.objects.create(
            title="Software Engineer",
            company=company,
            applied_date=date(2026, 3, 25),
        )
        url = reverse("unemployment_report")
        now = timezone.make_aware(datetime(2026, 3, 29, 9, 0))

        with patch("jobs.unemployment.timezone.now", return_value=now):
            response = self.client.get(url)

        self.assertContains(response, f'href="{job.get_absolute_url()}"')

    def sunday_to_saturday_span(self, arg0):
        """Helper that asserts an application date resolves to the
        expected reporting window.  It validates that the unemployment
        week always spans the same Sunday-to-Saturday period.
        """
        applied_date = date(2026, 3, arg0)
        start, end = get_unemployment_week(applied_date)
        self.assertEqual(start, date(2026, 3, 22))
        self.assertEqual(end, date(2026, 3, 28))


class UpdateJobStatusesCommandTests(TestCase):
    def test_company_filter_only_selects_matching_company(self):
        target_company = Company.objects.create(name="Acme Corp")
        other_company = Company.objects.create(name="Other Corp")
        target_job = Job.objects.create(
            title="Target role",
            company=target_company,
            status=Job.Status.OPEN,
        )
        other_job = Job.objects.create(
            title="Other role", company=other_company, status=Job.Status.OPEN
        )
        output = StringIO()

        call_command(
            "update_job_statuses",
            (timezone.localdate() + timezone.timedelta(days=1)).isoformat(),
            "--company",
            "acme corp",
            "--status",
            Job.Status.REJECTED,
            stdout=output,
        )

        target_job.refresh_from_db()
        other_job.refresh_from_db()
        self.assertEqual(target_job.status, Job.Status.REJECTED)
        self.assertEqual(other_job.status, Job.Status.OPEN)
        self.assertIn("Successfully updated 1 job(s)", output.getvalue())
