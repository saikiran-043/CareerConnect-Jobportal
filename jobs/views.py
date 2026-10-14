from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RegisterForm, JobForm, ApplicationForm
from .models import User, Job, Application


def home(request):
    jobs = Job.objects.filter(is_active=True).select_related("employer")
    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    employment_type = request.GET.get("type", "").strip()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | Q(company__icontains=query)
            | Q(description__icontains=query) | Q(requirements__icontains=query)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    valid_types = {choice[0] for choice in Job.EmploymentType.choices}
    if employment_type in valid_types:
        jobs = jobs.filter(employment_type=employment_type)

    return render(request, "jobs/home.html", {
        "jobs": jobs, "query": query, "location": location,
        "selected_type": employment_type, "employment_types": Job.EmploymentType.choices,
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    if request.user.role == User.Role.EMPLOYER:
        jobs = Job.objects.filter(employer=request.user)
        applications = Application.objects.filter(job__employer=request.user).select_related(
            "job", "applicant"
        )
        return render(request, "jobs/employer_dashboard.html", {
            "jobs": jobs, "applications": applications[:8],
            "job_count": jobs.count(), "application_count": applications.count(),
        })
    applications = Application.objects.filter(applicant=request.user).select_related("job")
    return render(request, "jobs/seeker_dashboard.html", {
        "applications": applications[:10], "application_count": applications.count(),
        "recent_jobs": Job.objects.filter(is_active=True)[:5],
    })


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related("employer"), pk=pk, is_active=True)
    already_applied = (
        request.user.is_authenticated
        and Application.objects.filter(job=job, applicant=request.user).exists()
    )
    return render(request, "jobs/job_detail.html", {
        "job": job, "already_applied": already_applied,
    })


@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    if request.user.role != User.Role.SEEKER:
        return HttpResponseForbidden("Only job seekers can apply for jobs.")
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, "You have already applied for this job.")
        return redirect("job_detail", pk=job.pk)
    form = ApplicationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.applicant = request.user
        application.save()
        messages.success(request, "Your application has been submitted.")
        return redirect("my_applications")
    return render(request, "jobs/apply.html", {"form": form, "job": job})


@login_required
def my_applications(request):
    if request.user.role != User.Role.SEEKER:
        return HttpResponseForbidden("This page is for job seekers.")
    applications = Application.objects.filter(applicant=request.user).select_related("job")
    return render(request, "jobs/my_applications.html", {"applications": applications})


def employer_required(view_func):
    from functools import wraps
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if request.user.role != User.Role.EMPLOYER:
            return HttpResponseForbidden("Employer account required.")
        return view_func(request, *args, **kwargs)
    return _wrapped


@employer_required
def job_create(request):
    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.employer = request.user
        job.save()
        messages.success(request, "Job posted successfully.")
        return redirect("dashboard")
    return render(request, "jobs/job_form.html", {"form": form, "heading": "Post a new job"})


@employer_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    form = JobForm(request.POST or None, instance=job)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Job listing updated.")
        return redirect("dashboard")
    return render(request, "jobs/job_form.html", {"form": form, "heading": "Edit job"})


@employer_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job listing deleted.")
        return redirect("dashboard")
    return render(request, "jobs/job_confirm_delete.html", {"job": job})


@employer_required
def employer_applications(request):
    applications = Application.objects.filter(job__employer=request.user).select_related(
        "job", "applicant"
    )
    return render(request, "jobs/employer_applications.html", {"applications": applications})


@employer_required
@require_POST
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, job__employer=request.user)
    new_status = request.POST.get("status", "")
    valid_statuses = {choice[0] for choice in Application.Status.choices}
    if new_status in valid_statuses:
        application.status = new_status
        application.save(update_fields=["status"])
        messages.success(request, "Application status updated.")
    else:
        messages.error(request, "Invalid application status.")
    return redirect("employer_applications")
