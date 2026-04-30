from .models import Company, Industry, Interview, Interviewer, Job

from datetime import date

from django import forms


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
            "company",
            "applied_date",
            "location",
            "job_type",
            "work_mode",
            "level",
            "salary_min",
            "salary_max",
            "application_link",
            "expiry_date",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Senior Software Engineer",
                }
            ),
            "company": forms.Select(
                attrs={
                    "class": "form-select select2-enable",
                    "data-placeholder": "Search or select a company...",
                }
            ),
            "applied_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Remote or New York, NY",
                }
            ),
            "job_type": forms.Select(attrs={"class": "form-select"}),
            "work_mode": forms.Select(attrs={"class": "form-select"}),
            "level": forms.Select(attrs={"class": "form-select"}),
            "salary_min": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Min"}
            ),
            "salary_max": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Max"}
            ),
            "application_link": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
            "expiry_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "class": "form-control",
                    "placeholder": "Paste job description here...",
                }
            ),
        }

    def clean_applied_date(self):
        applied_date = self.cleaned_data.get("applied_date")
        if applied_date and applied_date > date.today():
            raise forms.ValidationError(
                "Applied date cannot be in the future."
            )
        return applied_date

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get("salary_min")
        salary_max = cleaned_data.get("salary_max")

        if salary_min and salary_max and salary_max < salary_min:
            self.add_error(
                "salary_max", "Maximum salary cannot be less than minimum."
            )
        return cleaned_data


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
