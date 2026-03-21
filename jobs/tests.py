from .models import Company, Industry, Job

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
        url = reverse("job_calendar") + "?year=2026&month=3"

        # We expect ~5-7 queries: Session, User, Jobs (1 JOIN),
        # Interviews, etc.  Without select_related, this would be 25+.
        with self.assertNumQueries(4):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
