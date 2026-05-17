"""Agent query REST endpoint — dispatches async pipeline via Celery."""

import logging

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from agent_core.enums import PipelineEventStatus
from apps.agent.serializers import AgentQuerySerializer
from tasks.agent_tasks import run_agent_pipeline

logger = logging.getLogger(__name__)


class AgentQueryViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/v1/agent/query/
    Accepts RM query, enqueues agent pipeline, returns session metadata.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AgentQuerySerializer

    @method_decorator(ratelimit(key="user", rate="30/m", method="POST", block=True))
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]
        query = serializer.validated_data["query"]
        rm_id = str(request.user.pk)

        run_agent_pipeline.delay(
            session_id=str(session_id),
            rm_id=rm_id,
            query=query,
        )

        logger.info(
            "Agent query enqueued session=%s rm=%s",
            session_id,
            rm_id,
        )

        return Response(
            {
                "session_id": str(session_id),
                "status": PipelineEventStatus.QUEUED.value,
                "websocket_url": f"/ws/agent/{session_id}/",
            },
            status=status.HTTP_202_ACCEPTED,
        )
