import re

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from pypdf import PdfReader


def validate_not_reserved(value):
    if value.lower() == "add":
        raise ValidationError(
            "The slug 'add' is reserved for system routing."
        )


class Resume(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Name of the resume (e.g., 'Software Engineer Resume')",
    )
    raw_text = models.TextField(
        help_text="The extracted plain text used for LLM context processing."
    )
    pdf_file = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True,
        help_text="Optional original PDF storage.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            "Designates if this is the primary resume "
            "for default match comparisons."
        ),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the resume was created.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Resumes"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} (Active: {self.is_active})"

    def save(self, *args, **kwargs):
        # If a file is uploaded and raw_text is missing, extract it
        # right away
        if self.pdf_file and not self.raw_text:
            try:
                # Open the file stream directly from the FileField
                # memory/storage
                reader = PdfReader(self.pdf_file)
                extracted_pages = []

                for page in reader.pages:
                    if text := page.extract_text():
                        extracted_pages.append(text)

                # Join all pages with standard newlines and save to
                # the database field
                self.raw_text = "\n\n".join(extracted_pages).strip()

            except Exception as e:
                # Falling back gracefully so file saves don't
                # hard-crash the app if a PDF is corrupted
                self.raw_text = (
                    "[ERROR] Failed to automatically parse text "
                    f"from PDF: {str(e)}"
                )
        if self.is_active:
            # Deactivate other resumes
            Resume.objects.filter(is_active=True).exclude(pk=self.pk).update(
                is_active=False
            )
        super().save(*args, **kwargs)


class Industry(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Industries"

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    industry = models.ForeignKey(
        Industry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Interviewer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interviewers",
    )

    class Meta:
        unique_together = ("name", "company")

    def __str__(self):
        return self.name


class Interview(models.Model):
    job = models.ForeignKey(
        "Job", on_delete=models.CASCADE, related_name="interviews"
    )
    interviewer = models.ForeignKey(
        Interviewer, on_delete=models.SET_NULL, null=True, blank=True
    )
    candidate_name = models.CharField(max_length=255, default="Vinny Murphy")
    scheduled_time = models.DateTimeField()
    feedback = models.TextField(blank=True)

    meeting_link = models.URLField(blank=True, max_length=1000)

    class Meta:
        ordering = ["-scheduled_time"]

    def __str__(self):
        # Fallback if an interviewer isn't assigned yet (e.g., 'Hiring Team')
        manager = self.interviewer.name if self.interviewer else "Hiring Team"

        # Safely fetch the company name from the related Job model
        company = (
            self.job.company.name
            if self.job and hasattr(self.job, "company")
            else "Unknown Company"
        )

        return f"Interview with {manager} at {company}"


class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = "FT", "Full-Time"
        PART_TIME = "PT", "Part-Time"
        CONTRACT = "CT", "Contract"
        INTERNSHIP = "IN", "Internship"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        APPLIED = "applied", "Applied"
        NEGOTIATING = "negotiating", "Negotiating"
        INTERVIEWING = "interviewing", "Interviewing"
        REJECTED = "rejected", "Rejected"
        CLOSED = "closed", "Closed"

    class Level(models.TextChoices):
        SENIOR = "SR", "Senior"
        STAFF = "ST", "Staff"
        PRINCIPAL = "PR", "Principal"
        LEAD = "LD", "Lead"

    class WorkMode(models.TextChoices):
        REMOTE = "remote", "Remote"
        ONSITE = "onsite", "On-site"
        HYBRID = "hybrid", "Hybrid"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="jobs"
    )
    match_score = models.JSONField(
        null=True,
        blank=True,
        help_text="Semantic match score (0-100) generated by LLM",
    )
    last_matched_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last semantic match",
    )
    location = models.CharField(max_length=150)
    level = models.CharField(max_length=2, choices=Level.choices, blank=True)

    # Salary range (optional)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)

    job_type = models.CharField(
        max_length=2, choices=JobType.choices, default=JobType.FULL_TIME
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    work_mode = models.CharField(
        max_length=10, choices=WorkMode.choices, default=WorkMode.ONSITE
    )
    applied_date = models.DateField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(
        unique=True, blank=True, validators=[validate_not_reserved]
    )
    expiry_date = models.DateField(null=True, blank=True)
    posted_by = models.CharField(max_length=255, blank=True)
    application_link = models.URLField(blank=True, max_length=1000)

    class Meta:
        ordering = ["-applied_date"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.company}-{self.title}")

            # Find all existing slugs starting with this base in one query
            existing = Job.objects.filter(
                slug__startswith=base_slug
            ).values_list("slug", flat=True)

            if base_slug in existing or base_slug == "add":
                pattern = re.compile(rf"^{re.escape(base_slug)}-(\d+)$")
                suffixes = [
                    int(m[1]) for s in existing if (m := pattern.match(s))
                ]
                self.slug = (
                    f"{base_slug}-{max(suffixes) + 1 if suffixes else 1}"
                )
            else:
                self.slug = base_slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("job_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return f"{self.title} at {self.company}"
