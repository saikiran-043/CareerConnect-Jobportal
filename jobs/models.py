from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings


class User(AbstractUser):
    class Role(models.TextChoices):
        SEEKER = "seeker", "Job seeker"
        EMPLOYER = "employer", "Employer"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.SEEKER)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Job(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full-time"
        PART_TIME = "part_time", "Part-time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"
        REMOTE = "remote", "Remote"

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posted_jobs"
    )
    title = models.CharField(max_length=160)
    company = models.CharField(max_length=120)
    location = models.CharField(max_length=120)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices)
    salary = models.CharField(max_length=100, blank=True, help_text="Example: ₹4–6 LPA or Negotiable")
    description = models.TextField()
    requirements = models.TextField(blank=True, help_text="One requirement per line is recommended.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.company}"


def resume_upload_path(instance, filename):
    # Do not trust user-supplied directory names.
    import os
    from uuid import uuid4
    extension = os.path.splitext(filename)[1].lower()
    return f"resumes/{uuid4().hex}{extension}"


class Application(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        REVIEWING = "reviewing", "Under review"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    resume = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    cover_letter = models.TextField(blank=True, max_length=5000)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SUBMITTED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["job", "applicant"], name="unique_job_applicant")
        ]

    def __str__(self):
        return f"{self.applicant.username} → {self.job.title}"
