from django.contrib import admin

from .forms import CompanyForm
from .models import Company, Industry, Interview, Interviewer, Job


@admin.register(Interviewer)
class InterviewerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "company")
    search_fields = ("name",)
    list_filter = ("company",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "industry", "created_at")
    search_fields = ("name", "website")
    list_filter = ("industry",)
    form = CompanyForm


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "location",
        "job_type",
        "status",
        "created_at",
        "work_mode",
    )
    list_filter = ("job_type", "status", "level", "work_mode")
    search_fields = ("title", "company", "location")
    prepopulated_fields = {"slug": ("company", "title")}
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "slug",
                    "company",
                    "description",
                    "location",
                )
            },
        ),
        (
            "Job Details",
            {
                "fields": (
                    "job_type",
                    "work_mode",
                )
            },
        ),
        (
            "Compensation",
            {
                "fields": ("salary_min", "salary_max"),
                "description": "Enter the salary range for this job. Both fields are optional.  ",
            },
        ),
        ("Status", {"fields": ("status",)}),
    )
    list_editable = ("status", "work_mode")


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        "candidate_name",
        "interviewer",
        "job",
        "scheduled_time",
    )
    search_fields = ("candidate_name", "job__title")
    list_filter = ("scheduled_time",)
