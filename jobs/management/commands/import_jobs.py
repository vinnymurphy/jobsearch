from jobs.models import Industry, Job

import csv

from django.core.management.base import BaseCommand
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Imports jobs from a CSV string or file"

    def handle(self, *args, **options):
        # Your CSV data
        csv_data = """Job Title,Company,Date
Senior Software Engineer,Redhat,2026-01-29
Senior DevOps Engineer,NVIDIA,2026-01-30
Software Engineer,Redhat,2026-02-05
Software Linux Engineer - Installation and Packaging,NVIDIA,2026-02-05
Senior Build Engineer,Sonos,2026-02-13
Production Engineering,Meta,2026-02-13
Senior Software Engineer,Snyk,2026-02-13
Senior Site Reliability Engineer,Redhat,2026-02-20
Staff Software Engineer - SRE Backend (Reliability Engineering),\
Affirm,2026-02-20
Sr. System Development Engineer; Amazon Technologies Portfolio;\
 Reliability Engineering,Amazon,2026-02-20
Senior Systems Integration Engineer; Senior Systems Integration \
Engineer, NVIDIA,2026-02-23
Staff Software Engineer,GitHub,2026-02-26
Sr. Software System Designer (Continuous Integration),AMD,2026-02-26"""

        # Using splitlines and csv.DictReader
        reader = csv.DictReader(csv_data.strip().splitlines())

        # We need a default Industry for these jobs
        default_industry, _ = Industry.objects.get_or_create(
            name="Software Engineering"
        )

        count = 0
        for row in reader:
            title = row["Job Title"].strip()
            company = row["Company"].strip()

            # Create the Job record
            # update_or_create prevents duplicates if you run the script twice
            job, created = Job.objects.update_or_create(
                title=title,
                company=company,
                defaults={
                    "industry": default_industry,
                    "status": "open",
                    "description": f"Automated import from {row['Date']}",
                    # slug is handled by the model's save() method usually,
                    # but we can force it here:
                    "slug": slugify(f"{company}-{title}")[:50],
                },
            )
            if created:
                count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully imported {count} new jobs")
        )
