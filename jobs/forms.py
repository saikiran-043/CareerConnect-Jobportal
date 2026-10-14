from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Job, Application


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Role.choices, widget=forms.Select())

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = (
            "title", "company", "location", "employment_type", "salary",
            "description", "requirements", "is_active",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("resume", "cover_letter")
        widgets = {
            "cover_letter": forms.Textarea(attrs={
                "rows": 5, "placeholder": "Tell the employer why you are a good fit (optional)."
            }),
        }

    def clean_resume(self):
        resume = self.cleaned_data["resume"]
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Resume must be 5 MB or smaller.")
        if not resume.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Please upload a PDF resume.")
        return resume
