"""Admin registration for campaigns."""

from django.contrib import admin

from apps.campaigns.models import Campaign, OutreachRecord


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "status", "created_at")
    list_filter = ("status",)


@admin.register(OutreachRecord)
class OutreachRecordAdmin(admin.ModelAdmin):
    list_display = ("campaign", "customer", "dispatch_status", "conversion_score")
    list_filter = ("dispatch_status",)
