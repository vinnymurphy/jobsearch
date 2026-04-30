import csv
import os
from datetime import datetime

import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from jobs.models import Company, Interview, Interviewer, Job  # noqa: E402

from django.utils.timezone import make_aware  # noqa: E402


def run_import():
    with open("interview.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            co_name = row["Company"].strip()
            role_name = row["Role"].strip()
            interviewer_name = row["Interviewers"].strip()

            # 1. Handle Timezone
            naive_dt = datetime.strptime(row["Date"], "%Y-%m-%d")
            aware_dt = make_aware(naive_dt)

            # 2. Robust Job Lookup We look for a job at that company
            # where the title matches the role
            job_obj = Job.objects.filter(
                company__name__iexact=co_name, title__icontains=role_name
            ).first()

            if job_obj:
                # Get or create interviewer based on unique name +
                # company constraint
                interviewer_obj, _ = Interviewer.objects.get_or_create(
                    name=interviewer_name, company=job_obj.company
                )
                Interview.objects.create(
                    job=job_obj,
                    interviewer=interviewer_obj,
                    scheduled_time=aware_dt,
                    feedback=f"Initial contact for {role_name}",
                )
            else:
                # If no job exists yet, create a "Placeholder" Job so
                # the Interview can save
                print(
                    f"No job found for {role_name} at {co_name}. "
                    "Creating placeholder."
                )
                company_obj, _ = Company.objects.get_or_create(name=co_name)
                new_job = Job.objects.create(
                    title=role_name, company=company_obj, status="open"
                )
                # Get or create interviewer for the placeholder company
                interviewer_obj, _ = Interviewer.objects.get_or_create(
                    name=interviewer_name, company=company_obj
                )
                Interview.objects.create(
                    job=new_job,
                    interviewer=interviewer_obj,
                    scheduled_time=aware_dt,
                )


if __name__ == "__main__":
    run_import()
