"""Campaign and outreach record models."""

import uuid

from django.db import models

from apps.accounts.models import RelationshipManager
from apps.customers.models import Customer


class CampaignStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class Campaign(models.Model):
    """RM-initiated outreach campaign."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        RelationshipManager,
        on_delete=models.PROTECT,
        related_name="campaigns",
        db_index=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=CampaignStatus.choices,
        default=CampaignStatus.DRAFT,
        db_index=True,
    )
    query_text = models.TextField(help_text="Original RM natural-language query")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
        indexes = [
            models.Index(fields=["created_by", "status", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.name


class DispatchStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class OutreachRecord(models.Model):
    """Per-customer outreach outcome within a campaign."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.PROTECT,
        related_name="outreach_records",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="outreach_records",
    )
    conversion_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    message_text = models.TextField(blank=True)
    dispatch_status = models.CharField(
        max_length=16,
        choices=DispatchStatus.choices,
        default=DispatchStatus.PENDING,
        db_index=True,
    )
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Outreach Record"
        verbose_name_plural = "Outreach Records"
        indexes = [
            models.Index(fields=["campaign", "dispatch_status"]),
        ]

    def __str__(self) -> str:
        return f"Outreach {self.campaign_id} → {self.customer_id}"
