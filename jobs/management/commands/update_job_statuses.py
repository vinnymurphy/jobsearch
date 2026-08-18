from jobs.models import Job

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Bulk updates job application statuses prior to a specified date."

    def add_arguments(self, parser):
        # Mandatory positional argument: Cutoff date (YYYY-MM-DD)
        parser.add_argument(
            "cutoff_date",
            type=str,
            help=(
                "Cutoff date in YYYY-MM-DD format "
                "(jobs BEFORE this date will be updated)."
            ),
        )

        # Optional argument: Status value to apply (defaults to REJECTED)
        parser.add_argument(
            "--status",
            type=str,
            default="REJECTED",
            help="The new status value to apply (default: REJECTED).",
        )

        # Optional argument: Field name to filter on (default: created_at)
        parser.add_argument(
            "--date-field",
            type=str,
            default="created_at",
            choices=["created_at", "closing_date"],
            help="Which model field to filter against (default: created_at).",
        )

        # Optional company filter, matched case-insensitively against the
        # company name.
        parser.add_argument(
            "--company",
            type=str,
        )

        # Flag to preview changes without modifying the database
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the update without altering records.",
        )

    def handle(self, *args, **options):
        raw_date = options["cutoff_date"]
        new_status = options["status"]
        date_field = options["date_field"]
        company_name = options["company"]
        dry_run = options["dry_run"]

        # Parse date input
        try:
            cutoff_dt = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError as e:
            raise CommandError(
                "Invalid date format. Please use YYYY-MM-DD."
            ) from e

        # Construct dynamic lookup query (e.g., created_at__date__lt)
        filter_kwargs = {f"{date_field}__date__lt": cutoff_dt}
        if company_name:
            filter_kwargs["company__name__iexact"] = company_name

        queryset = Job.objects.filter(**filter_kwargs)
        match_count = queryset.count()

        company_description = (
            f" for company '{company_name}'" if company_name else ""
        )

        if match_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    f"No jobs found with {date_field} before {cutoff_dt}"
                    f"{company_description}."
                )
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"[DRY RUN] Found {match_count} job(s) before {cutoff_dt}"
                    f"{company_description} to update to "
                    f"status '{new_status}'."
                )
            )
            for job in queryset[:5]:
                self.stdout.write(
                    f"  - [{job.id}] {job.title} at {job.company.name}"
                )
            if match_count > 5:
                self.stdout.write(f"  ... and {match_count - 5} more.")
            return

        # Perform bulk update
        updated_count = queryset.update(status=new_status)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated {updated_count} "
                f"job(s) to status '{new_status}'."
            )
        )
