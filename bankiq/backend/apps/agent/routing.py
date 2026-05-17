"""WebSocket URL routing for agent pipeline streaming."""

from django.urls import path

from apps.agent.consumers import AgentPipelineConsumer

websocket_urlpatterns = [
    path("ws/agent/<uuid:session_id>/", AgentPipelineConsumer.as_asgi()),
]
