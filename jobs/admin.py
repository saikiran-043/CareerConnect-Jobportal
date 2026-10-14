from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Job, Application


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("CareerConnect", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("CareerConnect", {"fields": ("role", "email")}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "employment_type", "employer", "is_active", "created_at")
    list_filter = ("employment_type", "is_active")
    search_fields = ("title", "company", "location")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "applicant", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("job__title", "applicant__username", "applicant__email")
