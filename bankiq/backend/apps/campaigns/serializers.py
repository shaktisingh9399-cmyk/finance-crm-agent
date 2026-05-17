"""Campaign and outreach serializers."""

from rest_framework import serializers

from apps.campaigns.models import Campaign, CampaignStatus, OutreachRecord


class CampaignSerializer(serializers.ModelSerializer):
    """Campaign CRUD serializer."""

    class Meta:
        model = Campaign
        fields = (
            "id",
            "name",
            "description",
            "status",
            "query_text",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_status(self, value: str) -> str:
        if value not in CampaignStatus.values:
            raise serializers.ValidationError("Invalid campaign status.")
        return value


class OutreachRecordSerializer(serializers.ModelSerializer):
    """Outreach record serializer — customer ID only, no raw PII."""

    class Meta:
        model = OutreachRecord
        fields = (
            "id",
            "campaign",
            "customer",
            "conversion_score",
            "message_text",
            "dispatch_status",
            "rejection_reason",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
