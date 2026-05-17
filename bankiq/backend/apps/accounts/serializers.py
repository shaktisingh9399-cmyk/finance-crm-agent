"""Serializers for Relationship Manager accounts."""

from rest_framework import serializers

from apps.accounts.models import RelationshipManager


class RelationshipManagerSerializer(serializers.ModelSerializer):
    """Public RM profile — no sensitive fields."""

    class Meta:
        model = RelationshipManager
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "employee_id",
            "branch_code",
        )
        read_only_fields = fields
