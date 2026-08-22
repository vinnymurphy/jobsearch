from jobs.models import Job

import json
import logging
import os
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger("jobs.commands")


class Command(BaseCommand):
    help = (
        "Generates a cover letter using generic or custom "
        "local templates and externalized profile data."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--id", type=int, help="Database ID of the job position."
        )
        parser.add_argument(
            "--company", type=str, help="Name of the company."
        )
        parser.add_argument(
            "--no-input",
            "--noinput",
            action="store_true",
            help=(
                "Bypass interactive prompts and automatically "
                "select the newest matching job."
            ),
        )
        parser.add_argument(
            "--save",
            action="store_true",
            help="Save the output directly to job.cover_letter.",
        )

    def handle(self, *args, **options):
        job_id = options["id"]
        company_query = options["company"]

        logger.info(
            f"Execution started | Query: '{company_query}' "
            f"| no_input={options['no_input']}"
        )
        job = self.get_selected_job(
            job_id, company_query, options["no_input"]
        )
        if job is None:
            return

        self.announce_selected_job(job)
        rendered_letter = self.render_cover_letter(job)
        self.save_or_output_letter(job, rendered_letter, options["save"])

    def get_selected_job(self, job_id, company_query, no_input):
        """Return a job selected by ID, query, or an interactive prompt."""
        if job_id:
            return Job.objects.get(pk=job_id)
        if not company_query:
            logger.warning("No job ID or company query was provided.")
            raise CommandError("Provide either --id or --company.")

        matching_jobs = Job.objects.filter(
            company__name__icontains=company_query
        ).order_by("-id")
        match_count = matching_jobs.count()
        if not match_count:
            raise CommandError(f"No jobs found matching '{company_query}'.")
        if match_count == 1:
            return matching_jobs.first()
        if no_input:
            return self.select_newest_match(matching_jobs)
        return self.select_job_from_multiple_matches(
            matching_jobs, company_query
        )

    def select_newest_match(self, matching_jobs):
        """Select and announce the newest job when prompting is disabled."""
        selected_job = matching_jobs.first()
        self.stdout.write(
            self.style.WARNING(
                "[NO-INPUT] Multiple records found. Automatically "
                "selected newest match: "
                f"[{selected_job.id}] {selected_job.title}"
            )
        )
        return selected_job

    def announce_selected_job(self, job):
        """Display the selected job before generating its cover letter."""
        self.stdout.write(
            self.style.SUCCESS(
                f"\nSelected: [{job.id}] {job.title} at {job.company.name}"
            )
        )

    def render_cover_letter(self, job):
        """Render the active template using job and profile data."""
        template_text = self.load_active_template()
        context = self.build_template_context(job)
        return template_text.format(**context)

    def load_active_template(self):
        """Load the local override or committed default template."""
        template_dir = os.path.join(
            settings.BASE_DIR, "jobs", "templates", "jobs"
        )
        custom_template_path = os.path.join(
            template_dir, "cover_letter_custom.txt"
        )
        default_template_path = os.path.join(
            template_dir, "cover_letter_default.txt"
        )
        active_template_path = self.get_active_template_path(
            custom_template_path, default_template_path, template_dir
        )
        with open(active_template_path, encoding="utf-8") as template_file:
            return template_file.read()

    def get_active_template_path(
        self, custom_template_path, default_template_path, template_dir
    ):
        """Return the preferred template path and announce the selection."""
        if os.path.exists(custom_template_path):
            self.stdout.write(
                self.style.SUCCESS(
                    "Using local custom template (cover_letter_custom.txt)"
                )
            )
            return custom_template_path
        if os.path.exists(default_template_path):
            self.stdout.write(
                "Using default committed template (cover_letter_default.txt)"
            )
            return default_template_path
        raise CommandError(f"No template found in {template_dir}")

    def build_template_context(self, job):
        """Build the values used to render a cover letter template."""
        return {
            **self.load_profile_data(),
            "date_today": date.today().strftime("%B %d, %Y"),
            "company_name": job.company.name,
            "job_title": job.title,
            "job_bullet_points": self.format_job_bullet_points(job),
        }

    def load_profile_data(self):
        """Load local profile data, falling back to generic placeholders."""
        profile_path = os.path.join(settings.BASE_DIR, "user_profile.json")
        if os.path.exists(profile_path):
            with open(profile_path, encoding="utf-8") as profile_file:
                return json.load(profile_file)
        return {
            "applicant_name": os.getenv("APPLICANT_NAME", "[Your Name]"),
            "applicant_location": os.getenv(
                "APPLICANT_LOCATION", "[Your City, State]"
            ),
            "applicant_email": os.getenv("APPLICANT_EMAIL", "[Your Email]"),
        }

    def format_job_bullet_points(self, job):
        """Format custom job bullets or use the default bullet points."""
        bullets = getattr(job, "key_bullets", [])
        if bullets:
            return "\n".join(f"* {bullet.strip()}" for bullet in bullets)
        return (
            "* Architectural leadership in building resilient CI/CD "
            "pipelines.\n"
            "* Advanced automation using Python and Bash for infrastructure "
            "tooling.\n"
            "* Collaborative incident diagnostics and system reliability "
            "engineering."
        )

    def save_or_output_letter(self, job, rendered_letter, save_to_db):
        """Save the letter to the job or write it to standard output."""
        if not save_to_db:
            self.stdout.write("\n" + "=" * 60 + "\n")
            self.stdout.write(rendered_letter)
            self.stdout.write("=" * 60 + "\n")
            return

        job.cover_letter = rendered_letter
        job.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Saved cover letter to database for job ID {job.id}."
            )
        )

    def select_job_from_multiple_matches(self, matching_jobs, company_query):
        """Prompt the user to choose one job from matching company records."""
        self.stdout.write(
            self.style.WARNING(
                f"\nMultiple jobs found for '{company_query}':\n"
            )
        )
        job_list = list(matching_jobs)
        for index, job in enumerate(job_list, start=1):
            created_str = (
                job.created_at.strftime("%Y-%m-%d")
                if hasattr(job, "created_at") and job.created_at
                else f"ID {job.id}"
            )
            self.stdout.write(
                f"  [{index}] {job.title} ({job.company.name}) - "
                f"{created_str} [Status: {job.status}]"
            )

        while True:
            choice = input(
                f"\nSelect a job (1-{len(job_list)}) or 'q' to quit: "
            ).strip()

            if choice.lower() == "q":
                self.stdout.write(self.style.NOTICE("Selection canceled."))
                return None

            if choice.isdigit() and 1 <= int(choice) <= len(job_list):
                return job_list[int(choice) - 1]

            self.stdout.write(
                self.style.ERROR(
                    "Invalid choice. Please enter a number between 1 "
                    f"and {len(job_list)}."
                )
            )
