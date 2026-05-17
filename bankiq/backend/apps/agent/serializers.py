"""Serializers for agent query endpoint."""

from rest_framework import serializers


class AgentQuerySerializer(serializers.Serializer):
    """Inbound RM natural-language query."""

    query = serializers.CharField(max_length=4000)
    session_id = serializers.UUIDField()

    def validate_query(self, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Query cannot be empty.")
        return stripped
