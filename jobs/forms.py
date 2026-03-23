from datetime import date

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
        fields = "__all__"
        widgets = {
            "applied_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "company": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        fields = "__all__"

        def clean_applied_date(self):
            applied_date = self.cleaned_data.get("applied_date")
            if applied_date and applied_date > date.today():
                raise forms.ValidationError(
                    "Applied date cannot be in the future."
                )
            return applied_date


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
