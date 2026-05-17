"""Admin registration for Relationship Manager accounts."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import RelationshipManager


@admin.register(RelationshipManager)
class RelationshipManagerAdmin(UserAdmin):
    list_display = ("username", "employee_id", "branch_code", "is_active")
    search_fields = ("username", "employee_id", "email")
