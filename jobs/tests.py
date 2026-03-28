from .models import Company, Industry, Job
from .utils import get_unemployment_week

from datetime import date

import factory
from django.test import Client, TestCase
from django.urls import reverse


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

    def sunday_to_saturday_span(self, arg0):
        """Helper that asserts an application date resolves to the
        expected reporting window.  It validates that the unemployment
        week always spans the same Sunday-to-Saturday period.
        """
        applied_date = date(2026, 3, arg0)
        start, end = get_unemployment_week(applied_date)
        self.assertEqual(start, date(2026, 3, 22))
        self.assertEqual(end, date(2026, 3, 28))
