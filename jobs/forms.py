from django import forms

from .models import Company, Industry, Interview, Interviewer, Job


class InterviewerForm(forms.ModelForm):
    class Meta:
        model = Interviewer
        fields = ["name", "email", "phone", "company"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "John Doe"}),
            "email": forms.EmailInput(
                attrs={"placeholder": "john.doe@example.com"}
            ),
            "phone": forms.TextInput(attrs={"placeholder": "123-456-7890"}),
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "website", "description", "industry"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "slug",
            "company",
            "description",
            "location",
            "salary_min",
            "salary_max",
            "job_type",
            "level",
            "status",
            "work_mode",
            "expiry_date",
            "application_link",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        fields = "__all__"


class IndustryForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = ["name"]


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            "interviewer",
            "candidate_name",
            "scheduled_time",
        ]
        widgets = {
            "scheduled_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }
