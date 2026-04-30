import re

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


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

    class Meta:
        ordering = ["-scheduled_time"]

    def __str__(self):
        return f"Interview with {self.candidate_name} for {self.job.title}"


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
    slug = models.SlugField(unique=True, blank=True)
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

            if base_slug in existing:
                pattern = re.compile(rf"^{re.escape(base_slug)}-(\d+)$")
                suffixes = [
                    int(m.group(1))
                    for s in existing
                    if (m := pattern.match(s))
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
