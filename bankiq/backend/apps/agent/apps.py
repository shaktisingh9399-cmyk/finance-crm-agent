"""App configuration for agent API and WebSocket consumers."""

from django.apps import AppConfig


class AgentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.agent"
    verbose_name = "Agent"
