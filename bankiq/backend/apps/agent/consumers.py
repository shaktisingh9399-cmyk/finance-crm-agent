"""WebSocket consumer for real-time agent pipeline stage updates."""

import logging
from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from agent_core.enums import ChannelEventField, ScopeKey

logger = logging.getLogger(__name__)


class AgentPipelineConsumer(AsyncJsonWebsocketConsumer):
    """
    Streams pipeline stage transitions to the authenticated RM.
    Group: agent_{session_id}
    """

    async def connect(self) -> None:
        self.session_id = self.scope[ScopeKey.URL_ROUTE.value][ScopeKey.KWARGS.value]["session_id"]
        self.group_name = f"agent_{self.session_id}"
        user = self.scope.get(ScopeKey.USER.value)

        if user is None or user.is_anonymous:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info("WebSocket connected session=%s user=%s", self.session_id, user.pk)

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info("WebSocket disconnected session=%s code=%s", self.session_id, close_code)

    async def pipeline_stage(self, event: dict[str, Any]) -> None:
        """Handler for group_send type 'pipeline.stage'."""
        await self.send_json(event[ChannelEventField.PAYLOAD.value])
