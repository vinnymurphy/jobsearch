from django.test import TestCase, Client
from django.urls import reverse
import factory
from .models import Job, Company

# Simple Factory to generate test data
class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job
    title = factory.Faker('job')
    company = factory.LazyAttribute(lambda o: Company.objects.create(name="Test Corp"))

class PDFExportTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a few jobs so the calendar has events to render
        JobFactory.create_batch(3)

    def test_pdf_export_status_and_type(self):
        """Verify the PDF view returns 200 and correct Content-Type."""
        url = reverse('export_pdf', kwargs={'year': 2026, 'month': 3})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        
    def test_pdf_filename_header(self):
        """Ensure the filename is formatted correctly."""
        url = reverse('export_pdf', kwargs={'year': 2026, 'month': 3})
        response = self.client.get(url)
        self.assertIn('filename=calendar_2026_3.pdf', response['Content-Disposition'])
