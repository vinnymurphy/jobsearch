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

    def __str__(self):
        return f"Interview with {self.candidate_name} for {self.job.title}"


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ("FT", "Full-Time"),
        ("PT", "Part-Time"),
        ("CT", "Contract"),
        ("IN", "Internship"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("applied", "Applied"),
        ("interviewing", "Interviewing"),
        ("rejected", "Rejected"),
        ("closed", "Closed"),
    ]
    LEVEL_CHOICES = [
        ("SR", "Senior"),
        ("ST", "Staff"),
        ("PR", "Principal"),
        ("LD", "Lead"),
    ]
    WORK_MODE_CHOICES = [
        ("remote", "Remote"),
        ("onsite", "On-site"),
        ("hybrid", "Hybrid"),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="jobs"
    )

    location = models.CharField(
        max_length=150
    )  # e.g., "Remote" or "New York, NY"
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, blank=True)

    # Salary range (optional)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)

    job_type = models.CharField(
        max_length=2, choices=JOB_TYPE_CHOICES, default="FT"
    )
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default="open"
    )
    work_mode = models.CharField(
        max_length=10, choices=WORK_MODE_CHOICES, default="onsite"
    )
    applied_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    posted_by = models.CharField(max_length=255, blank=True)
    application_link = models.URLField(blank=True, max_length=1000)

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.company}-{self.title}")
        counter = 1
        while Job.objects.filter(slug=self.slug).exists():
            self.slug = slugify(f"{self.company}-{self.title}-{counter}")
            counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("job_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return f"{self.title} at {self.company}"
